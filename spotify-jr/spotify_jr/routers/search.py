import json
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from requests import get

from .. import config, dependencies

router = APIRouter(tags=["search"])


@router.get("/search")
async def search(
    q: str,
    type: str,
    limit: int = Query(default=10, g=0, le=50),
    offset: int = Query(default=0, g=0, le=1000),
    authorization: str = Header(),
    settings: config.Settings = Depends(dependencies.get_settings),
):

    base_url = settings.spotify_api_url + "/search"
    query_string = urlencode({"q": q, "type": type, "limit": limit, "offset": offset})
    full_url = base_url + "?" + query_string

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    api_response = get(url=full_url, headers=headers)

    if api_response.status_code >= 200 and api_response.status_code <= 299:
        data = json.loads(api_response.content)
        return data
    else:
        error = json.loads(api_response.content)["error"]
        raise HTTPException(status_code=error["status"], detail=error["message"])
