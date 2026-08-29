# from app.langgraph.router import QueryRouter

# router = QueryRouter()

# questions = [
#     "What airline is associated with AIR2504?",
#     "What aircraft is involved in AIR2602?",
#     "Which aircraft is associated with Alaska Airlines?",
#     "Which reports involve CRJ700?",
#     "What caused the aircraft to crash?",
#     "Compare the causes of AIR2504 and AIR2602.",
#     "What is the title of AIR2504?",
#     "Where did the collision happen?"
# ]

# for question in questions:
#     route = router.route(
#         question,
#         scope="Aviation Database"
#     )

#     print(f"{question}")
#     print(f"-> {route}\n")


# from app.retrieval.vector_store import VectorStore

# store = VectorStore()
# db = store.load_uploaded()

# query = "What was the probable cause of the AIR-24-07 air show collision?"

# print("\n--- MMR ---")

# mmr_docs = db.max_marginal_relevance_search(
#     query=query,
#     k=5,
#     fetch_k=40,
#     lambda_mult=0.85
# )

# for doc in mmr_docs:
#     print(
#         doc.metadata.get("source"),
#         "Page:",
#         doc.metadata.get("page")
#     )


# print("\n--- SIMILARITY SEARCH ---")

# similarity_docs = db.similarity_search(
#     query=query,
#     k=5
# )

# for doc in similarity_docs:
#     print(
#         doc.metadata.get("source"),
#         "Page:",
#         doc.metadata.get("page")
#     )

from app.retrieval.retrieval_service import RetrievalService

retriever = RetrievalService()

print("\n--- Uploaded Documents ---")
results = retriever.retrieve(
    query="What caused the accident?",
    scope="Uploaded Documents",
    k=5
)

print("Results:", len(results))

print("\n--- Both ---")
results = retriever.retrieve(
    query="What caused the accident?",
    scope="Both",
    k=5
)

print("Results:", len(results))