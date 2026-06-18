import uuid
from typing import List, Dict, Any

class Chunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits text into chunks of `chunk_size` characters with `chunk_overlap`.
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
            
        return chunks

    def process_document(self, document_id: str, parsed_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes parsed pages from PDFParser and returns a list of chunk metadata dictionaries.
        """
        all_chunks = []
        for page_data in parsed_pages:
            text = page_data["text"]
            if not text.strip():
                continue
                
            text_chunks = self.chunk_text(text)
            
            for chunk_str in text_chunks:
                all_chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "source": page_data["source"],
                    "page": page_data["page"],
                    "text": chunk_str
                })
                
        return all_chunks
