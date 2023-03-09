from pydantic import BaseSettings


class Settings(BaseSettings):
    spotify_client_id: str
    spotify_client_secret: str
    spotify_auth_url: str
    spotify_api_url: str
    redirect_url: str

    class Config:
        env_file = "../.env"
