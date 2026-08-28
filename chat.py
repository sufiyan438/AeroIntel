import os

from app.rag.rag_engine import RAGEngine

def print_banner():
    print("=" * 60)
    print("                 AeroIntel AI")
    print("      Aviation Knowledge Intelligence System")
    print("=" * 60)

def print_sources(results):
    print("\nSources")
    print("-" * 60)

    seen = set()
    for doc, score in results:
        source = os.path.basename(
            doc.metadata.get("source", "Unknown")
        )
        page = doc.metadata.get("page", 0) + 1

        key = (source, page)
        if key not in seen:
            seen.add(key)
            if source is None:
                print(f"• {source} (Page {page}) | Retrieval: MMR")
            else:
                print(f"• {source} (Page {page}) | Similarity Score: {score:.4f}")


def main():
    rag = RAGEngine()
    print_banner()

    while True:
        question = input("\nAsk a question (type 'exit' to quit):\n>")
        if question.lower() in ["exit", "quit"]:
            print("\nExiting...\n")
            break

        try:
            print("\nSearching documents...\n")
            answer, results = rag.ask(question)

            print("\n" + "=" * 60)
            print("Answer")
            print("=" * 60)

            print(answer)
            print_sources(results)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break

        except Exception as e:
            print("\nError:")
            print("-" * 60)
            print(e)
            print("\n" * 60)


if __name__ == "__main__":
    main()