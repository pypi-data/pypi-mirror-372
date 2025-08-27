from datetime import timedelta

import httpx
from cachetools import TTLCache, cached


@cached(cache=TTLCache(
    maxsize=1_000,
    ttl=timedelta(hours=1).seconds,
))
def get_username(bearer_token: str) -> str:
    # https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api
    return httpx.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {bearer_token}",
        },
    ).json()["login"]
