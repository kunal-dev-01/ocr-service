from pathlib import Path
from fastapi import UploadFile, HTTPException
import tempfile
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def validate_upload(file: UploadFile) -> Path:

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected .pdf, got: {file.filename}"
        )
    
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max: {max_mb:.1f}MB, got: {actual_mb:.1f}MB"
        )
    
    if not content.startswith(b'%PDF-'):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file (missing PDF header)"
        )
    
    try:
        temp_file = tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False,
            suffix='.pdf',
            dir=settings.UPLOAD_DIR
        )
        temp_file.write(content)
        temp_file.close()
        
        temp_path = Path(temp_file.name)
        logger.info(f"Validated and saved file: {file.filename} ({file_size} bytes) -> {temp_path}")
        
        return temp_path
        
    except Exception as e:
        logger.error(f"Failed to save temporary file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")