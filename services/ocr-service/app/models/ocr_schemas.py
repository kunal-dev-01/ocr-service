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
        default=300,
        ge=150,
        le=600,
        description="DPI for OCR processing (150-600)"
    )



# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class OcrResponse(BaseModel):
    message: str
    pages_processed: int
    language: str
