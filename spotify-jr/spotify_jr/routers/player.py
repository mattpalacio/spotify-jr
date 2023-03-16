import json
from enum import Enum
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from requests import get, post, put

from .. import config, dependencies, schemas


class RepeatMode(str, Enum):
    track = "track"
    context = "context"
    off = "off"


router = APIRouter(tags=["player"])


@router.put("/player", status_code=204, tags=["player"])
async def transfer_playback(
    request: Request,
    playback: schemas.PlaybackTransferIn,
    settings: config.Settings = Depends(dependencies.get_settings),
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


@router.get("/player/devices", tags=["player"])
async def get_devices(
    request: Request, settings: config.Settings = Depends(dependencies.get_settings)
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


@router.get("/player/currently-playing", tags=["player"])
async def get_currently_playing(
    request: Request, settings: config.Settings = Depends(dependencies.get_settings)
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


@router.post("/player/next", status_code=204, tags=["player"])
async def skip_to_next(
    request: Request,
    device_id: str,
    settings: config.Settings = Depends(dependencies.get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/next"
    query_string = urlencode({"device_id": device_id})
    full_url = base_url + "?" + query_string
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    api_response = post(url=full_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        return None
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@router.post("/player/previous", status_code=204, tags=["player"])
async def skip_to_previous(
    request: Request,
    device_id: str,
    settings: config.Settings = Depends(dependencies.get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/previous"
    query_string = urlencode({"device_id": device_id})
    full_url = base_url + "?" + query_string
    headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }

    api_response = post(url=full_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        return None
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])


@router.put("/player/play", status_code=204, tags=["player"])
async def start_playback(
    request: Request,
    device_id: str,
    playback: schemas.PlaybackStartIn,
    settings: config.Settings = Depends(dependencies.get_settings),
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


@router.put("/player/pause", status_code=204, tags=["player"])
async def pause_playback(
    request: Request,
    device_id: str,
    settings: config.Settings = Depends(dependencies.get_settings),
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


@router.put("/player/repeat", status_code=204, tags=["player"])
async def set_repeat_mode(
    request: Request,
    state: RepeatMode,
    device_id: str,
    settings: config.Settings = Depends(dependencies.get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/repeat"
    query_string = urlencode({"state": state, "device_id": device_id})
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


@router.put("/player/shuffle", status_code=204, tags=["player"])
async def toggle_shuffle(
    request: Request,
    state: bool,
    device_id: str,
    settings: config.Settings = Depends(dependencies.get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/shuffle"
    query_string = urlencode({"state": state, "device_id": device_id})
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


@router.put("/player/seek", status_code=204, tags=["player"])
async def seek_to_position(
    request: Request,
    position_ms: int,
    device_id: str,
    settings: config.Settings = Depends(dependencies.get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/seek"
    query_string = urlencode({"position_ms": position_ms, "device_id": device_id})
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


@router.put("/player/volume", status_code=204, tags=["player"])
async def set_playback_volume(
    request: Request,
    device_id: str,
    volume_percent: int = Query(ge=0, le=100),
    settings: config.Settings = Depends(dependencies.get_settings),
):
    bearer_token = request.headers["authorization"]
    base_url = settings.spotify_api_url + "/me/player/pause"
    query_string = urlencode({"volume_percent": volume_percent, "device_id": device_id})
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
