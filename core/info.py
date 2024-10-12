import requests

from secretniy import base
from core.headers import headers


def get_info(token, proxies=None):
    url = "https://app.production.tonxdao.app/api/v1/profile"

    try:
        response = requests.get(
            url=url, headers=headers(token=token), proxies=proxies, timeout=20
        )
        data = response.json()
        dao_id = data["dao_id"]
        coins = data["coins"]
        energy = data["energy"]
        max_energy = data["max_energy"]

        base.log(
            f"{base.green}Balance: {base.white}{coins:,} - {base.green}Energy: {base.white}{energy} - {base.green}Max Energy: {base.white}{max_energy}"
        )
        return dao_id
    except:
        return None
