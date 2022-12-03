from typing import Optional

from pydantic import BaseSettings


def in_container():
    """Returns: True iff running in a container"""
    with open("/proc/1/cgroup") as ifh:
        value = ifh.read()
        return "docker" in value or "kubepod" in value


class BaseConfig:
    env_file = ".env"
    secrets_dir: str | None = None


if in_container():
    BaseConfig.secrets_dir = "/run/secrets"


class Settings(BaseSettings):
    server: str
    username: str
    password: str
    ssl_ciphers: Optional[str] = None
    debug_file_watcher: bool = False
    imap_wait_timeout: int = 60

    class Config(BaseConfig):
        pass
