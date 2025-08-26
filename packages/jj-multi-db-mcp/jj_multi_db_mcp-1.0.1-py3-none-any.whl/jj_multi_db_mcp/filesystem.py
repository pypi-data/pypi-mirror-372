"""Filesystem operations manager."""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)


class FilesystemManager:
    """Filesystem operations manager."""
    
    def __init__(self):
        """Initialize filesystem manager."""
        # Get configuration from environment variables
        self.allowed_paths = self._parse_paths(os.getenv("FS_ALLOWED_PATHS", "*"))
        self.allowed_extensions = self._parse_extensions(os.getenv("FS_ALLOWED_EXTENSIONS", "*"))
        self.max_file_size = int(os.getenv("FS_MAX_FILE_SIZE", str(100 * 1024 * 1024)))  # 100MB
        self.enable_write = os.getenv("FS_ENABLE_WRITE", "true").lower() == "true"
        self.enable_delete = os.getenv("FS_ENABLE_DELETE", "false").lower() == "true"
    
    def _parse_paths(self, paths_str: str) -> List[str]:
        """Parse allowed paths from string."""
        if paths_str == "*":
            return ["*"]
        return [path.strip() for path in paths_str.split(",") if path.strip()]
    
    def _parse_extensions(self, extensions_str: str) -> List[str]:
        """Parse allowed extensions from string."""
        if extensions_str == "*":
            return ["*"]
        extensions = []
        for ext in extensions_str.split(","):
            ext = ext.strip()
            if ext and not ext.startswith("."):
                ext = "." + ext
            extensions.append(ext)
        return extensions
    
    def is_full_access_mode(self) -> bool:
        """Check if filesystem is in full access mode."""
        return "*" in self.allowed_paths
    
    def _is_path_allowed(self, file_path: Path) -> bool:
        """Check if path is allowed."""
        if "*" in self.allowed_paths:
            return True
        
        file_path = file_path.resolve()
        for allowed_path in self.allowed_paths:
            allowed_path = Path(allowed_path).resolve()
            try:
                file_path.relative_to(allowed_path)
                return True
            except ValueError:
                continue
        return False
    
    def _is_extension_allowed(self, file_path: Path) -> bool:
        """Check if file extension is allowed."""
        if "*" in self.allowed_extensions:
            return True
        
        return file_path.suffix.lower() in [ext.lower() for ext in self.allowed_extensions]
    
    def _validate_file_operation(self, file_path: Path, operation: str):
        """Validate file operation."""
        if not self._is_path_allowed(file_path):
            raise PermissionError(f"Access denied to path: {file_path}")

        # Only check extension for files, not directories
        # Skip extension check for directories or when path doesn't exist yet (for write operations)
        if (operation in ["read", "write"] and
            file_path.suffix and  # Has an extension
            (not file_path.exists() or file_path.is_file()) and  # Either doesn't exist yet or is a file
            not self._is_extension_allowed(file_path)):
            raise PermissionError(f"File extension not allowed: {file_path.suffix}")

        if operation == "write" and not self.enable_write:
            raise PermissionError("Write operations are disabled")

        if operation == "delete" and not self.enable_delete:
            raise PermissionError("Delete operations are disabled")
    
    def read_file(self, file_path: Union[str, Path]) -> str:
        """Read content from a file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, "read")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise IsADirectoryError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"File read successfully: {file_path} ({file_size} bytes)")
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            logger.info(f"File read successfully (latin-1): {file_path} ({file_size} bytes)")
            return content
    
    def write_file(self, file_path: Union[str, Path], content: str) -> None:
        """Write content to a file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, "write")
        
        # Check content size
        content_size = len(content.encode('utf-8'))
        if content_size > self.max_file_size:
            raise ValueError(f"Content too large: {content_size} bytes (max: {self.max_file_size})")
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"File written successfully: {file_path} ({content_size} bytes)")
    
    def list_directory(self, dir_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """List directory contents."""
        dir_path = Path(dir_path)
        self._validate_file_operation(dir_path, "read")
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
        
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        
        items = []
        for item in dir_path.iterdir():
            if self._is_path_allowed(item):
                try:
                    stat = item.stat()
                    items.append({
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': stat.st_size if item.is_file() else None,
                        'modified': stat.st_mtime,
                        'path': str(item)
                    })
                except (PermissionError, OSError) as e:
                    logger.warning(f"Cannot access {item}: {e}")
        
        logger.info(f"Directory listed successfully: {dir_path} ({len(items)} items)")
        return items
    
    def delete_file(self, file_path: Union[str, Path]) -> None:
        """Delete a file."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, "delete")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
        
        file_path.unlink()
        logger.info(f"File deleted successfully: {file_path}")
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get file information."""
        file_path = Path(file_path)
        self._validate_file_operation(file_path, "read")
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'path': str(file_path),
            'type': 'directory' if file_path.is_dir() else 'file',
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'permissions': oct(stat.st_mode)[-3:],
            'extension': file_path.suffix if file_path.is_file() else None
        }
