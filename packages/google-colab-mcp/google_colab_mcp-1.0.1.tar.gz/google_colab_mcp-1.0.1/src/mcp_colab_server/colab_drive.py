"""Google Drive API integration for Colab notebook management."""

import json
import logging
from typing import Dict, List, Optional, Any
from io import BytesIO

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from .auth_manager import AuthManager
from .utils import (
    create_notebook_content, 
    create_code_cell, 
    sanitize_filename,
    validate_notebook_id,
    retry_with_backoff
)


class ColabDriveManager:
    """Manages Google Colab notebooks through Drive API."""
    
    COLAB_MIME_TYPE = 'application/vnd.google.colaboratory'
    
    def __init__(self, auth_manager: AuthManager):
        """Initialize the Drive manager."""
        self.auth_manager = auth_manager
        self.logger = logging.getLogger(__name__)
        self._service = None
    
    def _handle_http_error(self, error: HttpError, operation: str, resource_id: str = None) -> Exception:
        """Standardized HTTP error handling."""
        if error.resp.status == 404:
            resource_name = f" {resource_id}" if resource_id else ""
            return Exception(f"Notebook not found:{resource_name}")
        elif error.resp.status == 403:
            return Exception(f"Access denied for {operation}. Check permissions.")
        elif error.resp.status == 429:
            return Exception(f"Rate limit exceeded for {operation}. Please try again later.")
        else:
            self.logger.error(f"HTTP {error.resp.status} error during {operation}: {error}")
            return Exception(f"Failed to {operation}: HTTP {error.resp.status}")
    
    @property
    def service(self):
        """Get authenticated Drive service."""
        if not self._service:
            self._service = self.auth_manager.get_drive_service()
        return self._service
    
    @retry_with_backoff(max_retries=3, delay=1.0)
    def create_notebook(self, name: str, content: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Create a new Colab notebook."""
        media = None
        try:
            # Sanitize filename
            safe_name = sanitize_filename(name)
            if not safe_name.endswith('.ipynb'):
                safe_name += '.ipynb'
            
            # Create notebook content if not provided
            if content is None:
                content = create_notebook_content([
                    create_code_cell("# Welcome to your new Colab notebook!\nprint('Hello, World!')")
                ])
            
            # Convert content to JSON
            notebook_json = json.dumps(content, indent=2)
            
            # Create file metadata
            file_metadata = {
                'name': safe_name,
                'mimeType': self.COLAB_MIME_TYPE,
                'parents': []  # Will be placed in root directory
            }
            
            # Upload notebook
            media = MediaIoBaseUpload(
                BytesIO(notebook_json.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            self.logger.info(f"Created notebook: {file.get('name')} (ID: {file.get('id')})")
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'url': file.get('webViewLink'),
                'colab_url': f"https://colab.research.google.com/drive/{file.get('id')}"
            }
            
        except HttpError as e:
            self.logger.error(f"HTTP error creating notebook: {e}")
            raise Exception(f"Failed to create notebook: {e}")
        except Exception as e:
            self.logger.error(f"Error creating notebook: {e}")
            raise
        finally:
            # Ensure proper cleanup of media resources
            if media and hasattr(media, '_fd'):
                try:
                    media._fd.close()
                except Exception:
                    pass
    
    @retry_with_backoff(max_retries=3, delay=1.0)
    def get_notebook_content(self, notebook_id: str) -> Dict[str, Any]:
        """Get the content of a Colab notebook."""
        file_io = None
        try:
            if not validate_notebook_id(notebook_id):
                raise ValueError("Invalid notebook ID format")
            
            # Download notebook content
            request = self.service.files().get_media(fileId=notebook_id)
            file_io = BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Parse JSON content
            file_io.seek(0)
            content = json.loads(file_io.read().decode('utf-8'))
            
            self.logger.info(f"Retrieved notebook content for ID: {notebook_id}")
            return content
            
        except HttpError as e:
            if e.resp.status == 404:
                raise Exception(f"Notebook not found: {notebook_id}")
            else:
                self.logger.error(f"HTTP error getting notebook content: {e}")
                raise Exception(f"Failed to get notebook content: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in notebook: {e}")
            raise Exception("Notebook contains invalid JSON")
        except Exception as e:
            self.logger.error(f"Error getting notebook content: {e}")
            raise
        finally:
            # Ensure proper cleanup of BytesIO resource
            if file_io:
                file_io.close()
    
    @retry_with_backoff(max_retries=3, delay=1.0)
    def update_notebook(self, notebook_id: str, content: Dict[str, Any]) -> bool:
        """Update a Colab notebook with new content."""
        try:
            if not validate_notebook_id(notebook_id):
                raise ValueError("Invalid notebook ID format")
            
            # Convert content to JSON
            notebook_json = json.dumps(content, indent=2)
            
            # Update file
            media = MediaIoBaseUpload(
                BytesIO(notebook_json.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            self.service.files().update(
                fileId=notebook_id,
                media_body=media
            ).execute()
            
            self.logger.info(f"Updated notebook: {notebook_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                raise Exception(f"Notebook not found: {notebook_id}")
            else:
                self.logger.error(f"HTTP error updating notebook: {e}")
                raise Exception(f"Failed to update notebook: {e}")
        except Exception as e:
            self.logger.error(f"Error updating notebook: {e}")
            raise
    
    @retry_with_backoff(max_retries=3, delay=1.0)
    def list_notebooks(self, max_results: int = 100) -> List[Dict[str, str]]:
        """List user's Colab notebooks."""
        try:
            query = f"mimeType='{self.COLAB_MIME_TYPE}' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=min(max_results, 1000),
                fields="files(id,name,modifiedTime,webViewLink,size)"
            ).execute()
            
            files = results.get('files', [])
            
            notebooks = []
            for file in files:
                notebooks.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'modified': file.get('modifiedTime'),
                    'url': file.get('webViewLink'),
                    'colab_url': f"https://colab.research.google.com/drive/{file.get('id')}",
                    'size': file.get('size', 'Unknown')
                })
            
            self.logger.info(f"Found {len(notebooks)} notebooks")
            return notebooks
            
        except HttpError as e:
            self.logger.error(f"HTTP error listing notebooks: {e}")
            raise Exception(f"Failed to list notebooks: {e}")
        except Exception as e:
            self.logger.error(f"Error listing notebooks: {e}")
            raise
    
    @retry_with_backoff(max_retries=3, delay=1.0)
    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a Colab notebook."""
        try:
            if not validate_notebook_id(notebook_id):
                raise ValueError("Invalid notebook ID format")
            
            self.service.files().delete(fileId=notebook_id).execute()
            
            self.logger.info(f"Deleted notebook: {notebook_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                raise Exception(f"Notebook not found: {notebook_id}")
            else:
                self.logger.error(f"HTTP error deleting notebook: {e}")
                raise Exception(f"Failed to delete notebook: {e}")
        except Exception as e:
            self.logger.error(f"Error deleting notebook: {e}")
            raise
    
    def get_notebook_info(self, notebook_id: str) -> Dict[str, Any]:
        """Get metadata information about a notebook."""
        try:
            if not validate_notebook_id(notebook_id):
                raise ValueError("Invalid notebook ID format")
            
            file = self.service.files().get(
                fileId=notebook_id,
                fields="id,name,mimeType,size,createdTime,modifiedTime,webViewLink,owners"
            ).execute()
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'mime_type': file.get('mimeType'),
                'size': file.get('size'),
                'created': file.get('createdTime'),
                'modified': file.get('modifiedTime'),
                'url': file.get('webViewLink'),
                'colab_url': f"https://colab.research.google.com/drive/{file.get('id')}",
                'owners': file.get('owners', [])
            }
            
        except HttpError as e:
            if e.resp.status == 404:
                raise Exception(f"Notebook not found: {notebook_id}")
            else:
                self.logger.error(f"HTTP error getting notebook info: {e}")
                raise Exception(f"Failed to get notebook info: {e}")
        except Exception as e:
            self.logger.error(f"Error getting notebook info: {e}")
            raise
    
    def add_code_cell(self, notebook_id: str, code: str, position: Optional[int] = None) -> bool:
        """Add a code cell to an existing notebook."""
        try:
            # Get current content
            content = self.get_notebook_content(notebook_id)
            
            # Create new code cell
            new_cell = create_code_cell(code)
            
            # Add cell at specified position or at the end
            if position is not None and 0 <= position <= len(content['cells']):
                content['cells'].insert(position, new_cell)
            else:
                content['cells'].append(new_cell)
            
            # Update notebook
            return self.update_notebook(notebook_id, content)
            
        except Exception as e:
            self.logger.error(f"Error adding code cell: {e}")
            raise