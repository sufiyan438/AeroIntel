import os

from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi

from app.retrieval.vector_store import VectorStore
from app.retrieval.metadata_service import MetadataService
from app.config.settings import TOP_K, FETCH_K, MMR_LAMBDA

class RetrievalService:
    """
    Retrieval Modes

    • Aviation Database
    • Uploaded Documents
    • Both

    Retrieval Pipeline

    1. Metadata Matching
    2. Query Expansion
    3. MMR Retrieval
    4. Metadata Filtering
    """

    def __init__(self):
        self.vector_store = VectorStore()
        self.aviation_db = self.vector_store.load_aviation()
        self.upload_db = self.vector_store.load_uploaded()
        self.metadata_service = MetadataService()
        self.reranker = CrossEncoder("BAAI/bge-reranker-base")

        self.bm25_docs = []
        self.bm25 = None

        if self.aviation_db is not None:
            self.bm25_docs = list(
                self.aviation_db.docstore._dict.values()
            )

            tokenized_corpus = [
                doc.page_content.lower().split()
                for doc in self.bm25_docs
            ]

            self.bm25 = BM25Okapi(tokenized_corpus)


    def rerank(self, query, docs, top_k):
        if not docs:
            return []

        pairs = [
            [query, doc.page_content]
            for doc in docs
        ]

        scores = self.reranker.predict(pairs)

        ranked = sorted(
            zip(docs, scores),
            key=lambda item: item[1],
            reverse=True
        )

        return ranked[:top_k]




    def retrieve(self, query, scope="Aviation Database", k=TOP_K):

        print("\nSearching vector database...")

        # -------------------------------------------------
        # Uploaded Documents Only
        # -------------------------------------------------

        if scope == "Uploaded Documents":

            if self.upload_db is None:
                print("\nNo uploaded documents indexed.")
                return []

            docs = self.upload_db.max_marginal_relevance_search(
                query=query,
                k=k,
                fetch_k=FETCH_K,
                lambda_mult=MMR_LAMBDA
            )

            print(f"\nRetrieved {len(docs)} uploaded chunks.")

            return [(doc, None) for doc in docs]

        # -------------------------------------------------
        # Decide retrieval size
        # -------------------------------------------------

        if scope == "Both":

            aviation_k = (k + 1) // 2
            upload_k = k // 2

        else:

            aviation_k = k
            upload_k = 0

        # -------------------------------------------------
        # Aviation Database = Metadata + vector MMR
        # -------------------------------------------------

        best_match = self.metadata_service.get_best_match(query)

        expanded_query = query

        if best_match:

            print("\nMetadata Filter Applied:")
            print(f"• {best_match['report_id']}")

            expanded_query = f"""
Title:
{best_match['title']}

Airline:
{best_match['airline']}

Aircraft:
{best_match['aircraft']}

Keywords:
{' '.join(best_match['keywords'])}

Question:
{query}
"""

        # -------------------------------------------------
        # Retrieve larger candidate pool
        # -------------------------------------------------

        # candidate_docs = self.aviation_db.max_marginal_relevance_search(
        #     query=expanded_query,
        #     k=FETCH_K,
        #     fetch_k=FETCH_K * 2,
        #     lambda_mult=MMR_LAMBDA
        # )


        # -------------------------------------------------
        # Dense retrieval using FAISS + MMR
        # -------------------------------------------------

        dense_docs = self.aviation_db.max_marginal_relevance_search(
            query=expanded_query,
            k=FETCH_K,
            fetch_k=FETCH_K * 2,
            lambda_mult=MMR_LAMBDA
        )

        # -------------------------------------------------
        # Sparse retrieval using BM25
        # -------------------------------------------------

        bm25_docs = self.bm25_search(
            query=query,
            k=FETCH_K
        )

        print(
            f"\nHybrid candidates: "
            f"{len(dense_docs)} dense/MMR + "
            f"{len(bm25_docs)} BM25"
        )

        # -------------------------------------------------
        # Merge and deduplicate hybrid candidates
        # -------------------------------------------------

        candidate_docs = []

        seen = set()

        for doc in dense_docs + bm25_docs:

            key = (
                doc.metadata.get("source"),
                doc.metadata.get("page"),
                doc.page_content
            )

            if key not in seen:
                seen.add(key)
                candidate_docs.append(doc)


        print(
            f"Hybrid candidates after deduplication: "
            f"{len(candidate_docs)}"
        )




        # -------------------------------------------------
        # Filter to matched aviation report
        # -------------------------------------------------

        if best_match:

            candidate_docs = [
                doc
                for doc in candidate_docs
                if os.path.basename(
                    doc.metadata.get("source", "")
                ) == best_match["pdf"]
            ]

        # -------------------------------------------------
        # Rerank investigation-oriented queries
        # -------------------------------------------------

        reranked_docs = self.rerank(
            query=query,
            docs=candidate_docs,
            top_k=aviation_k
        )

        filtered_aviation_docs = [
            doc
            for doc, score in reranked_docs
        ]






        # -------------------------------------------------
        # Aviation Database Only
        # -------------------------------------------------

        if scope == "Aviation Database":

            print(
                f"\nRetrieved {len(filtered_aviation_docs)} aviation chunks."
            )

            # return [
            #     (doc, None)
            #     for doc in filtered_aviation_docs[:k]
            # ]

            return reranked_docs[:k]

        # -------------------------------------------------
        # Both
        # -------------------------------------------------

        if self.upload_db is not None:
            upload_docs = self.upload_db.max_marginal_relevance_search(
                query=query,
                k=upload_k,
                fetch_k=FETCH_K,
                lambda_mult=MMR_LAMBDA
            )
        else:
            upload_docs = []

        # upload_docs = self.upload_db.max_marginal_relevance_search(
        #     query=query,
        #     k=upload_k,
        #     fetch_k=FETCH_K,
        #     lambda_mult=MMR_LAMBDA
        # )

        combined_docs = (
            filtered_aviation_docs
            +
            upload_docs
        )

        print(
            f"\nRetrieved "
            f"{len(filtered_aviation_docs)} aviation chunks "
            f"and {len(upload_docs)} uploaded chunks."
        )

        return [
            (doc, None)
            for doc in combined_docs[:k]
        ]



    def _rerank_investigation_chunks(self, docs, query):
        query_lower = query.lower()

        investigation_terms = [
            "finding",
            "findings",
            "probable cause",
            "safety issue",
            "safety issues",
            "recommendation",
            "recommendations",
            "conclusion",
            "conclusions",
            "limitations",
            "shortcomings",
            "contributing",
            "contributed",
        ]

        wants_investigation_findings = any(
            term in query_lower
            for term in [
                "finding",
                "findings",
                "probable cause",
                "safety issue",
                "recommendation",
                "conclusion",
            ]
        )

        if not wants_investigation_findings:
            return docs

        def score(doc):
            text = doc.page_content.lower()

            return sum(
                text.count(term)
                for term in investigation_terms
            )

        return sorted(
            docs,
            key=score,
            reverse=True
        )





    def bm25_search(self, query, k=FETCH_K):
        if self.bm25 is None:
            return []

        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        return [
            self.bm25_docs[i]
            for i in ranked_indices[:k]
            if scores[i] > 0
        ]