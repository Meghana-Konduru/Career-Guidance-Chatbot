from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import faiss
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import uvicorn
import requests
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CareerChatbot:
    def __init__(self, embeddings_dir="embeddings"):
        self.embeddings_dir = embeddings_dir
        self.load_embeddings()
        
    def load_embeddings(self):
        print("Loading career guidance embeddings...")
        try:
            self.index = faiss.read_index(os.path.join(self.embeddings_dir, "career_index.faiss"))
            with open(os.path.join(self.embeddings_dir, "metadata.pkl"), 'rb') as f:
                self.metadata = pickle.load(f)
            with open(os.path.join(self.embeddings_dir, "documents.pkl"), 'rb') as f:
                self.documents = pickle.load(f)
            with open(os.path.join(self.embeddings_dir, "vectorizer.pkl"), 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open(os.path.join(self.embeddings_dir, "svd.pkl"), 'rb') as f:
                self.svd = pickle.load(f)
            print(f"Loaded {len(self.documents)} documents")
        except Exception as e:
            print(f"Error: {e}")
            raise e
    
    def search_similar(self, query, k=3):
        query_tfidf = self.vectorizer.transform([query])
        query_embedding = self.svd.transform(query_tfidf).astype('float32')
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        distances, indices = self.index.search(query_embedding, k)
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx]
                })
        return results

    def generate_response_with_ollama(self, query):
        # Get relevant documents
        similar_docs = self.search_similar(query, k=3)
        
        if not similar_docs:
            context = "No specific documents found."
        else:
            context_parts = []
            for doc in similar_docs:
                content = doc['content'][:500]  # Limit each doc
                context_parts.append(content)
            context = "\n\n".join(context_parts)
        
        # Create prompt for Ollama
        prompt = f"""You are a helpful career guidance assistant. Use the following context to answer the user's question. 
If the context doesn't contain relevant information, provide general career advice based on your knowledge.
Be conversational, helpful, and provide actionable advice.

Context from career guidance documents:
{context}

User Question: {query}

Answer (be specific, helpful, and conversational):"""

        try:
            # Call Ollama API
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama3.2:1b',
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response'].strip()
            else:
                return "I'm having trouble generating a response right now. Please try again."
                
        except Exception as e:
            print(f"Ollama error: {e}")
            return "I'm having trouble connecting to the language model. Please make sure Ollama is running."
    
    def generate_response(self, query):
        return self.generate_response_with_ollama(query)


print("Starting Career Guidance Chatbot...")
try:
    chatbot = CareerChatbot("embeddings")
    chatbot_initialized = True
    print("Chatbot ready!")
except Exception as e:
    print(f"Failed: {e}")
    chatbot_initialized = False
    chatbot = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool

@app.get("/")
async def root():
    return {"message": "Career Chatbot API Running"}

@app.get("/health")
async def health_check():
    return {"status": "ready" if chatbot_initialized else "error"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not chatbot_initialized:
        raise HTTPException(status_code=503, detail="System not ready")
    try:
        response = chatbot.generate_response(request.message)
        return ChatResponse(response=response, success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)