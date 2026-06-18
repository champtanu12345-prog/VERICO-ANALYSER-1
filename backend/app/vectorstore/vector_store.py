import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, index_path="faiss_index.bin", meta_path="faiss_meta.pkl", model_name="all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.meta_path = meta_path
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Load or initialize index
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = [] # List to map FAISS ids to chunk dicts

    def add_documents(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
            
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        self.index.add(embeddings)
        self.metadata.extend(chunks)
        self._save()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if self.index.ntotal == 0:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                # Convert L2 distance to a dummy relevance score (lower distance = higher score)
                score = 1.0 / (1.0 + distances[0][i])
                results.append((self.metadata[idx], float(score)))
                
        return results

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)
