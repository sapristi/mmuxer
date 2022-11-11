from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    server: str
    username: str
    password: str = Field(..., env="password")

    class Config:
        env_file = ".env"
