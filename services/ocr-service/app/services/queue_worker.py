import asyncio
import time
import logging
from typing import Dict, Any
from pathlib import Path

from zemrev_queue import queue_manager
from app.services.ocr_processor import ocr_pdf_to_searchable

from app.core.config import settings
from app.utils.file_io import safe_remove

logger = logging.getLogger(__name__)

class QueueWorker:
    """Background worker for OCR processing"""
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.is_running = False
        self.jobs_processed = 0
    
    async def process_job(self, job_data: Dict[str, Any]) -> bool:
        """Process a single OCR job"""
        
        job_id = job_data["id"]
        job_type = job_data["type"]
        start_time = time.time()
        
        # Track files for cleanup
        pdf_path = None
        output_path = None
        
        try:
            logger.info(f"Worker {self.worker_id} processing {job_id} ({job_type})")
            
            task_data = job_data["data"]
            pdf_path = Path(task_data["pdf_path"])
            options = task_data.get("options", {})
            
            result = None
            
            # ================================================================
            # TOOL: PDF TO SEARCHABLE
            # ================================================================
            if job_type == "pdf-to-searchable":
                language = options.get("language", "eng")
                dpi = options.get("dpi", 200) 
                
                # Clamp DPI to safe range (in case frontend sends bad values)
                dpi = max(150, min(300, dpi)) 
                
                output_path = pdf_path.parent / f"{pdf_path.stem}_searchable.pdf"
                
                ocr_result = ocr_pdf_to_searchable(
                    pdf_path, 
                    output_path, 
                    language, 
                    dpi
                )
                
                result = {
                    "filename": output_path.name,
                    "output_path": str(output_path),
                    "pages_processed": ocr_result["pages_processed"],
                    "ocr_skipped": ocr_result["ocr_skipped"],
                    "skip_reason": ocr_result.get("reason"),
                    "language": language,
                    "dpi": dpi,
                    "processing_time": round(time.time() - start_time, 2)
                }
                
                logger.info(
                    f"Worker {self.worker_id} | {job_id} | "
                    f"Pages: {ocr_result['pages_processed']} | "
                    f"Skipped: {ocr_result['ocr_skipped']} | "
                    f"Time: {result['processing_time']}s"
                )
            
            else:
                raise ValueError(f"Unknown job type: {job_type}")
            
            # Complete job with result
            if result:
                await queue_manager.complete_job(job_id, result)
                self.jobs_processed += 1
                logger.info(f"Worker {self.worker_id} completed {job_id}")
                return True
            else:
                raise Exception("No result generated")
        
        except Exception as e:
            logger.error(f"Worker {self.worker_id} failed {job_id}: {e}")
            await queue_manager.fail_job(job_id, str(e))
            return False
        
        finally:
            # ✅ ADDED: Cleanup files after processing (success or failure)
            if pdf_path and pdf_path.exists():
                safe_remove(pdf_path)
                logger.debug(f"Cleaned up input: {pdf_path.name}")
            
    
    async def start(self):
        """Start worker loop"""
        
        self.is_running = True
        logger.info(f"Worker {self.worker_id} started")
        
        while self.is_running:
            try:
                job_data = await queue_manager.dequeue()
                
                if job_data:
                    await self.process_job(job_data)
                else:
                    # No jobs in queue, wait before checking again
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")
                await asyncio.sleep(5)  # Back off on errors
        
        logger.info(f"Worker {self.worker_id} stopped")
    
    async def stop(self):
        """Stop worker"""
        self.is_running = False


class WorkerManager:
    """Manage multiple workers"""
    
    def __init__(self):
        self.workers = []
        self.tasks = []
    
    async def start_workers(self, num_workers: int = 1):
        """Start workers"""
        
        logger.info(f"Starting {num_workers} OCR workers...")
        
        for i in range(num_workers):
            worker = QueueWorker(worker_id=i+1)
            self.workers.append(worker)
            
            task = asyncio.create_task(worker.start())
            self.tasks.append(task)
        
        logger.info(f"✅ {num_workers} workers started")
    
    async def stop_workers(self):
        """Stop all workers"""
        
        logger.info("Stopping workers...")
        
        for worker in self.workers:
            await worker.stop()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.workers.clear()
        self.tasks.clear()
        
        logger.info("✅ Workers stopped")


worker_manager = WorkerManager()