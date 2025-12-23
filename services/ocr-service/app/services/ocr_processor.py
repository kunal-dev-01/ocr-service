from pathlib import Path
import fitz  
from PIL import Image
import pytesseract
import io
import os

from app.core.logging import get_logger

logger = get_logger(__name__)

# ============================================================================
# OCR HARD LIMITS
# ============================================================================
OCR_MAX_PAGES = 40
OCR_MAX_SIZE_MB = 10
OCR_FIXED_DPI = 300
OCR_LANGUAGE = "eng"


def ocr_pdf_to_searchable(
    input_path: Path,
    output_path: Path,
    language: str = OCR_LANGUAGE,
    dpi: int = OCR_FIXED_DPI
) -> int:

    try:
        # ---------------- File size check ----------------
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        if file_size_mb > OCR_MAX_SIZE_MB:
            raise ValueError(
                f"OCR supports max {OCR_MAX_SIZE_MB} MB PDFs (got {file_size_mb:.1f} MB)"
            )

        # ---------------- Open PDF ----------------
        input_doc = fitz.open(input_path)
        total_pages = len(input_doc)

        logger.info(f"OCR started | pages={total_pages}, size={file_size_mb:.1f}MB")

        # ---------------- Page limit check ----------------
        if total_pages > OCR_MAX_PAGES:
            input_doc.close()
            raise ValueError(
                f"OCR supports max {OCR_MAX_PAGES} pages (got {total_pages})"
            )

        output_doc = fitz.open()

        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)

        # ---------------- OCR per page ----------------
        for page_num in range(total_pages):
            page = input_doc[page_num]

            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            ocr_pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                img,
                lang=OCR_LANGUAGE,
                extension="pdf"
            )

            ocr_page = fitz.open("pdf", ocr_pdf_bytes)
            output_doc.insert_pdf(ocr_page)
            ocr_page.close()

            logger.debug(f"OCR page {page_num + 1}/{total_pages}")

        input_doc.close()

        output_doc.save(output_path, garbage=4, deflate=True)
        output_doc.close()

        logger.info(f"OCR completed | pages={total_pages}")
        return total_pages

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        raise Exception(str(e))
