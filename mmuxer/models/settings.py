from pydantic import BaseSettings


class Settings(BaseSettings):
    server: str
    username: str
    password: str

    class Config:
        env_file = ".env"
