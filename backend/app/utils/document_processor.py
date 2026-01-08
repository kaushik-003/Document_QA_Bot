import os
from typing import List, Dict, Any
import PyPDF2
import docx
from io import BytesIO

class DocumentProcessor:
    """Handle document text extraction"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = BytesIO(file_content)
            doc = docx.Document(docx_file)
            
            text = ""
            for i, para in enumerate(doc.paragraphs):
                if para.text.strip():
                    text += para.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting DOCX text: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            # Try UTF-8 first, then fallback to latin-1
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                text = file_content.decode('latin-1')
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting TXT text: {str(e)}")
    
    @staticmethod
    def extract_text_from_markdown(file_content: bytes) -> str:
        """Extract text from Markdown file"""
        try:
            # Markdown is plain text, just decode it
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                text = file_content.decode('latin-1')
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting Markdown text: {str(e)}")
    
    @staticmethod
    def extract_text(file_content: bytes, file_type: str) -> str:
        """Extract text based on file type"""
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return DocumentProcessor.extract_text_from_pdf(file_content)
        elif file_type == 'docx':
            return DocumentProcessor.extract_text_from_docx(file_content)
        elif file_type == 'txt':
            return DocumentProcessor.extract_text_from_txt(file_content)
        elif file_type in ['md', 'markdown']:
            return DocumentProcessor.extract_text_from_markdown(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 700, overlap: int = 150) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in characters (approximates tokens)
            overlap: Overlap between chunks in characters
            
        Returns:
            List of chunk dictionaries with content and metadata
        """
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size and we have content
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "chunk_index": chunk_index,
                    "content": current_chunk.strip(),
                    "char_count": len(current_chunk.strip())
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
                chunk_index += 1
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append({
                "chunk_index": chunk_index,
                "content": current_chunk.strip(),
                "char_count": len(current_chunk.strip())
            })
        
        return chunks