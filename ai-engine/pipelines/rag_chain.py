from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import faiss
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

app = FastAPI(
    title="Career Guidance Chatbot API",
    description="AI-powered career guidance and counseling",
    version="1.0.0"
)

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CareerRAGSystem:
    def __init__(self, embeddings_dir="pipelines/embeddings"):
        self.embeddings_dir = embeddings_dir
        self.load_embeddings()
        
    def load_embeddings(self):
        """Load embeddings and FAISS index"""
        print("🧠 Loading career guidance embeddings...")
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(os.path.join(self.embeddings_dir, "career_index.faiss"))
            
            # Load metadata and documents
            with open(os.path.join(self.embeddings_dir, "metadata.pkl"), 'rb') as f:
                self.metadata = pickle.load(f)
            
            with open(os.path.join(self.embeddings_dir, "documents.pkl"), 'rb') as f:
                self.documents = pickle.load(f)
            
            # Load vectorizer and SVD
            with open(os.path.join(self.embeddings_dir, "vectorizer.pkl"), 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(os.path.join(self.embeddings_dir, "svd.pkl"), 'rb') as f:
                self.svd = pickle.load(f)
            
            print(f"✅ RAG Ready with {len(self.documents)} document chunks")
            
        except Exception as e:
            print(f"❌ Error loading embeddings: {e}")
            raise e
    
    def search_similar(self, question, k=4):
        """Search for similar career guidance content"""
        # Transform query using the same vectorizer and SVD
        query_tfidf = self.vectorizer.transform([question])
        query_embedding = self.svd.transform(query_tfidf).astype('float32')
        
        # Manual normalization for query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        scores, indices = self.index.search(query_embedding, k)
        
        retrieved_docs = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                retrieved_docs.append({
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'score': float(score)
                })
        
        return retrieved_docs

    def generate_response(self, question):
        """Generate response from retrieved documents"""
        retrieved_docs = self.search_similar(question, k=4)
        
        if not retrieved_docs:
            return "I don't have specific information about that topic. Could you try asking about career paths, skills development, or job search strategies?"
        
        # Build response from similar documents
        response_parts = []
        response_parts.append("Based on your question, here's some relevant career guidance:\n")
        
        for i, doc in enumerate(retrieved_docs[:3]):
            source = doc['metadata']['doc_name']
            content = doc['content']
            
            # Truncate very long content
            if len(content) > 300:
                content = content[:300] + "..."
                
            response_parts.append(f"**From {source}:** {content}")
        
        response_parts.append("\nIs there anything specific about this you'd like me to elaborate on?")
        
        return "\n\n".join(response_parts)

# Initialize RAG system
print("🚀 Initializing Career Guidance RAG System...")
try:
    rag_system = CareerRAGSystem("pipelines/embeddings")
    print("✅ RAG system initialized successfully!")
except Exception as e:
    print(f"❌ Failed to initialize RAG system: {e}")
    rag_system = None

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    success: bool

# API endpoints
@app.get("/")
async def root():
    return {
        "message": "Career Guidance Chatbot API is running!",
        "status": "healthy",
        "rag_initialized": rag_system is not None
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy" if rag_system is not None else "initializing",
        "rag_initialized": rag_system is not None,
        "service": "career-guidance-chatbot"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if rag_system is None:
        raise HTTPException(
            status_code=503, 
            detail="Career guidance system is not initialized. Please check if embeddings are built."
        )
    
    try:
        print(f"📨 Received message: {request.message}")
        
        # Get response from RAG system
        response = rag_system.generate_response(request.message)
        
        return ChatResponse(
            response=response,
            success=True
        )
        
    except Exception as e:
        print(f"❌ Error processing chat request: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing your request: {str(e)}"
        )

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify RAG system is working"""
    if rag_system is None:
        return {"status": "error", "message": "RAG system not initialized"}
    
    try:
        test_question = "What skills do I need for web development?"
        response = rag_system.generate_response(test_question)
        
        return {
            "status": "success",
            "test_question": test_question,
            "response": response,
            "rag_working": True
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"RAG test failed: {str(e)}",
            "rag_working": False
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🌟 Starting Career Guidance Chatbot Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("🧪 Test endpoint: http://localhost:8000/test")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )