import base64
import json
from functools import lru_cache
from requests import post, get
from fastapi import Depends, FastAPI, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
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


def get_token(settings: config.Settings):
    auth_string = settings.spotify_client_id + ":" + settings.spotify_client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = settings.spotify_auth_url + "/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_token_using_code(code: str, settings: config.Settings):
    auth_string = settings.spotify_client_id + ":" + settings.spotify_client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = settings.spotify_auth_url + "/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.redirect_uri,
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name, settings: config.Settings):
    url = settings.spotify_api_url + "/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None

    return json_result


@app.get("/login")
async def home(response: Response, settings: config.Settings = Depends(get_settings)):
    scope = "user-library-read"
    url = settings.spotify_auth_url + "/authorize"
    query = f"?client_id={settings.spotify_client_id}&response_type=code&redirect_uri={settings.redirect_uri}&scope={scope}"
    response = RedirectResponse(url=url + query)
    return response


@app.get("/callback")
async def callback(
    code: str | None,
    request: Request,
    settings: config.Settings = Depends(get_settings),
):
    code = request.query_params["code"]
    token = get_token_using_code(code=code, settings=settings)
    print(token)
    return token
