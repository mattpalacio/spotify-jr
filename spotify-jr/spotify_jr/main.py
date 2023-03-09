import os
import base64
import json
from dotenv import load_dotenv
from requests import post, get
from fastapi import FastAPI

load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
auth_url = os.getenv("SPOTIFY_AUTH_URL")
api_url = os.getenv("SPOTIFY_API_URL")
redirect_uri = os.getenv("REDIRECT_URI")

app = FastAPI()


def get_code():
    scope = "user-library-read"

    url = auth_url + "/authorize"
    query = f"?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
    result = get(url + query)
    print(result)


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = auth_url + "/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_token_using_code(code: str):
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = auth_url + "/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = api_url + "/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None

    return json_result


@app.get("/")
async def home():
    get_code()
    return None


@app.get("/callback")
async def callback(code: str | None, state: str | None):
    token = get_token_using_code(code=code)
    print(token)
    return token


@app.get("/artists/{artist_name}")
async def get_artist(artist_name: str):
    token = get_token()
    artist = search_for_artist(token=token, artist_name=artist_name)
    return {"result": artist}
