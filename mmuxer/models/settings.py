from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    server: str
    username: str
    password: str
    ssl_ciphers: Optional[str] = None
    debug_file_watcher: bool = False

    class Config:
        env_file = ".env"
        secrets_dir = "/run/secrets"
