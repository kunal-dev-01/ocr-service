from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from concurrent.futures import ThreadPoolExecutor
import asyncio

from app.services.validator import validate_upload
from app.services.ocr_processor import ocr_pdf_to_searchable
from app.models.ocr_schemas import OcrPdfRequest
from app.utils.file_io import create_temp_pdf_path, safe_remove
from app.core.logging import get_logger

logger = get_logger(__name__)

# Thread pool for blocking OCR operations
executor = ThreadPoolExecutor(max_workers=2)


async def ocr_pdf_handler(
    file: UploadFile,
    request: OcrPdfRequest
) -> FileResponse:
    """Handle OCR PDF to searchable PDF."""
    input_path = None
    output_path = None

    try:
        input_path = await validate_upload(file)
        output_path = create_temp_pdf_path(prefix="ocr_searchable")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor,
            ocr_pdf_to_searchable,
            input_path,
            output_path,
            request.language,
            request.dpi
        )

        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="searchable.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if input_path:
            safe_remove(input_path)
