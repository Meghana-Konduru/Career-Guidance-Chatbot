import os
import json
import numpy as np
import faiss
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import re
import glob

class CareerDocumentEmbedder:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=512, stop_words='english')
        self.documents = []
        self.metadata = []
        
    def find_career_files(self):
        """Find all text files in current directory and subdirectories"""
        txt_files = []
        
        # Look in current directory
        txt_files.extend(glob.glob('*.txt'))
        txt_files.extend(glob.glob('*.txt.txt'))  # For double extension files
        
        # Look in subdirectories
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.txt'):
                    full_path = os.path.join(root, file)
                    txt_files.append(full_path)
        
        # Remove duplicates and sort
        return sorted(list(set(txt_files)))
    
    def load_documents_from_files(self, file_paths):
        """Load and process documents from text files"""
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    
                # Extract filename without extension for metadata
                filename = os.path.basename(file_path)
                doc_name = os.path.splitext(filename)[0]
                # Handle double extensions
                if doc_name.endswith('.txt'):
                    doc_name = os.path.splitext(doc_name)[0]
                
                # Split content into chunks (sentences or paragraphs)
                chunks = self._split_into_chunks(content)
                
                for i, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 50:  # Only include meaningful chunks
                        self.documents.append(chunk)
                        self.metadata.append({
                            'file': filename,
                            'doc_name': doc_name,
                            'chunk_id': i,
                            'content_preview': chunk[:100] + '...' if len(chunk) > 100 else chunk
                        })
                        
                print(f"Loaded {len(chunks)} chunks from {filename}")
                
            except Exception as e:
                print(f"Error loading {file_path}: {str(e)}")
    
    def _split_into_chunks(self, text, max_length=512):
        """Split text into manageable chunks for embedding"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If paragraph is too long, split by sentences
            if len(paragraph) > max_length:
                sentences = re.split(r'[.!?]+', paragraph)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    if len(current_chunk) + len(sentence) < max_length:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks.append(paragraph)
        
        return chunks
    
    def generate_embeddings(self):
        """Generate TF-IDF embeddings and reduce dimensionality"""
        print("Generating TF-IDF embeddings...")
        
        # Create TF-IDF vectors
        tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
        
        # Reduce dimensionality for better similarity search
        n_components = min(128, tfidf_matrix.shape[1])
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        self.embeddings = svd.fit_transform(tfidf_matrix)
        
        # Convert to float32 for FAISS compatibility
        self.embeddings = self.embeddings.astype('float32')
        
        print(f"Reduced embeddings shape: {self.embeddings.shape}")
        self.svd = svd
    
    def build_faiss_index(self):
        """Build FAISS index for efficient similarity search"""
        dimension = self.embeddings.shape[1]
        
        # Create index with correct dimensions
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        # Use manual normalization to avoid FAISS wrapper issues
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # Avoid division by zero
        normalized_embeddings = self.embeddings / norms
        
        # Add to index
        self.index.add(normalized_embeddings)
        
        print(f"FAISS index built with {self.index.ntotal} vectors")
        self.normalized_embeddings = normalized_embeddings
    
    def save_embeddings(self, output_dir="embeddings"):
        """Save embeddings, index, and metadata"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Save FAISS index
        faiss.write_index(self.index, os.path.join(output_dir, "career_index.faiss"))
        
        # Save metadata
        with open(os.path.join(output_dir, "metadata.pkl"), 'wb') as f:
            pickle.dump(self.metadata, f)
        
        # Save documents
        with open(os.path.join(output_dir, "documents.pkl"), 'wb') as f:
            pickle.dump(self.documents, f)
        
        # Save embeddings as numpy array
        np.save(os.path.join(output_dir, "embeddings.npy"), self.embeddings)
        
        # Save vectorizer and SVD
        with open(os.path.join(output_dir, "vectorizer.pkl"), 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        with open(os.path.join(output_dir, "svd.pkl"), 'wb') as f:
            pickle.dump(self.svd, f)
        
        # Save config
        config = {
            'embedding_dimension': self.embeddings.shape[1],
            'total_documents': len(self.documents),
            'total_chunks': len(self.metadata)
        }
        
        with open(os.path.join(output_dir, "config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"All files saved to {output_dir}/ directory")
        
    def search_similar(self, query, k=5):
        """Search for similar documents"""
        # Transform query using the same vectorizer and SVD
        query_tfidf = self.vectorizer.transform([query])
        query_embedding = self.svd.transform(query_tfidf).astype('float32')
        
        # Manual normalization for query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'rank': i + 1,
                    'score': float(distance),
                    'content': self.documents[idx],
                    'metadata': self.metadata[idx]
                })
        
        return results

def main():
    # Initialize embedder
    embedder = CareerDocumentEmbedder()
    
    # Find all text files automatically
    print("Searching for text files...")
    career_files = embedder.find_career_files()
    
    if not career_files:
        print("No text files found! Please make sure your .txt files are in the same directory or subdirectories.")
        print("Current directory:", os.getcwd())
        return
    
    print(f"Found {len(career_files)} text files:")
    for file in career_files:
        print(f"  - {file}")
    
    # Load documents
    embedder.load_documents_from_files(career_files)
    
    if not embedder.documents:
        print("No documents loaded!")
        return
    
    print(f"Total document chunks: {len(embedder.documents)}")
    
    # Generate embeddings
    embedder.generate_embeddings()
    
    # Build FAISS index
    embedder.build_faiss_index()
    
    # Save everything
    embedder.save_embeddings()
    
    # Test search
    print("\nTesting search functionality...")
    test_queries = [
        "frontend developer skills",
        "job search strategies", 
        "web development career path",
        "JavaScript frameworks"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = embedder.search_similar(query, k=2)
        for result in results:
            print(f"  - {result['metadata']['doc_name']} (score: {result['score']:.3f})")
    
    print(f"\nEmbedding process completed successfully!")
    print(f"Total documents processed: {len(embedder.documents)}")
    print(f"Embedding dimension: {embedder.embeddings.shape[1]}")

if __name__ == "__main__":
    main()