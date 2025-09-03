import os
import tempfile
from typing import List, Dict, Any
from tika import parser
import logging
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Legacy document processor - kept for backward compatibility.
    For new CV processing, use CVProcessor instead.
    """
    def __init__(self):
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200  # overlap between chunks
    
    async def process_document(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Process a document and return chunks"""
        try:
            # Extract text using Tika
            text = await self._extract_text(file_path)
            
            # Clean and chunk the text
            chunks = self._chunk_text(text, filename)
            
            logger.info(f"Processed {filename} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from file using Tika"""
        try:
            # Parse document with Tika
            parsed = parser.from_file(file_path)
            
            # Get text content
            text = parsed["content"]
            
            if not text:
                raise ValueError("No text content extracted from document")
            
            # Clean the text
            text = self._clean_text(text)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _chunk_text(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        words = text.split()
        
        # Calculate approximate words per chunk (assuming ~5 chars per word)
        words_per_chunk = self.chunk_size // 5
        words_overlap = self.chunk_overlap // 5
        
        start = 0
        chunk_index = 0
        
        while start < len(words):
            # Get chunk words
            end = start + words_per_chunk
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            # Only add chunk if it has meaningful content
            if len(chunk_text.strip()) > 50:  # Minimum chunk size
                chunks.append({
                    "text": chunk_text,
                    "filename": filename,
                    "chunk_index": chunk_index
                })
                chunk_index += 1
            
            # Move start position with overlap
            start = end - words_overlap
            
            # Break if we've reached the end
            if end >= len(words):
                break
        
        return chunks
    
    def set_chunk_parameters(self, chunk_size: int, chunk_overlap: int):
        """Update chunking parameters"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"Updated chunk parameters: size={chunk_size}, overlap={chunk_overlap}") 