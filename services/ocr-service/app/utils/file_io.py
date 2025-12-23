"""
============================================================================
FILE: services/pdf-service/app/utils/file_io.py
PURPOSE: File I/O utilities for PDF operations
============================================================================
"""

from pathlib import Path
import tempfile
import shutil
from typing import List
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_temp_pdf_path(prefix: str = "output") -> Path:

    temp_file = tempfile.NamedTemporaryFile(
        mode='wb',
        delete=False,
        suffix='.pdf',
        prefix=f"{prefix}_",
        dir=settings.UPLOAD_DIR
    )
    temp_file.close()
    return Path(temp_file.name)


def safe_remove(path: Path) -> None:

    try:
        if path.exists():
            path.unlink()
            logger.debug(f"Removed temp file: {path}")
    except Exception as e:
        logger.warning(f"Failed to remove temp file {path}: {e}")

