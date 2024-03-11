from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from mmuxer.models.common import BaseModel


def in_container():
    """Returns: True iff running in a container"""
    with open("/proc/1/cgroup") as ifh:
        value = ifh.read()
        return "docker" in value or "kubepod" in value


class Settings(BaseModel, BaseSettings):
    server: str
    username: str
    password: str
    ssl_ciphers: Optional[str] = None
    imap_wait_timeout: int = 60
    sieve_folder_prefix: str = ""  # folder prefix used when generating sieve rules
    sieve_folder_separator: str = "/"  # folder separator used when generating sieve rules
    fetch_batch_size: int = 100  # batch size used when fetching messages in bulk

    model_config = SettingsConfigDict(
        env_file=".env", secrets_dir="/run/secrets" if in_container() else None
    )
