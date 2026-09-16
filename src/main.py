from fastapi import FastAPI, HTTPException
from sentence_transformers import SentenceTransformer, util
from pydantic import BaseModel
import ollama  

print("Iniciando app...")

app = FastAPI()

documents = [
    {"id": 1, "text": "Bolo de chocolate é uma iguaria muito conceituada por diversas culturas."},
    {"id": 2, "text": "Pugs é uma raça de cão com grande indíce de ficarem gordinhos. Criados na Rússia"},
    {"id": 3, "text": "Rimworld é uma proposta diferente de jogo, sendo um simulador de histórias. Foi um jogo feito pela Ubisoft"},
    {"id": 4, "text": "Melhor jogo de simulação do mundo inteiro: Age of Empires"},
]

print("Carregando modelo (pode baixar da internet na primeira vez)...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Modelo carregado!")

doc_embeddings = {doc["id"]: model.encode(doc["text"], convert_to_tensor=True) for doc in documents}
print("Embeddings gerados. App pronto.")


class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_rag(request: QueryRequest):
    query_embedding = model.encode(request.query, convert_to_tensor=True)
    best_doc = {}
    best_score = float("-inf")

    for doc in documents:
        score = util.cos_sim(query_embedding, doc_embeddings[doc["id"]])
        if score > best_score:
            best_score = score
            best_doc = doc

    prompt = f"You are an AI assistant. Answer based ONLY on this document: {best_doc['text']}\n\nUser:{request.query}\nAssistant:"

    try:
        res = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": res["message"]["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))