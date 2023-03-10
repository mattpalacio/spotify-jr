import base64
import json
from functools import lru_cache

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from requests import post

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


@app.get("/authorize")
async def authorize(
    response: Response, settings: config.Settings = Depends(get_settings)
):
    scope = "user-library-read"
    url = settings.spotify_auth_url + "/authorize"
    query = f"?client_id={settings.spotify_client_id}&response_type=code&redirect_uri={settings.redirect_uri}&scope={scope}"
    response = RedirectResponse(url=url + query)
    return response


@app.get("/login")
async def login(
    request: Request,
    settings: config.Settings = Depends(get_settings),
):
    code = request.query_params["code"]

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
