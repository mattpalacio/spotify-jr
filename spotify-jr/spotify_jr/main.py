import base64
import json
from functools import lru_cache
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from requests import get, post, put

from . import config, schemas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache()
def get_settings():
    return config.Settings()


@app.get("/authorize", tags=["auth"])
async def authorize(
    response: Response, settings: config.Settings = Depends(get_settings)
):
    scope = "streaming user-read-email user-read-private user-library-read user-library-modify user-read-playback-state user-modify-playback-state"
    base_url = settings.spotify_auth_url + "/authorize"
    query_string = urlencode(
        {
            "client_id": settings.spotify_client_id,
            "response_type": "code",
            "redirect_uri": settings.redirect_uri,
            "scope": scope,
        }
    )
    full_url = base_url + "?" + query_string
    response = RedirectResponse(url=full_url)
    return response


@app.get("/login", response_model=schemas.SpotifyCredential, tags=["auth"])
async def login(code: str, settings: config.Settings = Depends(get_settings)):
    url = settings.spotify_auth_url + "/api/token"

    auth_string = settings.spotify_client_id + ":" + settings.spotify_client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.redirect_uri,
    }

    api_response = post(url, headers=headers, data=data)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        data = json.loads(api_response.content)
        return data
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.get("/refresh", response_model=schemas.SpotifyCredentialRefresh, tags=["auth"])
async def refresh(
    refresh_token: str, settings: config.Settings = Depends(get_settings)
):
    url = settings.spotify_auth_url + "/api/token"

    auth_string = settings.spotify_client_id + ":" + settings.spotify_client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    api_response = post(url, headers=headers, data=data)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        data = json.loads(api_response.content)
        return data
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.get("/search", tags=["search"])
async def search(
    request: Request,
    q: str,
    type: str,
    limit: int = Query(default=10, g=0, le=50),
    offset: int = Query(default=0, g=0, le=1000),
    settings: config.Settings = Depends(get_settings),
):
    bearer_token = request.headers["authorization"]

    base_url = settings.spotify_api_url + "/search"
    query_string = urlencode({"q": q, "type": type, "limit": limit, "offset": offset})
    full_url = base_url + "?" + query_string

    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    api_response = get(url=full_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        data = json.loads(api_response.content)
        return data
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.put("/player", status_code=204, tags=["player"])
async def transfer_playback(
    request: Request,
    playback: schemas.PlaybackTransferIn,
    settings: config.Settings = Depends(get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player"
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    json_data = {"device_ids": playback.device_ids, "play": playback.play}

    api_response = put(url=base_url, headers=headers, json=json_data)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        return None
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.get("/player/devices", tags=["player"])
async def get_devices(
    request: Request, settings: config.Settings = Depends(get_settings)
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/devices"
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    api_response = get(url=base_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        data = json.loads(api_response.content)
        return data
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.get("/player/currently-playing", tags=["player"])
async def get_currently_playing(
    request: Request, settings: config.Settings = Depends(get_settings)
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/currently-playing"
    query_string = urlencode({"additional_types": "track,episode", "market": "US"})
    full_url = base_url + "?" + query_string
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    api_response = get(url=full_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        data = json.loads(api_response.content)
        return data
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.put("/player/play", status_code=204, tags=["player"])
async def start_playback(
    request: Request,
    device_id: str,
    playback: schemas.PlaybackStartIn,
    settings: config.Settings = Depends(get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/play"
    query_string = urlencode({"device_id": device_id})
    full_url = base_url + "?" + query_string
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }
    json_data = {"uris": playback.uris, "position_ms": playback.position_ms}

    api_response = put(url=full_url, headers=headers, json=json_data)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        return None
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@app.put("/player/pause", status_code=204, tags=["player"])
async def pause_playback(
    request: Request,
    device_id: str,
    settings: config.Settings = Depends(get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/pause"
    query_string = urlencode({"device_id": device_id})
    full_url = base_url + "?" + query_string
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    api_response = put(url=full_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        return None
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])
