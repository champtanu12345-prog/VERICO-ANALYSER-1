from transformers import pipeline
import os
from typing import List, Dict, Any, Tuple

class QAEngine:
    def __init__(self, use_qa_model: bool = True):
        self.use_qa_model = use_qa_model
        if self.use_qa_model:
            # We load the pipeline once
            self.qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
        else:
            self.qa_pipeline = None

    def get_answer(self, question: str, retrieved_chunks: List[Tuple[Dict[str, Any], float]]) -> Dict[str, Any]:
        """
        Takes a question and a list of chunks from VectorStore.search().
        Returns the best answer along with citations.
        """
        if not retrieved_chunks:
            return {
                "answer": "No relevant information found.",
                "confidence": 0.0,
                "citations": []
            }

        # Combine text context for QA model if needed, but standard pipeline works best on single context
        # We will iterate through chunks and find the best score
        best_answer = {"score": 0.0, "answer": "", "chunk": None}
        
        citations = []
        for chunk_data, retrieval_score in retrieved_chunks:
            chunk = chunk_data
            citations.append({
                "document": chunk["source"],
                "page": chunk["page"],
                "excerpt": chunk["text"]
            })
            
            if self.use_qa_model:
                try:
                    result = self.qa_pipeline(question=question, context=chunk["text"])
                    if result["score"] > best_answer["score"]:
                        best_answer = {
                            "score": result["score"],
                            "answer": result["answer"],
                            "chunk": chunk
                        }
                except Exception as e:
                    print(f"Error in QA pipeline: {e}")
                    
        if self.use_qa_model:
            final_answer = best_answer["answer"] if best_answer["answer"] else "Could not determine an answer."
            confidence = best_answer["score"]
        else:
            # Best-span extraction fallback: just return the highest scoring chunk's text
            best_chunk = retrieved_chunks[0][0]
            final_answer = best_chunk["text"]
            confidence = retrieved_chunks[0][1] # The retrieval score
            
        return {
            "answer": final_answer,
            "confidence": confidence,
            "citations": citations
        }
