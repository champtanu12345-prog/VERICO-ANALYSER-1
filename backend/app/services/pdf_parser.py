import fitz  # PyMuPDF
import os

class PDFParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self):
        """
        Extracts text from the PDF, preserving page numbers and basic metadata.
        Returns a list of dictionaries, one per page.
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")

        document = fitz.open(self.filepath)
        filename = os.path.basename(self.filepath)
        
        extracted_data = []
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text = page.get_text("text")
            
            # Clean up the text somewhat
            text = " ".join(text.split())
            
            extracted_data.append({
                "source": filename,
                "page": page_num + 1,  # 1-indexed pages
                "text": text
            })
            
        return extracted_data
