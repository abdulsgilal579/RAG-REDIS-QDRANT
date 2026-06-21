from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from src.config import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_URL, QDRANT_API_KEY
from src.ingestion.pdf_loader import extract_chunks

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer(EMBEDDING_MODEL)


def setup_collection(pdf_path):
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        chunks = extract_chunks(pdf_path)
        store_chunks(chunks)
        print(f"Collection '{COLLECTION_NAME}' created and indexed.")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists. Skipping indexing.")


def store_chunks(chunks):
    embeddings = model.encode(chunks)
    points = [
        PointStruct(id=i, vector=embedding.tolist(), payload={"text": chunk})
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Stored {len(points)} chunks.")


def search(query, top_k=3):
    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k
    ).points
    return [r.payload["text"] for r in results]
