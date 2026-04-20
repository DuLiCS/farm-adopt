import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://farm_user:farm_pass_123@localhost/farm_adopt")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "farm2026")
    # 逗号分隔的允许跨域来源列表，例如: http://150.158.24.148,https://example.com
    ALLOWED_ORIGINS: list[str] = [
        o.strip() for o in os.getenv(
            "ALLOWED_ORIGINS",
            "http://150.158.24.148,http://localhost:5173,http://localhost:3000"
        ).split(",") if o.strip()
    ]

settings = Settings()