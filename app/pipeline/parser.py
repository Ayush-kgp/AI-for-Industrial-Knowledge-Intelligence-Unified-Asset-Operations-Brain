import fitz  # PyMuPDF
import os

def parse_pdf(file_path: str) -> str:
    """
    Parses text from a PDF file using PyMuPDF.
    If a page has no text, it could flag it for OCR (mocked for now, as PyMuPDF extracts native text).
    """
    doc = fitz.open(file_path)
    full_text = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        
        if not text:
            # Fallback for OCR would happen here by extracting the page image
            # For this MVP, we assume text-native PDFs unless explicitly given a scanned image.
            text = f"[OCR REQUIRED FOR PAGE {page_num+1}]"
        else:
            full_text.append(f"--- Page {page_num+1} ---\n{text}")
            
    doc.close()
    return "\n".join(full_text)
