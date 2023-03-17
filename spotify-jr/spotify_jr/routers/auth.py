import base64
import json
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from requests import post

from .. import config, dependencies, schemas

router = APIRouter(tags=["auth"])


@router.get(
    "/authorize",
)
async def authorize(
    response: Response, settings: config.Settings = Depends(dependencies.get_settings)
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


@router.get("/login", response_model=schemas.SpotifyCredential)
async def login(
    code: str, settings: config.Settings = Depends(dependencies.get_settings)
):
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


@router.get("/refresh", response_model=schemas.SpotifyCredentialRefresh)
async def refresh(
    refresh_token: str, settings: config.Settings = Depends(dependencies.get_settings)
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
