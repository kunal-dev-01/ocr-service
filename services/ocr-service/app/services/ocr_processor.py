from pathlib import Path
import fitz
import pytesseract
import numpy as np
import os
import shutil

from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# ============================================================================
# OCR LIMITS (Use settings where available)
# ============================================================================
OCR_MAX_PAGES = 40
OCR_MAX_SIZE_MB = 5
OCR_DEFAULT_DPI = 200
OCR_MIN_TEXT_THRESHOLD = 0.1 


def check_pdf_has_text(pdf_path: Path, threshold: float = OCR_MIN_TEXT_THRESHOLD) -> bool:

    try:
        doc = fitz.open(pdf_path)
        total_chars = 0
        
        for page in doc:
            text = page.get_text().strip()
            total_chars += len(text)
            
            # Early exit optimization
            if total_chars > 100:
                doc.close()
                logger.info("PDF has substantial text (>100 chars), skipping OCR")
                return True
        
        doc.close()
        
        avg_chars = total_chars / len(doc) if len(doc) > 0 else 0
        has_text = avg_chars >= (threshold * 100)
        
        if has_text:
            logger.info(f"PDF has text ({avg_chars:.1f} chars/page avg), skipping OCR")
        else:
            logger.info(f"PDF lacks text ({avg_chars:.1f} chars/page avg), OCR required")
        
        return has_text
        
    except Exception as e:
        logger.warning(f"Text check failed: {e}, proceeding with OCR")
        return False


def ocr_pdf_to_searchable(
    input_path: Path,
    output_path: Path,
    language: str = "eng",
    dpi: int = OCR_DEFAULT_DPI
) -> dict:

    try:
        # ========== FILE SIZE CHECK ==========
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        if file_size_mb > OCR_MAX_SIZE_MB:
            raise ValueError(
                f"PDF too large for OCR (max {OCR_MAX_SIZE_MB}MB, got {file_size_mb:.1f}MB)"
            )
        
        # ========== TEXT EXTRACTION CHECK (GOAL #1) ==========
        if check_pdf_has_text(input_path):
            # PDF already has text, just copy it
            shutil.copy(input_path, output_path)
            return {
                "pages_processed": 0,
                "ocr_skipped": True,
                "reason": "text_exists"
            }
        
        # ========== PAGE COUNT CHECK ==========
        input_doc = fitz.open(input_path)
        total_pages = len(input_doc)
        
        logger.info(f"OCR starting | pages={total_pages}, size={file_size_mb:.1f}MB, dpi={dpi}")
        
        if total_pages > OCR_MAX_PAGES:
            input_doc.close()
            raise ValueError(
                f"PDF has too many pages (max {OCR_MAX_PAGES}, got {total_pages})"
            )
        
        # ========== OCR PROCESSING ==========
        output_doc = fitz.open()
        
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        for page_num in range(total_pages):
            page = input_doc[page_num]
            
            # Render page to grayscale pixmap (GOAL #2)
            pix = page.get_pixmap(
                matrix=mat,
                alpha=False,
                colorspace=fitz.csGRAY 
            )
            
            # Convert to numpy array (faster than PNG encoding)
            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                pix.height, pix.width
            )
            
            # Run OCR
            ocr_pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                img_array,
                lang=language, 
                extension="pdf"
            )
            
            # Insert OCR page
            ocr_page = fitz.open("pdf", ocr_pdf_bytes)
            output_doc.insert_pdf(ocr_page)
            ocr_page.close()
            
            # ✅ Explicit memory cleanup
            pix = None
            img_array = None
            ocr_pdf_bytes = None
            
            logger.debug(f"OCR page {page_num + 1}/{total_pages}")
        
        input_doc.close()
        
        # Save with compression
        output_doc.save(output_path, garbage=4, deflate=True)
        output_doc.close()
        
        logger.info(f"OCR completed | pages={total_pages}")
        
        return {
            "pages_processed": total_pages,
            "ocr_skipped": False,
            "reason": None
        }
    
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise Exception(str(e))