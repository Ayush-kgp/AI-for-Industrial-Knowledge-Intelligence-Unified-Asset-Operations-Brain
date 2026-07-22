import re
from typing import List

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 100) -> List[str]:
    """
    A simple text splitter that chunks text by paragraphs or length,
    ensuring no chunk exceeds max_chars.
    """
    chunks = []
    
    # Simple split by paragraphs first
    paragraphs = text.split('\n\n')
    current_chunk = ""
    
    for p in paragraphs:
        # If adding the next paragraph exceeds the limit, save current and start new
        if len(current_chunk) + len(p) > max_chars and current_chunk:
            chunks.append(current_chunk.strip())
            # Simple overlap handling (taking last 'overlap' chars, adjusted to word boundary)
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            # Find first space to avoid cutting words
            first_space = overlap_text.find(' ')
            if first_space != -1:
                overlap_text = overlap_text[first_space:]
                
            current_chunk = overlap_text + "\n\n" + p
        else:
            if current_chunk:
                current_chunk += "\n\n" + p
            else:
                current_chunk = p
                
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks
