import fitz
import os
from openai import OpenAI
import json
import numpy as np

def extract_pdf(pdf_path):
    my_file = fitz.open(pdf_path)
    all_text = ""

    for page_num in range(my_file.page_count):
        page = my_file[page_num]
        textes = page.get_text("text")
        all_text += textes

    return all_text

def create_chunks(text, n, overlap):
    chunk = []
    for i in range(0, len(text), n - overlap):
        texted = text[i:i+n]
        chunk.append(texted)
    return chunk

print(create_chunks(extract_pdf("namer.pdf"), 40, 10))

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    base_url = "YOUR_URL"
)

def create_embeddings(text, model = "BAAI/bge-en-icl"):
    response = client.embeddings.create(
        model = model,
        input = text
    )
    return response

def cosine_similarity(vec1, vec2):
    result = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    return result

def semantic_search(query, text_chunks, embeddings, k = 5):
    embedded_query = create_embeddings(query).data[0].embedding
    semantic_search = []

    for i, chunk in enumerate(embeddings):
        similarity = cosine_similarity(np.array(embedded_query), np.array(chunk))
        semantic_search.append(i, similarity)

    semantic_search = semantic_search.sort(key = lambda x: x[1], reverse = True)
    top_indexes = [index for index, _ in semantic_search]
    itog = [text_chunks[index] for index in top_indexes]
    return itog