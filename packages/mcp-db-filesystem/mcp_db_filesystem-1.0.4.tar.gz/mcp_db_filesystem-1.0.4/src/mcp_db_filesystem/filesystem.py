"""Filesystem operations for MCP server."""

import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import aiofiles
import asyncio
from datetime import datetime

from .config import get_config

logger = logging.getLogger(__name__)


class FilesystemSecurityError(Exception):
    """Raised when a filesystem operation fails security checks."""
    pass


class FilesystemOperationError(Exception):
    """Raised when a filesystem operation fails."""
    pass


class FilesystemManager:
    """Manages filesystem operations with security controls."""
    
    def __init__(self):
        self._validate_configuration()
        self._log_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate filesystem configuration."""
        config = get_config()
        # Log current access mode
        if config.filesystem.is_full_access_mode:
            logger.warning("Filesystem in FULL ACCESS mode - can access all disk files!")
            logger.warning("Consider restricting access by setting FS_ALLOWED_PATHS for production use")
        else:
            logger.info(f"Filesystem access restricted to {len(config.filesystem.allowed_paths)} allowed paths")
        
        # Validate allowed paths exist and are accessible
        for path_str in config.filesystem.allowed_paths:
            if path_str == '*':  # Skip wildcard
                continue
                
            path = Path(path_str)
            if not path.exists():
                logger.warning(f"Allowed path does not exist: {path}")
            elif not path.is_dir():
                logger.warning(f"Allowed path is not a directory: {path}")
            else:
                logger.debug(f"Validated allowed path: {path}")
    
    def _log_configuration(self) -> None:
        """Log current filesystem configuration for debugging."""
        config = get_config()
        logger.info("Filesystem Configuration Summary:")
        logger.info(f"  Access Mode: {'FULL ACCESS' if config.filesystem.is_full_access_mode else 'RESTRICTED'}")
        logger.info(f"  Allowed Paths: {config.filesystem.allowed_paths if config.filesystem.allowed_paths else 'ALL (full access)'}")
        logger.info(f"  Max File Size: {config.filesystem.max_file_size / (1024*1024):.1f} MB")
        logger.info(f"  Allowed Extensions: {config.filesystem.allowed_extensions if config.filesystem.allowed_extensions else 'ALL'}")
        logger.info(f"  Write Enabled: {config.filesystem.enable_write}")
        logger.info(f"  Delete Enabled: {config.filesystem.enable_delete}")
        logger.info(f"  Ignore File Locks: {config.filesystem.ignore_file_locks}")
    
    def _is_path_allowed(self, file_path: Union[str, Path]) -> bool:
        """Check if a path is allowed based on configuration."""
        config = get_config()
        file_path = Path(file_path).resolve()

        # Check if we're in full access mode
        if config.filesystem.is_full_access_mode:
            logger.debug(f"Path allowed: {file_path} (full access mode - no restrictions)")
            return True

        # Check if path is under any allowed path
        for allowed_path_str in config.filesystem.allowed_paths:
            # Skip wildcard entries (already handled above)
            if allowed_path_str == '*':
                continue
                
            allowed_path = Path(allowed_path_str).resolve()
            try:
                file_path.relative_to(allowed_path)
                logger.debug(f"Path allowed: {file_path} is under {allowed_path}")
                return True  # Path is under an allowed directory
            except ValueError:
                continue  # Path is not under this allowed directory

        logger.debug(f"Path not allowed: {file_path} is not under any allowed directory")
        return False  # Path is not under any allowed directory
    
    def _is_extension_allowed(self, file_path: Union[str, Path]) -> bool:
        """Check if file extension is allowed."""
        config = get_config()
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        # If allowed extensions specified, check if extension is in the list
        if config.filesystem.allowed_extensions:
            # Check for wildcard (allow all)
            if '*.*' in config.filesystem.allowed_extensions or '*' in config.filesystem.allowed_extensions:
                logger.debug(f"Extension allowed: {extension} (wildcard mode - all extensions allowed)")
                return True
            
            # Check specific extensions
            allowed = extension in config.filesystem.allowed_extensions
            logger.debug(f"Extension {'allowed' if allowed else 'not allowed'}: {extension}")
            return allowed

        # No restrictions configured - allow all extensions (full access mode)
        logger.debug(f"Extension allowed: {extension} (no restrictions configured)")
        return True
    
    def _validate_file_operation(self, file_path: Union[str, Path], operation: str) -> None:
        """Validate file operation for security."""
        config = get_config()
        file_path = Path(file_path)
        
        # Check if path is allowed
        if not self._is_path_allowed(file_path):
            raise FilesystemSecurityError(f"Path not allowed: {file_path}")
        
        # Check file extension
        if not self._is_extension_allowed(file_path):
            raise FilesystemSecurityError(f"File extension not allowed: {file_path.suffix}")
        
        # Check write operations
        if operation in ['write', 'create', 'move', 'copy'] and not config.filesystem.enable_write:
            raise FilesystemSecurityError("Write operations are disabled")
        
        # Check delete operations
        if operation == 'delete' and not config.filesystem.enable_delete:
            raise FilesystemSecurityError("Delete operations are disabled")
        
        logger.debug(f"File operation validated: {operation} on {file_path}")
    
    def read_file(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """Read file content."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, 'read')
        
        try:
            if not file_path.exists():
                raise FilesystemOperationError(f"File does not exist: {file_path}")
            
            if not file_path.is_file():
                raise FilesystemOperationError(f"Path is not a file: {file_path}")
            
            # Check file size
            config = get_config()
            file_size = file_path.stat().st_size
            if file_size > config.filesystem.max_file_size:
                raise FilesystemOperationError(
                    f"File too large: {file_size} bytes (max: {config.filesystem.max_file_size})"
                )
            
            # Try to read file, with option to ignore locks
            content = None
            last_error = None
            
            # First try normal read
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
            except (PermissionError, OSError) as e:
                last_error = e
                if config.filesystem.ignore_file_locks:
                    logger.warning(f"File may be locked, trying alternative read methods: {file_path}")
                    
                    # Try reading with different sharing modes on Windows
                    try:
                        import msvcrt
                        import os
                        # Try opening with shared read/write access
                        fd = os.open(file_path, os.O_RDONLY | os.O_BINARY)
                        try:
                            with os.fdopen(fd, 'rb') as f:
                                raw_content = f.read()
                                content = raw_content.decode(encoding)
                        finally:
                            # fd is closed by fdopen context manager
                            pass
                    except (ImportError, OSError, UnicodeDecodeError):
                        # Fallback: try reading in binary mode and decode
                        try:
                            with open(file_path, 'rb') as f:
                                raw_content = f.read()
                                content = raw_content.decode(encoding, errors='replace')
                        except Exception:
                            # If all methods fail, raise the original error
                            raise last_error
                else:
                    raise last_error
            
            if content is None:
                raise FilesystemOperationError(f"Failed to read file: {last_error}")
            
            logger.info(f"File read successfully: {file_path} ({file_size} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise FilesystemOperationError(f"Failed to read file: {e}")
    
    def write_file(self, file_path: Union[str, Path], content: str, encoding: str = 'utf-8', create_dirs: bool = True) -> None:
        """Write content to file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, 'write')
        
        try:
            # Check content size
            config = get_config()
            content_size = len(content.encode(encoding))
            if content_size > config.filesystem.max_file_size:
                raise FilesystemOperationError(
                    f"Content too large: {content_size} bytes (max: {config.filesystem.max_file_size})"
                )
            
            # Create parent directories if needed
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to write file, with option to ignore locks
            last_error = None
            
            # First try normal write
            try:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
            except (PermissionError, OSError) as e:
                last_error = e
                if config.filesystem.ignore_file_locks:
                    logger.warning(f"File may be locked, trying alternative write methods: {file_path}")
                    
                    # Try writing with different sharing modes on Windows
                    try:
                        import tempfile
                        import shutil
                        
                        # Write to temporary file first, then replace
                        temp_dir = file_path.parent
                        with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, 
                                                       dir=temp_dir, delete=False, 
                                                       suffix='.tmp') as temp_file:
                            temp_file.write(content)
                            temp_path = temp_file.name
                        
                        # Try to replace the original file
                        try:
                            if file_path.exists():
                                # On Windows, we might need to remove the target first
                                file_path.unlink()
                            shutil.move(temp_path, file_path)
                        except Exception:
                            # Clean up temp file if replacement failed
                            Path(temp_path).unlink(missing_ok=True)
                            raise
                            
                    except Exception:
                        # If all methods fail, raise the original error
                        raise last_error
                else:
                    raise last_error
            
            logger.info(f"File written successfully: {file_path} ({content_size} bytes)")
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise FilesystemOperationError(f"Failed to write file: {e}")
    
    def list_directory(self, dir_path: Union[str, Path], recursive: bool = False) -> List[Dict[str, Any]]:
        """List directory contents."""
        dir_path = Path(dir_path)
        self._validate_file_operation(dir_path, 'read')
        
        try:
            if not dir_path.exists():
                raise FilesystemOperationError(f"Directory does not exist: {dir_path}")
            
            if not dir_path.is_dir():
                raise FilesystemOperationError(f"Path is not a directory: {dir_path}")
            
            items = []
            
            if recursive:
                for item in dir_path.rglob('*'):
                    if self._is_path_allowed(item):
                        items.append(self._get_file_info(item))
            else:
                for item in dir_path.iterdir():
                    if self._is_path_allowed(item):
                        items.append(self._get_file_info(item))
            
            logger.info(f"Directory listed successfully: {dir_path} ({len(items)} items)")
            return items
            
        except Exception as e:
            logger.error(f"Failed to list directory {dir_path}: {e}")
            raise FilesystemOperationError(f"Failed to list directory: {e}")
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get file information."""
        try:
            stat = file_path.stat()
            return {
                'name': file_path.name,
                'path': str(file_path),
                'type': 'directory' if file_path.is_dir() else 'file',
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'extension': file_path.suffix.lower() if file_path.is_file() else None,
            }
        except Exception as e:
            logger.warning(f"Failed to get file info for {file_path}: {e}")
            return {
                'name': file_path.name,
                'path': str(file_path),
                'type': 'unknown',
                'error': str(e)
            }
    
    def create_directory(self, dir_path: Union[str, Path], parents: bool = True) -> None:
        """Create directory."""
        dir_path = Path(dir_path)
        self._validate_file_operation(dir_path, 'create')
        
        try:
            dir_path.mkdir(parents=parents, exist_ok=True)
            logger.info(f"Directory created successfully: {dir_path}")
            
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            raise FilesystemOperationError(f"Failed to create directory: {e}")
    
    def delete_file(self, file_path: Union[str, Path]) -> None:
        """Delete file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, 'delete')
        
        try:
            if not file_path.exists():
                raise FilesystemOperationError(f"File does not exist: {file_path}")
            
            if file_path.is_file():
                file_path.unlink()
                logger.info(f"File deleted successfully: {file_path}")
            else:
                raise FilesystemOperationError(f"Path is not a file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise FilesystemOperationError(f"Failed to delete file: {e}")


# Global filesystem manager instance
fs_manager = FilesystemManager()
