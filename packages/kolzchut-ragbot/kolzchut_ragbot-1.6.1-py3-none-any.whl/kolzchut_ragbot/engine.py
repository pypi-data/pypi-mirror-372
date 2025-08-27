import time
from collections import defaultdict
from datetime import datetime
from .llm_client import LLMClient
from . import config
from .model import es_client_factory
from .Document import factory
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from .get_full_documents_utilities import find_page_id_in_all_indices, unite_docs_to_single_instance
import torch
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
definitions = factory()


class Engine:
    """
    Engine class for handling document search and retrieval using Elasticsearch and LLMs.

    Attributes:
        llms_client (LLMClient): The LLM client instance.
        elastic_model (Model): The Elasticsearch model instance.
        models (dict): A dictionary of SentenceTransformer models.
        reranker_tokenizer (AutoTokenizer): The tokenizer for the reranker model.
        reranker_model (AutoModelForSequenceClassification): The reranker model.
        identifier_field (str): The identifier field for documents.

    Methods:
        rerank_with_me5(query, documents, k=5):
            Reranks documents based on the query using the reranker model.

        update_docs(list_of_docs, embed_only_fields=None, delete_existing=False):
            Updates or creates documents in the Elasticsearch index.

        reciprocal_rank_fusion(ranking_lists, k=60, weights=None):
            Performs Reciprocal Rank Fusion on a list of ranking lists.

        search_documents(query, top_k):
            Searches for documents based on the query and returns the top_k results.

        answer_query(query, top_k, model):
            Answers a query using the top_k documents and the specified model.
    """

    def __init__(self, llms_client: LLMClient, elastic_model=None, models=None, reranker_tokenizer=None,
                 reranker_model=None, es_client=None):
        """
        Initializes the Engine instance.

        Args:
            llms_client (LLMClient): The LLM client instance.
            elastic_model (Model, optional): The Elasticsearch model instance. Default is None.
            models (dict, optional): A dictionary of SentenceTransformer models. Default is None.
            reranker_tokenizer (AutoTokenizer, optional): The tokenizer for the reranker model. Default is None.
            reranker_model (AutoModelForSequenceClassification, optional): The reranker model. Default is None.
            es_client (optional): The Elasticsearch client instance. Default is None.
        """
        if elastic_model is None:
            self.elastic_model = es_client_factory(es_client)
        else:
            self.elastic_model = elastic_model

        self.llms_client = llms_client

        self.identifier_field = factory().identifier

        if models is None:
            self.models = {f"{model_name}": SentenceTransformer(config.MODELS_LOCATION + "/" + model_name).to(device)
                           for model_name in definitions.models.keys()}
        else:
            self.models = models
        for model in self.models.values():
            model.eval()

        if reranker_tokenizer is None:
            self.reranker_tokenizer = AutoTokenizer.from_pretrained(os.getenv("TOKENIZER_LOCATION"))
        else:
            self.reranker_tokenizer = reranker_tokenizer

        if reranker_model is None:
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained(os.getenv("TOKENIZER_LOCATION"))
        else:
            self.reranker_model = reranker_model
        self.reranker_model.eval()

    def change_llm(self, llms_client: LLMClient):
        """
        Changes the LLM client for the Engine instance.

        Args:
            llms_client (LLMClient): The new LLM client instance.
        """
        self.llms_client = llms_client

    def rerank_with_me5(self, query, documents, k=5):
        """
        Reranks documents based on the query using the reranker model.

        Args:
            query (str): The query string.
            documents (list): A list of documents to be reranked.
            k (int, optional): The number of top documents to return. Default is 5.

        Returns:
            list: A list of top k reranked documents.
        """
        pairs = [(query, doc) for doc in set(documents)]
        inputs = self.reranker_tokenizer(pairs, return_tensors='pt', padding=True, truncation=True, max_length=512)

        # Make predictions
        with torch.no_grad():
            outputs = self.reranker_model(**inputs)

        scores = outputs.logits.squeeze()

        if scores.ndim > 1:
            scores = scores[:, 1]  # Assuming binary classification and index 1 is the relevance score

        sorted_indices = torch.argsort(scores, descending=True)
        # If there is only one document, return it to avoid torch error
        if len(sorted_indices) == 1:
            return [pairs[0][1]]
        # Sort documents by their highest score
        sorted_docs = [pairs[i][1] for i in sorted_indices]
        return sorted_docs[:k]

    def update_docs(self, list_of_docs: list[dict], embed_only_fields=None, delete_existing=False):
        """
        Updates or creates documents in the Elasticsearch index.

        Args:
            list_of_docs (list[dict]): A list of dictionaries representing the documents to be indexed.
            embed_only_fields (list, optional): A list of fields to be embedded. Default is None.
            delete_existing (bool, optional): Whether to delete existing documents. Default is False.
        """
        embed_only_fields = embed_only_fields or definitions.models.values()
        for doc in list_of_docs:
            for semantic_model, field in definitions.models.items():
                if field in doc.keys() and field in embed_only_fields:
                    content_vectors = self.models[semantic_model].encode(doc[field])
                    doc[f'{field}_{semantic_model}_vectors'] = content_vectors

            doc['last_update'] = datetime.now()
        self.elastic_model.create_or_update_documents(list_of_docs, delete_existing)

    def reciprocal_rank_fusion(self, ranking_lists, k=60, weights=None):
        """
        Performs Reciprocal Rank Fusion on a list of ranking lists.

        Args:
        :param ranking_lists: List of ranking lists, where each ranking list is a list of documents returned by a model.
        :param k: The parameter for the reciprocal rank calculation (default is 60).
        :param: weights: Optional. Weights for each ranking list.

        Returns:
            list: A fused ranking list of documents.
        """
        scores = defaultdict(float)

        for list_index, rank_list in enumerate(ranking_lists):
            for rank, identifier in enumerate(rank_list):
                # Reciprocal rank score
                w = weights[list_index] if weights else 1
                scores[identifier] += w / (k + rank + 1)

        # Sort the documents by their cumulative scores in descending order
        fused_list = sorted(scores, key=scores.get, reverse=True)

        return fused_list

    def search_documents(self, query: str, top_k: int):
        """
        Searches for documents based on the query and returns the top_k results.

        Args:
            query (str): The query string.
            top_k (int): The number of top documents to return.

        Returns:
            list: A list of top k documents.
        """
        query_embeddings = {f"{semantic_model}": self.models[semantic_model].encode(query) for semantic_model in
                            definitions.models.keys()}
        all_docs_by_model = self.elastic_model.search(query_embeddings)
        all_docs = []
        ids_for_fusion = []
        all_docs_and_scores = {}

        for key, values in all_docs_by_model.items():
            print(f"\nFound {len(values)} documents for model\n")
            model_ids = []
            scores_for_model = []

            for doc in values:
                model_ids.append(doc["_source"]["page_id"])
                all_docs.append(doc)
                scores_for_model.append({"doc": doc["_source"]["title"], "score": doc["_score"]})
            ids_for_fusion.append(model_ids)
            all_docs_and_scores[f'{key}'] = scores_for_model
        print(f"\nFusing {len(ids_for_fusion)} results\n")
        fused_ids = self.reciprocal_rank_fusion(ids_for_fusion, k=top_k)
        top_k_documents = []
        top_titles = []

        for fused_id in fused_ids:
            for doc in all_docs:
                if doc["_source"]["page_id"] == fused_id and doc["_source"]["title"] not in top_titles:
                    top_k_documents.append(doc["_source"])
                    top_titles.append(doc["_source"]["title"])
                    break
            if len(top_titles) >= top_k:
                break

        return top_k_documents, all_docs_and_scores

    def answer_query(self, query, top_k: int, model, additional_document: dict = None, send_complete_pages_to_llm: bool = False):
        """
        Answers a query using the top_k documents and the specified model.

        Args:
            query (str): The query string.
            top_k (int): The number of top documents to use for answering the query.
            model: The model to use for answering the query.
            additional_document (dict, optional): An additional document to include in the search. Default is None.
            send_complete_pages_to_llm (bool, optional): Whether to send complete pages to the

        Returns:
            tuple: A tuple containing the top k documents, the answer, and the stats.
        """
        before_retrieval = time.perf_counter()
        top_k_documents, all_docs_and_scores = self.search_documents(query, top_k)

        if send_complete_pages_to_llm:
            top_k_documents = [self.transform_document_to_full_page(doc) for doc in top_k_documents]

        if additional_document:
            top_k_documents.append(additional_document)

        retrieval_time = round(time.perf_counter() - before_retrieval, 4)
        print(f"retrieval time: {retrieval_time}")

        gpt_answer, gpt_elapsed, tokens, request_params = self.llms_client.answer(query, top_k_documents)
        stats = {
            "retrieval_time": retrieval_time,
            "gpt_model": model,
            "gpt_time": gpt_elapsed,
            "tokens": tokens
        }
        return top_k_documents, gpt_answer, stats, all_docs_and_scores, request_params

    def transform_document_to_full_page(self, document: dict) -> dict:
        """
        Adds the full page content to the document by retrieving it from Elasticsearch.

        Args:
            document (dict): The document to which the full page content will be added.

        Returns:
            dict: The updated document with the full page content added.
        """
        if not document.get("page_id"):
            return document
        full_document = self.get_full_document_by_page_id(document["page_id"])
        if full_document and full_document.get("content"):
            document["content"] = full_document["content"]
        return document

    def get_full_document_by_page_id(self, page_id: int) -> dict | None:
        """
        Retrieves a unified document instance for a given page_id by searching all indices in Elasticsearch.

        Args:
            page_id (int): The page ID to search for.

        Returns:
            dict | None: A single dict representing the united document (with metadata and concatenated content),
                        or None if no documents are found.
        """
        es_client = self.elastic_model.es_client
        indices = es_client.indices.get_alias(index="*").keys()
        parts_of_documents = find_page_id_in_all_indices(page_id=page_id, es_client=es_client, indices=indices)
        if not parts_of_documents:
            return None
        full_document = unite_docs_to_single_instance(parts_of_documents)
        return full_document


engine = None


def engine_factory(llms_client: LLMClient, es_client=None):
    global engine
    if engine is None:
        engine = Engine(llms_client=llms_client, es_client=es_client)
    return engine
