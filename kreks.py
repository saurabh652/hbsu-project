# ================================
# SMART DOCUMENT Q&A SYSTEM (RAG)
# ================================

# Import libraries
import kreta
import scikitlearn
import os
import faiss
import pickle
import numpy as np
from typing import List

# PDF reading
from PyPDF2 import PdfReader

# Embedding model
from sentence_transformers import SentenceTransformer

# LLM (you can replace with OpenAI/Gemini)
from transformers import pipeline

# -------------------------------
# STEP 1: LOAD PDF DATA
# -------------------------------

def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    return text


# -------------------------------
# STEP 2: TEXT CHUNKING
# -------------------------------

def chunk_text(text: str, chunk_size=500, overlap=100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -------------------------------
# STEP 3: EMBEDDING GENERATION
# -------------------------------

def create_embeddings(chunks: List[str]):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    return embeddings, model


# -------------------------------
# STEP 4: STORE IN FAISS
# -------------------------------

def store_faiss(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


# -------------------------------
# STEP 5: SAVE INDEX
# -------------------------------

def save_index(index, chunks):
    faiss.write_index(index, "faiss_index.bin")

    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)


# -------------------------------
# STEP 6: LOAD INDEX
# -------------------------------

def load_index():
    index = faiss.read_index("faiss_index.bin")

    with open("chunks.pkl", "rb") as f:
        chunks = pickle.load(f)

    return index, chunks


# -------------------------------
# STEP 7: SEARCH SIMILAR CHUNKS
# -------------------------------

def search(query, index, model, chunks, top_k=3):
    query_embedding = model.encode([query])

    distances, indices = index.search(query_embedding, top_k)

    results = [chunks[i] for i in indices[0]]

    return results


# -------------------------------
# STEP 8: GENERATE ANSWER USING LLM
# -------------------------------

def generate_answer(context, question):
    generator = pipeline("text-generation", model="gpt2")

    prompt = f"""
    Context:
    {context}

    Question:
    {question}

    Answer:
    """

    result = generator(prompt, max_length=300, num_return_sequences=1)

    return result[0]["generated_text"]


# -------------------------------
# STEP 9: MAIN FUNCTION
# -------------------------------

def build_pipeline(pdf_path):
    print("Loading PDF...")
    text = load_pdf(pdf_path)

    print("Chunking text...")
    chunks = chunk_text(text)

    print("Creating embeddings...")
    embeddings, model = create_embeddings(chunks)

    print("Storing in FAISS...")
    index = store_faiss(embeddings)

    print("Saving index...")
    save_index(index, chunks)

    return model


def chat():
    print("Loading FAISS index...")
    index, chunks = load_index()

    model = SentenceTransformer("all-MiniLM-L6-v2")

    while True:
        query = input("\nAsk your question (type 'exit' to quit): ")

        if query.lower() == "exit":
            break

        results = search(query, index, model, chunks)

        context = " ".join(results)

        answer = generate_answer(context, query)

        print("\nAnswer:\n", answer)


# -------------------------------
# ENTRY POINT
# -------------------------------

if __name__ == "__main__":

    print("1. Build Knowledge Base")
    print("2. Start Chat")

    choice = input("Enter choice: ")

    if choice == "1":
        pdf_path = input("Enter PDF path: ")
        build_pipeline(pdf_path)

    elif choice == "2":
        chat()

    else:
        print("Invalid choice")