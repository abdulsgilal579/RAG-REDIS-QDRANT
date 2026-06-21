import json
import uuid
import numpy as np
import redis
from sentence_transformers import SentenceTransformer
from src.config import REDIS_URL, EMBEDDING_MODEL

client = redis.from_url(REDIS_URL)
model = SentenceTransformer(EMBEDDING_MODEL)

SIMILARITY_THRESHOLD = 0.85
CACHE_KEY = "rag:semantic_cache"

def _embed(text: str) -> list:
    return model.encode(text.strip().lower()).tolist()

def _cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get(query: str):
    query_embedding = _embed(query)
    all_entries = client.hgetall(CACHE_KEY)

    best_score = 0
    best_answer = None

    for _, value in all_entries.items():
        entry = json.loads(value)
        score = _cosine_similarity(query_embedding, entry["embedding"])
        if score > best_score:
            best_score = score
            best_answer = entry["answer"]

    if best_score >= SIMILARITY_THRESHOLD:
        return best_answer
    return None

def set(query: str, answer: str):
    embedding = _embed(query)
    entry = json.dumps({"embedding": embedding, "answer": answer})
    client.hset(CACHE_KEY, str(uuid.uuid4()), entry)
