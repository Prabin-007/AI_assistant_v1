import os
import numpy as np
import json

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
VECTOR_STORE_FILE = os.path.join(BASE_DIR, os.getenv("VECTOR_STORE_FILE"))

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

def add_embeddings(chunks):
    for chunk in chunks:
        chunk["vector"] = get_embedding(chunk["text"])
        
    return chunks

def chunk_document(document):
    chunks=[]
    for i,part in enumerate(document['text'].split("\n\n")):
        part=part.strip()
        if not part:
            continue
        
        chunks.append({
            "source": document["source"],
            "text": part,
            "chunk_id": i
        })
    return chunks

def create_chunks():
    documents=load_documents(KB_FOLDER)
    chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc)
        chunks.extend(doc_chunks)
    return chunks

def search(query,chunks,top_k=3):
    query_vector = get_embedding(query)
    #similiarity score store in results
    results = []
    
    for chunk in chunks:
        score = cosine_similarity(query_vector, chunk["vector"])
        results.append({
            "source": chunk["source"],
            "text": chunk["text"],
            "score": score,
            "chunk_id":chunk["chunk_id"],
            "size" : len(chunk["text"])
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:top_k]

def test(user_query,chunks,top_k=3):
    print("\nUser Query: ",user_query)

    results = search(user_query, chunks, top_k)
    
    for r in results:
        print(f"{r['score']:.2f} | {r['source']} | {r['size']} ")
        print(f"Chunk ID: {r['chunk_id']} | Text: {r['text']}...")  # Print the chunk text 
        
if os.path.exists(VECTOR_STORE_FILE):
    print(f"Loading chunks from {VECTOR_STORE_FILE}...")    
    with open(VECTOR_STORE_FILE, "r", encoding="utf-8") as f:
        chunks=json.loads(f.read())
else:
    print(f"Creating chunks from documents in {KB_FOLDER}...")
    chunks = create_chunks()
    chunks = add_embeddings(chunks)
    with open(VECTOR_STORE_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(chunks, ensure_ascii=False, indent=4))
        #ensure_ascii=False to preserve non-ASCII characters({"name": "प्रबिन"} stored as it is), indent=4 for pretty printing

# print(chunks[0]['text'])
print(f"Loaded {len(chunks)} chunks from {KB_FOLDER} and added embeddings.")

user_query ="how to get reimbursement for travel expenses and medical expenses"
test(user_query,chunks,top_k=3)
