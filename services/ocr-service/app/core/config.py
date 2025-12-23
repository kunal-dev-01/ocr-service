from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

class Settings(BaseSettings):
    # ========================================================================
    # SERVICE CONFIG ONLY (Queue config handled by zemrev-queue package)
    # ========================================================================
    
    WORKERS: int = 1
    LOG_LEVEL: str = "info"
    HOST: str = "0.0.0.0"
    PORT: int = 8004
    ALLOWED_ORIGINS: str = "https://www.zemrev.com,https://zemrev.com,https://api.zemrev.com,http://api.zemrev.com/"
    UPLOAD_DIR: str = "/tmp/zemrev_ocr_uploads"
    
    # ========================================================================
    # TOOL-SPECIFIC LIMITS
    # ========================================================================
    
    MAX_FILE_SIZE: int = 10485760           # 25MB
    MAX_PAGES: int = 40
    TOOL_TIMEOUT: int = 600                 # 10 minutes
    
    # ========================================================================
    # QUEUE-RELATED (Service uses this, .env provides value)
    # ========================================================================
    
    QUEUE_MAX_WORKERS: int = 1
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    def get_allowed_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]
    
    def ensure_upload_dir(self):
        """Create upload directory if it doesn't exist"""
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_upload_dir()