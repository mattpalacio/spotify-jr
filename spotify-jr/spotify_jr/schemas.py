from pydantic import BaseModel


class SpotifyCredentialBase(BaseModel):
    access_token: str
    token_type: str
    scope: str
    expires_in: int


class SpotifyCredentialRefresh(SpotifyCredentialBase):
    pass

    class Config:
        orm_mode = True


class SpotifyCredential(SpotifyCredentialBase):
    refresh_token: str

    class Config:
        orm_mode = True
