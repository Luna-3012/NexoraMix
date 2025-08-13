import os
import logging
import mimetypes
import requests
from typing import Optional
from supabase import create_client, Client

LOG = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")  
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "default")

def _detect_mime_type(file_path: str) -> str:
  # Try to detect from file extension first
  mime_type, _ = mimetypes.guess_type(file_path)
  
  if mime_type:
      return mime_type
  
  # Fallback based on file extension
  ext = os.path.splitext(file_path)[1].lower()
  mime_map = {
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.svg': 'image/svg+xml',
      '.json': 'application/json',
      '.txt': 'text/plain',
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.pdf': 'application/pdf',
      '.zip': 'application/zip',
      '.mp4': 'video/mp4',
      '.mp3': 'audio/mpeg',
  }
  
  return mime_map.get(ext, 'application/octet-stream')

def _client():
    """
    Create Supabase client with proper error handling for credentials.
    
    Returns:
        Supabase client
        
    Raises:
        RuntimeError: If Supabase credentials are not configured
    """
    if not SUPABASE_URL:
        LOG.error("Supabase URL not found. Please configure SUPABASE_URL")
        raise RuntimeError("Supabase URL not configured. Set SUPABASE_URL environment variable.")
    
    if not SUPABASE_KEY:
        LOG.error("Supabase key not found. Please configure SUPABASE_ANON_KEY")
        raise RuntimeError("Supabase key not configured. Set SUPABASE_ANON_KEY environment variable.")
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        LOG.error(f"Failed to create Supabase client: {e}")
        raise RuntimeError(f"Supabase client creation failed: {e}")

def upload_file(local_path: str, storage_path: str, public_read: bool = True, content_type: Optional[str] = None) -> str:
    """
    Upload a file to Supabase Storage with proper MIME type detection and error handling.
    
    Args:
        local_path: Path to the local file to upload
        storage_path: Path in Supabase storage bucket
        public_read: Whether to make the object publicly readable
        content_type: Optional explicit MIME type (overrides auto-detection)
        
    Returns:
        Public URL of the uploaded file
        
    Raises:
        RuntimeError: If Supabase not configured or upload fails
        FileNotFoundError: If local file doesn't exist
    """
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")
    
    # Detect MIME type if not provided
    if not content_type:
        content_type = _detect_mime_type(local_path)
        LOG.debug(f"Detected MIME type for {local_path}: {content_type}")
    
    try:
        supabase = _client()
        
        LOG.info(f"Uploading {local_path} to supabase://{SUPABASE_BUCKET}/{storage_path} (Content-Type: {content_type})")
        
        # Read file content
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        # Upload file to Supabase Storage
        result = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": content_type
            }
        )
        
        # Generate public URL
        if public_read:
            url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        else:
            # For private files, you might want to generate a signed URL
            url = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(storage_path, 3600)  # 1 hour expiry
        
        LOG.info(f"Successfully uploaded to: {url}")
        
        return url
        
    except Exception as e:
        LOG.exception(f"Unexpected error during Supabase upload: {e}")
        raise RuntimeError(f"Supabase upload failed: {e}")

def upload_image(local_path: str, storage_path: str, public_read: bool = True) -> str:
    """
    Convenience function for uploading images with proper image MIME types.
    
    Args:
        local_path: Path to the local image file
        storage_path: Path in Supabase storage bucket
        public_read: Whether to make the object publicly readable
        
    Returns:
        Public URL of the uploaded image
    """
    return upload_file(local_path, storage_path, public_read=public_read)

def upload_json(local_path: str, storage_path: str, public_read: bool = True) -> str:
    """
    Convenience function for uploading JSON files with proper MIME type.
    
    Args:
        local_path: Path to the local JSON file
        storage_path: Path in Supabase storage bucket
        public_read: Whether to make the object publicly readable
        
    Returns:
        Public URL of the uploaded JSON file
    """
    return upload_file(local_path, storage_path, public_read=public_read, content_type='application/json')

def delete_file(storage_path: str) -> bool:
    """
    Delete a file from Supabase Storage.
    
    Args:
        storage_path: Path in Supabase storage bucket
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        supabase = _client()
        
        LOG.info(f"Deleting file from supabase://{SUPABASE_BUCKET}/{storage_path}")
        
        result = supabase.storage.from_(SUPABASE_BUCKET).remove([storage_path])
        
        LOG.info(f"Successfully deleted: {storage_path}")
        return True
        
    except Exception as e:
        LOG.exception(f"Failed to delete file {storage_path}: {e}")
        return False

def list_files(prefix: str = "", limit: int = 100) -> list:
    """
    List files in Supabase Storage bucket.
    
    Args:
        prefix: Optional prefix to filter files
        limit: Maximum number of files to return
        
    Returns:
        List of file objects
    """
    try:
        supabase = _client()
        
        LOG.info(f"Listing files in supabase://{SUPABASE_BUCKET} with prefix: {prefix}")
        
        result = supabase.storage.from_(SUPABASE_BUCKET).list(path=prefix)
        
        # Limit results
        files = result[:limit] if result else []
        
        LOG.info(f"Found {len(files)} files")
        return files
        
    except Exception as e:
        LOG.exception(f"Failed to list files: {e}")
        return []
