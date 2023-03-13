import base64
import json
from functools import lru_cache
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from requests import get, post

from . import config

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


@app.get("/")
async def home():
    return {"message": "Hello World"}


"""
Auth Endpoints
"""


@app.get("/authorize")
async def authorize(
    response: Response, settings: config.Settings = Depends(get_settings)
):
    scope = "user-library-read"
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


@app.get("/login")
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

    if api_response.status_code == 200:
        data = json.loads(api_response.content)

    return data


@app.get("/refresh")
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

    if api_response.status_code == 200:
        data = json.loads(api_response.content)

    return data


"""
Search Endpoint
"""


@app.get("/search")
async def search(
    request: Request,
    q: str,
    type: str,
    limit: int = 10,
    offset: int = 0,
    settings: config.Settings = Depends(get_settings),
):
    bearer_token = request.headers["authorization"]

    base_url = settings.spotify_api_url + "/search"
    query_string = urlencode({"q": q, "type": type, "limit": limit, "offset": offset})
    full_url = base_url + "?" + query_string

    headers = {"Authorization": bearer_token, "Content-Type": "application/json"}

    api_response = get(url=full_url, headers=headers)

    if api_response.status_code == 200:
        data = json.loads(api_response.content)

    return data
