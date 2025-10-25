from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mmuxer.models.common import BaseModel


def in_container():
    """Returns: True iff running in a container"""
    try:
        with open("/proc/1/cgroup") as ifh:
            value = ifh.read()
            return "docker" in value or "kubepod" in value
    except FileNotFoundError:
        return False


class SieveSettings(BaseModel):
    folder_prefix: str = ""  # folder prefix used when generating sieve rules
    folder_separator: str = "/"  # folder separator used when generating sieve rules
    name: str | None = None  # name used when exporting with managesieve
    extensions: list[str] = Field(default_factory=lambda: ["fileinto"])


class Settings(BaseModel, BaseSettings):
    server: str
    username: str
    password: str
    ssl_ciphers: Optional[str] = None
    imap_wait_timeout: int = 60

    sieve: SieveSettings = Field(default_factory=SieveSettings)

    model_config = SettingsConfigDict(
        env_file=".env", secrets_dir="/run/secrets" if in_container() else None
    )
