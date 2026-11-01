import os
import numpy as np

from openai import OpenAI
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)  # Load environment variables from .env file

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


EMBED_MODEL = os.getenv("EMBED_MODEL")
KB_FOLDER = os.path.join(BASE_DIR, os.getenv("KB_FOLDER"))

def get_embedding(text):
    response = client.embeddings.create(
        model=os.getenv("EMBED_MODEL"),
        input=[text]
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def load_documents(folder=KB_FOLDER):
    documents = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        
        with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
            documents.append(
                {
                    "source": filename,
                    "text":f.read(),
                }
            )
    return documents

def add_embeddings(documents):
    for doc in documents:
        doc["vector"] = get_embedding(doc["text"])
        
    return documents

def search(query,documents,top_k=3):
    query_vector = get_embedding(query)
    #similiarity score store in results
    results = []
    
    for doc in documents:
        score = cosine_similarity(query_vector, doc["vector"])
        results.append({
            "source": doc["source"],
            "text": doc["text"],
            "score": score,
            "size" : len(doc["text"])
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:top_k]

def test(user_query,documents,top_k=3):
    print("\nUser Query: ",user_query)

    results = search(user_query, documents, top_k)
    
    for r in results:
        print(f"{r['score']:.2f} | {r['source']} | {r['size']} ")
    
documents = load_documents(KB_FOLDER)
documents = add_embeddings(documents)

print(documents[0])
# print(f"Loaded {len(documents)} documents from {KB_FOLDER} and added embeddings.")

# user_query ="how to get reimbursement for travel expenses"
# test(user_query,documents,top_k=3)
