import os
import random
import shutil
import string
from pathlib import Path
from typing import Optional

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)


class ResourceManager:
    """
    A utility class for managing folders and files for the project.

    This class provides functionality similar to tempfile but with a configurable
    root directory and better organization of project resources.
    """

    def __init__(self, root_dir: Optional[str] = None):
        """
        Initialize the ResourceManager.

        Args:
            root_dir: Optional custom root directory. If not provided, uses RESOURCE_ROOT from settings.
        """
        self.root_dir = Path(root_dir or settings.RESOURCE_ROOT)
        self._ensure_root_exists()
        self._created_dirs = []  # Track created directories for cleanup

    def _ensure_root_exists(self):
        """Ensure the root directory exists."""
        try:
            self.root_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Resource root directory ensured: {self.root_dir}")
        except Exception as e:
            logger.error(f"Failed to create resource root directory {self.root_dir}: {e}")
            raise

    def _generate_random_suffix(self, length: int = 8) -> str:
        """Generate a random suffix for directory names."""
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=length))

    def get_root_dir(self) -> Path:
        """
        Get the root directory path.

        Returns:
            Path object representing the root directory
        """
        return self.root_dir

    def create_temp_dir(self, prefix: str = "", suffix: str = "") -> Path:
        """
        Create a temporary directory with prefix and random postfix.

        Args:
            prefix: Prefix for the directory name (e.g., "flink_cdc_")
            suffix: Optional suffix for the directory name

        Returns:
            Path object representing the created directory

        Example:
            create_temp_dir("flink_cdc_") -> /tmp/flink_cdc_0aw8_0c5/
        """
        random_part = self._generate_random_suffix()
        dir_name = f"{prefix}{random_part}{suffix}"
        dir_path = self.root_dir / dir_name

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            self._created_dirs.append(dir_path)
            logger.debug(f"Created temporary directory: {dir_path}")
            return dir_path
        except Exception as e:
            logger.error(f"Failed to create temporary directory {dir_path}: {e}")
            raise

    def create_dir(self, name: str, create_parents: bool = True) -> Path:
        """
        Create a directory with a specific name (no random postfix).

        Args:
            name: Name of the directory to create (e.g., "logs", "configs")
            create_parents: Whether to create parent directories if they don't exist

        Returns:
            Path object representing the created directory

        Example:
            create_dir("logs") -> /tmp/logs/
        """
        dir_path = self.root_dir / name

        try:
            dir_path.mkdir(parents=create_parents, exist_ok=True)
            self._created_dirs.append(dir_path)
            logger.debug(f"Created directory: {dir_path}")
            return dir_path
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            raise

    def get_dir(self, name: str) -> Path:
        """
        Get a directory path without creating it.

        Args:
            name: Name of the directory

        Returns:
            Path object representing the directory (may not exist)
        """
        return self.root_dir / name

    def create_file_path(self, filename: str, subdir: Optional[str] = None) -> Path:
        """
        Create a file path within the resource root.

        Args:
            filename: Name of the file
            subdir: Optional subdirectory within the root

        Returns:
            Path object representing the file path

        Example:
            create_file_path("task.log", "logs") -> /tmp/logs/task.log
        """
        if subdir:
            dir_path = self.root_dir / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
            return dir_path / filename
        else:
            return self.root_dir / filename

    def cleanup_dir(self, dir_path: Path, force: bool = False):
        """
        Clean up a specific directory.

        Args:
            dir_path: Path to the directory to clean up
            force: If True, ignore errors during cleanup
        """
        if not dir_path.exists():
            return

        try:
            if dir_path.is_dir():
                shutil.rmtree(dir_path)
                logger.debug(f"Cleaned up directory: {dir_path}")
                # Remove from tracking list
                if dir_path in self._created_dirs:
                    self._created_dirs.remove(dir_path)
            else:
                logger.warning(f"Path is not a directory: {dir_path}")
        except Exception as e:
            error_msg = f"Failed to clean up directory {dir_path}: {e}"
            if force:
                logger.warning(error_msg)
            else:
                logger.error(error_msg)
                raise

    def cleanup_all(self, force: bool = True):
        """
        Clean up all directories created by this ResourceManager instance.

        Args:
            force: If True, ignore errors during cleanup
        """
        dirs_to_cleanup = self._created_dirs.copy()
        for dir_path in dirs_to_cleanup:
            try:
                self.cleanup_dir(dir_path, force=force)
            except Exception as e:
                if not force:
                    raise
                logger.warning(f"Error during cleanup of {dir_path}: {e}")

        if not dirs_to_cleanup:
            logger.debug("No directories to clean up")
        else:
            logger.info(f"Cleaned up {len(dirs_to_cleanup)} directories")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically cleanup."""
        self.cleanup_all(force=True)


_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    """Get the global ResourceManager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
