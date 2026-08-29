import os

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

#     def retrieve(self, query, scope="Aviation Database", k=TOP_K):
#         print("\nSearching vector database...")

#         if scope == "Uploaded Documents":
#             docs = self.upload_db.max_marginal_relevance_search(query=query, 
#                                                                 k=k, fetch_k=20, 
#                                                                 lambda_mult=0.7)
#             print(f"\nRetrieved {len(docs)} uploaded chunks.")
#             return [(doc, None) for doc in docs]


#         #Aviation Database
#         best_match = self.metadata_service.get_best_match(query)
#         expanded_query = query

#         if best_match:
#             print("\nMetadata Filter Applied:")
#             print(f"• {best_match['report_id']}")

#             expanded_query = f"""
# Title:
# {best_match['title']}

# Airline:
# {best_match['airline']}

# Aircraft:
# {best_match['aircraft']}

# Keywords:
# {' '.join(best_match['keywords'])}

# Question:
# {query}
# """

#         docs = self.aviation_db.max_marginal_relevance_search(query=expanded_query,
#                                                               k=k, fetch_k=20,
#                                                               lambda_mult=0.7)
#         filtered_docs = docs

#         #if specific report found, then discard filtered_docs
#         if best_match:
#             filtered_docs = []

#             for doc in docs:
#                 filename = os.path.basename(doc.metadata.get("source", ""))

#                 if filename == best_match["pdf"]:
#                     filtered_docs.append(doc)

#         if scope == "Both":
#             upload_docs = self.upload_db.max_marginal_relevance_search(query=query,
#                                                                        k=k, fetch_k=20,
#                                                                        lambda_mult=0.7)
#             filtered_docs.extend(upload_docs)

#         print(f"\nRetrieved {len(filtered_docs)} chunks.")

#         return [(doc, None) for doc in filtered_docs[:k]]   

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
        # Aviation Database
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

        aviation_docs = self.aviation_db.max_marginal_relevance_search(
            query=expanded_query,
            k=aviation_k,
            fetch_k=FETCH_K,
            lambda_mult=MMR_LAMBDA
        )

        # -------------------------------------------------
        # Filter Aviation Results
        # -------------------------------------------------

        filtered_aviation_docs = aviation_docs

        if best_match:

            filtered_aviation_docs = []

            for doc in aviation_docs:

                filename = os.path.basename(
                    doc.metadata.get("source", "")
                )

                if filename == best_match["pdf"]:
                    filtered_aviation_docs.append(doc)

        # -------------------------------------------------
        # Aviation Database Only
        # -------------------------------------------------

        if scope == "Aviation Database":

            print(
                f"\nRetrieved {len(filtered_aviation_docs)} aviation chunks."
            )

            return [
                (doc, None)
                for doc in filtered_aviation_docs[:k]
            ]

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