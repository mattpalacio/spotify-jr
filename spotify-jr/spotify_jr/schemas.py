from pydantic import BaseModel


class SpotifyCredentialBase(BaseModel):
    access_token: str
    token_type: str
    scope: str
    expires_in: int


class SpotifyCredentialRefresh(SpotifyCredentialBase):
    pass


class SpotifyCredential(SpotifyCredentialBase):
    refresh_token: str


class PlaybackStartIn(BaseModel):
    context_uri: str | None = None
    uris: list[str] | None = None
    offset: dict[str, int] | None = None
    position_ms: int = 0


class PlaybackTransferIn(BaseModel):
    device_ids: list[str]
    play: bool = True
