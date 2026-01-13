"""
Technical Documents Management Module
Handles uploading, updating, viewing, and deleting technical documents.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import shutil
from supabase import create_client, Client
from dotenv import load_dotenv

# Initialize Supabase client
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Constants
TECH_DOCS_DIR = Path("./uploads/tech_docs")
INDEX_FILE = TECH_DOCS_DIR / "index.json"  # Kept for backward compatibility/migration


def initialize_storage():
    """Initialize the tech_docs directory and index file if they don't exist."""
    TECH_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not INDEX_FILE.exists():
        with open(INDEX_FILE, 'w') as f:
            json.dump([], f)


def load_documents_index() -> List[Dict]:
    """Load the documents index from Supabase database."""
    try:
        response = supabase.table("technical_documents").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error loading documents from database: {e}")
        return []


def save_documents_index(documents: List[Dict]):
    """
    Deprecated: This function is kept for backward compatibility.
    Individual operations now interact directly with Supabase.
    """
    # This function is no longer needed with Supabase but kept for compatibility
    pass


def get_all_documents() -> List[Dict]:
    """Get all technical documents with their metadata."""
    return load_documents_index()


def get_document_by_id(doc_id: int) -> Optional[Dict]:
    """Get a specific document by its ID from Supabase."""
    try:
        response = supabase.table("technical_documents").select("*").eq("id", doc_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching document by ID: {e}")
        return None


def get_document_by_name(doc_name: str) -> Optional[Dict]:
    """Get a specific document by its name from Supabase."""
    try:
        response = supabase.table("technical_documents").select("*").eq("name", doc_name).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching document by name: {e}")
        return None


def generate_document_id() -> str:
    """
    Generate a unique document ID based on timestamp.
    
    DEPRECATED: This function is no longer used as Supabase auto-generates IDs.
    Kept for backward compatibility.
    """
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def add_document(file_bytes: bytes, file_name: str, document_name: str, 
                 uploaded_by: str, description: str = "", year: int = None, 
                 month: int = None) -> Tuple[bool, str]:
    """
    Add a new technical document.
    
    Args:
        file_bytes: The file content as bytes
        file_name: Original filename with extension
        document_name: User-friendly name for the document
        uploaded_by: Username of the person uploading
        description: Optional description of the document
        year: Year of the document (required)
        month: Month of the document (required)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    initialize_storage()
    
    # Check if document name already exists
    if get_document_by_name(document_name):
        return False, f"Un documento con el nombre '{document_name}' ya existe."
    
    file_extension = Path(file_name).suffix
    
    # Note: We'll generate the stored_filename after getting the ID from Supabase
    temp_stored_filename = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{file_extension}"
    temp_file_path = TECH_DOCS_DIR / temp_stored_filename
    
    try:
        # Save the file with temporary name first
        with open(temp_file_path, 'wb') as f:
            f.write(file_bytes)
        
        # Use provided year and month, or default to current date
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        # Validate year and month
        if not (2000 <= year <= 2100):
            if temp_file_path.exists():
                temp_file_path.unlink()
            return False, "El año debe estar entre 2000 y 2100."
        
        if not (1 <= month <= 12):
            if temp_file_path.exists():
                temp_file_path.unlink()
            return False, "El mes debe estar entre 1 y 12."
        
        # Determine MIME type
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
        }
        mime_type = mime_types.get(file_extension.lower(), 'application/octet-stream')
        
        # Insert into Supabase without ID (let Supabase auto-generate it)
        new_doc = {
            "name": document_name,
            "description": description,
            "original_filename": file_name,
            "stored_filename": temp_stored_filename,  # Temporary, will update after getting ID
            "file_path": str(temp_file_path),  # Temporary, will update after getting ID
            "uploaded_by": uploaded_by,
            "year": year,
            "month": month,
            "file_size": len(file_bytes),
            "mime_type": mime_type
        }
        
        # Insert and get the auto-generated ID
        response = supabase.table("technical_documents").insert(new_doc).execute()
        
        if not response.data or len(response.data) == 0:
            if temp_file_path.exists():
                temp_file_path.unlink()
            return False, "Error al insertar el documento en la base de datos."
        
        # Get the auto-generated ID
        doc_id = response.data[0]['id']
        
        # Now rename the file with the proper ID
        stored_filename = f"{doc_id}{file_extension}"
        file_path = TECH_DOCS_DIR / stored_filename
        
        # Rename the temporary file
        temp_file_path.rename(file_path)
        
        # Update the record with the correct stored_filename and file_path
        supabase.table("technical_documents").update({
            "stored_filename": stored_filename,
            "file_path": str(file_path)
        }).eq("id", doc_id).execute()
        
        return True, f"Documento '{document_name}' subido exitosamente."
    
    except Exception as e:
        # Clean up file if it was created
        if temp_file_path.exists():
            temp_file_path.unlink()
        return False, f"Error al subir el documento: {str(e)}"


def update_document(doc_id: int, file_bytes: bytes = None, file_name: str = None,
                    document_name: str = None, description: str = None,
                    updated_by: str = None) -> Tuple[bool, str]:
    """
    Update an existing technical document.
    
    Args:
        doc_id: ID of the document to update
        file_bytes: New file content (optional)
        file_name: New filename (optional, required if file_bytes provided)
        document_name: New document name (optional)
        description: New description (optional)
        updated_by: Username of the person updating
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Find the document
    doc = get_document_by_id(doc_id)
    
    if not doc:
        return False, "Documento no encontrado."
    
    try:
        updates = {}
        
        # Check if new name conflicts with another document
        if document_name and document_name != doc['name']:
            existing_doc = get_document_by_name(document_name)
            if existing_doc and existing_doc['id'] != doc_id:
                return False, f"Ya existe un documento con el nombre '{document_name}'."
            updates['name'] = document_name
        
        # Update description if provided
        if description is not None:
            updates['description'] = description
        
        # Update file if provided
        if file_bytes and file_name:
            # Delete old file
            old_file_path = Path(doc['file_path'])
            if old_file_path.exists():
                old_file_path.unlink()
            
            # Save new file with same ID but possibly different extension
            file_extension = Path(file_name).suffix
            stored_filename = f"{doc_id}{file_extension}"
            file_path = TECH_DOCS_DIR / stored_filename
            
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            # Determine MIME type
            mime_types = {
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xls': 'application/vnd.ms-excel',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.txt': 'text/plain',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
            }
            mime_type = mime_types.get(file_extension.lower(), 'application/octet-stream')
            
            updates['original_filename'] = file_name
            updates['stored_filename'] = stored_filename
            updates['file_path'] = str(file_path)
            updates['file_size'] = len(file_bytes)
            updates['mime_type'] = mime_type
        
        # Add updated_by if provided
        if updated_by:
            updates['updated_by'] = updated_by
        
        # Update in Supabase (updated_at will be handled by trigger)
        if updates:
            supabase.table("technical_documents").update(updates).eq("id", doc_id).execute()
        
        return True, f"Documento '{doc['name']}' actualizado exitosamente."
    
    except Exception as e:
        return False, f"Error al actualizar el documento: {str(e)}"


def delete_document(doc_id: str) -> Tuple[bool, str]:
    """
    Delete a technical document.
    
    Args:
        doc_id: ID of the document to delete
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Find the document
    doc = get_document_by_id(doc_id)
    
    if not doc:
        return False, "Documento no encontrado."
    
    try:
        # Delete the file
        file_path = Path(doc['file_path'])
        if file_path.exists():
            file_path.unlink()
        
        # Delete from Supabase
        supabase.table("technical_documents").delete().eq("id", doc_id).execute()
        
        return True, f"Documento '{doc['name']}' eliminado exitosamente."
    
    except Exception as e:
        return False, f"Error al eliminar el documento: {str(e)}"


def get_document_file(doc_id: int) -> Optional[Tuple[bytes, str, str]]:
    """
    Get the file content and metadata for a document.
    
    Args:
        doc_id: ID of the document
        
    Returns:
        Tuple of (file_bytes, filename, mime_type) or None if not found
    """
    doc = get_document_by_id(doc_id)
    if not doc:
        return None
    
    file_path = Path(doc['file_path'])
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        # Determine MIME type based on extension
        extension = Path(doc['original_filename']).suffix.lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
        }
        mime_type = mime_types.get(extension, 'application/octet-stream')
        
        return file_bytes, doc['original_filename'], mime_type
    
    except Exception:
        return None


def search_documents(query: str) -> List[Dict]:
    """
    Search documents by name or description.
    
    Args:
        query: Search query string
        
    Returns:
        List of matching documents
    """
    if not query:
        return get_all_documents()
    
    try:
        # Use Supabase's ilike for case-insensitive search
        query_lower = f"%{query}%"
        response = supabase.table("technical_documents").select("*").or_(
            f"name.ilike.{query_lower},description.ilike.{query_lower},original_filename.ilike.{query_lower}"
        ).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"Error searching documents: {e}")
        return []


def get_storage_stats() -> Dict:
    """Get storage statistics for technical documents."""
    documents = load_documents_index()
    
    total_files = len(documents)
    total_size = sum(doc.get('file_size', 0) for doc in documents)
    
    # Convert bytes to human-readable format
    if total_size < 1024:
        size_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        size_str = f"{total_size / 1024:.2f} KB"
    elif total_size < 1024 * 1024 * 1024:
        size_str = f"{total_size / (1024 * 1024):.2f} MB"
    else:
        size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
    
    return {
        "total_files": total_files,
        "total_size_bytes": total_size,
        "total_size_formatted": size_str
    }
