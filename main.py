from src.config import PDF_PATH
from src.vectorstore.qdrant import setup_collection, search
from src.llm.groq import search_and_answer
from src.cache import redis as cache

if __name__ == "__main__":
    setup_collection(PDF_PATH)

    print("\nAsk anything about the document. Type 'exit' to quit.\n")
    while True:
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() == "exit":
            print("Goodbye!")
            break

        cached = cache.get(query)
        if cached:
            print("[CACHE HIT] Returning cached answer...")
            print(f"\nAssistant: {cached}\n")
            continue

        print("[CACHE MISS] Calling API...")
        retrieved_chunks = search(query)
        answer = search_and_answer(retrieved_chunks, query)
        cache.set(query, answer)
        print(f"\nAssistant: {answer}\n")
