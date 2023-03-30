import base64
import json
from urllib.parse import urlencode

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from requests import post
from starlette.config import Config

from .. import config, dependencies, schemas

router = APIRouter(tags=["auth"])

scope = "streaming user-read-email user-read-private user-library-read user-library-modify user-read-playback-state user-modify-playback-state"

oauthConfig = Config(".env")
oauth = OAuth(oauthConfig)
settings = config.Settings()
oauth.register(
    name="spotify",
    access_token_url=settings.spotify_access_token_url,
    access_token_params=None,
    authorize_url=settings.spotify_auth_url,
    authorize_params=None,
    api_base_url=settings.spotify_api_url,
    client_kwargs={"scope": scope},
)


@router.get("/login")
async def login(
    # response: Response, settings: config.Settings = Depends(dependencies.get_settings)
    request: Request,
):
    # scope = "streaming user-read-email user-read-private user-library-read user-library-modify user-read-playback-state user-modify-playback-state"
    # query_string = urlencode(
    #     {
    #         "client_id": settings.spotify_client_id,
    #         "response_type": "code",
    #         "redirect_uri": settings.redirect_uri,
    #         "scope": scope,
    #     }
    # )
    # url = settings.spotify_auth_url + "?" + query_string
    # response = RedirectResponse(url=url)
    # return response
    redirect_uri = request.url_for("auth")
    return await oauth.spotify.authorize_redirect(request, redirect_uri)


@router.get(
    "/auth"
    # , response_model=schemas.SpotifyCredential
)
async def auth(
    # code: str, settings: config.Settings = Depends(dependencies.get_settings)
    request: Request,
):
    # url = settings.spotify_access_token_url

    # auth_string = settings.spotify_client_id + ":" + settings.spotify_client_secret
    # auth_bytes = auth_string.encode("utf-8")
    # auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    # headers = {
    #     "Authorization": "Basic " + auth_base64,
    #     "Content-Type": "application/x-www-form-urlencoded",
    # }

    # data = {
    #     "grant_type": "authorization_code",
    #     "code": code,
    #     "redirect_uri": settings.redirect_uri,
    # }

    # api_response = post(url, headers=headers, data=data)

    # if api_response.status_code >= 200 and api_response.status_code <= 299:
    #     data = json.loads(api_response.content)
    #     return data
    # else:
    #     error = json.loads(api_response.content)["error"]
    #     raise HTTPException(status_code=error["status"], detail=error["message"])
    token = await oauth.spotify.authorize_access_token(request)
    print("TOKEN", token)
    return token


@router.get("/refresh", response_model=schemas.SpotifyCredentialRefresh)
async def refresh(
    refresh_token: str, settings: config.Settings = Depends(dependencies.get_settings)
):
    url = settings.spotify_access_token_url

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
