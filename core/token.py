import requests

from secretniy import base
from core.headers import headers


def get_token(data, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/login/web-app"
    payload = {"initData": data}

    try:
        response = requests.post(
            url=url, headers=headers(), json=payload, proxies=proxies, timeout=20
        )
        data = response.json()
        token = data["access_token"]
        return token
    except:
        return None


def get_centrifugo_token(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/centrifugo-token"

    try:
        response = requests.get(
            url=url, headers=headers(token=token), proxies=proxies, timeout=20
        )
        data = response.json()
        token = data["token"]
        return token
    except:
        return None
