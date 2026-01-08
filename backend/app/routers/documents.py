from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import uuid
from datetime import datetime

from app.models.schemas import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentInfo,
    DeleteResponse
)
from app.utils.database import get_documents_collection, get_chunks_collection
from app.utils.document_processor import DocumentProcessor
from app.utils.embeddings import get_embedding_generator
from app.utils.vector_store import get_vector_store
from app.config import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.md'}

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document
    
    Supports: PDF, DOCX, TXT, MD
    """
    # Validate file extension
    file_ext = '.' + file.filename.split('.')[-1].lower()
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract text
        file_type = file_ext.replace('.', '')
        text = DocumentProcessor.extract_text(file_content, file_type)
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Document appears to be empty or too short")
        
        # Chunk the text
        chunks = DocumentProcessor.chunk_text(
            text,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to create chunks from document")
        
        # Generate embeddings
        embedding_gen = get_embedding_generator()
        chunk_texts = [chunk['content'] for chunk in chunks]
        embeddings = embedding_gen.generate_embeddings(chunk_texts)
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Store in MongoDB
        documents_col = get_documents_collection()
        chunks_col = get_chunks_collection()
        
        # Store document metadata
        document_data = {
            "document_id": document_id,
            "filename": file.filename,
            "file_type": file_type,
            "upload_date": datetime.utcnow(),
            "total_chunks": len(chunks),
            "total_chars": len(text)
        }
        documents_col.insert_one(document_data)
        
        # Store chunks in MongoDB
        chunk_docs = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_doc = {
                "document_id": document_id,
                "chunk_index": chunk['chunk_index'],
                "content": chunk['content'],
                "char_count": chunk['char_count'],
                "embedding": embedding
            }
            chunk_docs.append(chunk_doc)
        
        if chunk_docs:
            chunks_col.insert_many(chunk_docs)
        
        # Store in vector database
        vector_store = get_vector_store()
        vector_store.add_chunks(chunks, document_id, embeddings)
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_type=file_type,
            total_chunks=len(chunks),
            status="success",
            message=f"Document processed successfully with {len(chunks)} chunks"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """Get list of all uploaded documents"""
    try:
        documents_col = get_documents_collection()
        docs = list(documents_col.find({}, {"_id": 0}).sort("upload_date", -1))
        
        document_list = [
            DocumentInfo(
                document_id=doc['document_id'],
                filename=doc['filename'],
                file_type=doc['file_type'],
                upload_date=doc['upload_date'],
                total_chunks=doc['total_chunks']
            )
            for doc in docs
        ]
        
        return DocumentListResponse(
            documents=document_list,
            total=len(document_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

@router.delete("/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str):
    """Delete a specific document and all its chunks"""
    try:
        documents_col = get_documents_collection()
        chunks_col = get_chunks_collection()
        
        # Check if document exists
        doc = documents_col.find_one({"document_id": document_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from MongoDB
        documents_col.delete_one({"document_id": document_id})
        chunks_col.delete_many({"document_id": document_id})
        
        # Delete from vector store
        vector_store = get_vector_store()
        vector_store.delete_by_document_id(document_id)
        
        return DeleteResponse(
            success=True,
            message=f"Document '{doc['filename']}' deleted successfully",
            document_id=document_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.delete("/", response_model=DeleteResponse)
async def delete_all_documents():
    """Delete all documents and reset knowledge base"""
    try:
        documents_col = get_documents_collection()
        chunks_col = get_chunks_collection()
        
        # Count before deletion
        doc_count = documents_col.count_documents({})
        
        # Delete from MongoDB
        documents_col.delete_many({})
        chunks_col.delete_many({})
        
        # Clear vector store
        vector_store = get_vector_store()
        vector_store.clear_all()
        
        return DeleteResponse(
            success=True,
            message=f"Knowledge base reset successfully. Deleted {doc_count} documents."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting knowledge base: {str(e)}")