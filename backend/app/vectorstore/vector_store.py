import os
import pickle
from typing import List, Dict, Any, Tuple

import numpy as np

from app.services.text_features import FEATURE_DIM, text_to_features, texts_to_features

class VectorStore:
    def __init__(self, index_path="search_index.npy", meta_path="search_meta.pkl"):
        self.index_path = index_path
        self.meta_path = meta_path
        
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = np.load(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            self.index = np.empty((0, FEATURE_DIM), dtype=np.float32)
            self.metadata = []

    def add_documents(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
            
        texts = [chunk["text"] for chunk in chunks]
        embeddings = texts_to_features(texts)
        
        self.index = np.vstack([self.index, embeddings])
        self.metadata.extend(chunks)
        self._save()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        if len(self.metadata) == 0:
            return []
            
        query_embedding = text_to_features(query)
        scores = self.index @ query_embedding
        indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in indices:
            if idx < len(self.metadata) and scores[idx] > 0:
                results.append((self.metadata[idx], float(scores[idx])))
                
        return results

    def _save(self):
        np.save(self.index_path, self.index)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def clear(self):
        self.index = np.empty((0, FEATURE_DIM), dtype=np.float32)
        self.metadata = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)
