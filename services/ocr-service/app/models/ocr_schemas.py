from pydantic import BaseModel, Field
from typing import Optional


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class OcrPdfRequest(BaseModel):

    language: str = Field(
        default="eng",
        description="OCR language code (eng, fra, deu, spa, etc.)"
    )
    dpi: int = Field(
        default=200,
        ge=150,
        le=300, 
        description="DPI for OCR processing (150-300)"
    )


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class OcrResponse(BaseModel):
    """OCR processing result"""
    message: str
    pages_processed: int
    language: str
    ocr_skipped: bool = Field(
        default=False,
        description="True if PDF already had text (OCR was skipped)"
    )