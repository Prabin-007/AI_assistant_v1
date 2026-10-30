from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

response = client.embeddings.create(
    model="nomic-embed-text",
    input=["dsh dhs hdhhh dada nani","python is a great programming language"]
)

# print(len(response.data[0].embedding))
# print(len(response.data[1].embedding))
vec1=response.data[0].embedding
vec2=response.data[1].embedding

print(np.dot(vec1,vec2))