"""
============================================================================
FILE: services/pdf-service/app/api/routes/ocr_routes.py
PURPOSE: API routes for OCR operations
============================================================================
"""

from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse

from app.api.controllers.ocr_controller import ocr_pdf_handler
from app.models.ocr_schemas import OcrPdfRequest

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR Tools"])


@router.post("/pdf-to-searchable", response_class=FileResponse)
async def ocr_pdf_endpoint(
    file: UploadFile = File(..., description="Scanned/image-based PDF"),
    language: str = Form(default="eng", description="OCR language (eng, fra, deu, spa, etc.)"),
    dpi: int = Form(default=300, ge=150, le=600, description="DPI for OCR (150-600)")
) -> FileResponse:
    request = OcrPdfRequest(language=language, dpi=dpi)
    return await ocr_pdf_handler(file, request)
