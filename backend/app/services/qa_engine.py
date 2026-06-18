from typing import List, Dict, Any, Tuple

class QAEngine:
    def __init__(self, use_qa_model: bool = False):
        self.use_qa_model = False

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

        citations = []
        for chunk_data, retrieval_score in retrieved_chunks:
            chunk = chunk_data
            citations.append({
                "document": chunk["source"],
                "page": chunk["page"],
                "excerpt": chunk["text"]
            })

        best_chunk = retrieved_chunks[0][0]
        final_answer = best_chunk["text"]
        confidence = retrieved_chunks[0][1]
            
        return {
            "answer": final_answer,
            "confidence": confidence,
            "citations": citations
        }
