import os
from typing import List


class Settings:
    def __init__(self) -> None:
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.jwt_secret: str = os.getenv("JWT_SECRET", os.urandom(32).hex())
        self.jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
        self.allowed_origins: List[str] = [
            origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",") if origin.strip()
        ]
        self.allow_open_admin_signup: bool = os.getenv("ALLOW_OPEN_ADMIN_SIGNUP", "false").lower() == "true"


settings = Settings()