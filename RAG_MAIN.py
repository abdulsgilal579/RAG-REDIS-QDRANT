import fitz  # pymupdf
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from groq_client import search_and_answer

# --- Config ---
PDF_PATH = "Abdul Samad Gilal Resume.pdf"
COLLECTION_NAME = "pdf_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # fast, lightweight, 384 dims

# --- Setup ---
client = QdrantClient(url="http://localhost:6333")
 # swap to localhost:6333 for Docker
model = SentenceTransformer(EMBEDDING_MODEL)

# --- Step 1: Extract text from PDF ---
def extract_chunks(pdf_path, chunk_size=500):
    doc = fitz.open(pdf_path)
    chunks = []
    for page in doc:
        text = page.get_text()
        # split into chunks of ~chunk_size characters
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size].strip()
            if chunk:
                chunks.append(chunk)
    return chunks

# --- Step 2: Create collection (only if it doesn't exist) ---
def setup_collection():
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        chunks = extract_chunks(PDF_PATH)
        store_chunks(chunks)
        print(f"Collection '{COLLECTION_NAME}' created and indexed.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists. Skipping indexing.")

# --- Step 3: Embed and store ---
def store_chunks(chunks):
    embeddings = model.encode(chunks)
    points = [
        PointStruct(id=i, vector=embedding.tolist(), payload={"text": chunk})
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} chunks.")

# --- Step 4: Query ---
def search(query, top_k=3):
    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points
    return [r.payload['text'] for r in results]

# --- Run ---
if __name__ == "__main__":
    setup_collection()

    print("\nAsk anything about the document. Type 'exit' to quit.\n")
    while True:
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() == "exit":
            print("Goodbye!")
            break
        retrieved_chunks = search(query)
        answer = search_and_answer(retrieved_chunks, query)
        print(f"\nAssistant: {answer}\n")
