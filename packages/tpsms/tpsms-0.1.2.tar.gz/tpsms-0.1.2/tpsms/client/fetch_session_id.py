import requests
from urllib.parse import urlencode

async def fetch_session_id(base_url, encryption, sequence, username="admin", password=None):
    data = f"{username}\n{password}".encode("utf-8")

    encrypted = encryption["encrypt"](data, sequence, {
        "key": encryption["key"].decode("utf-8"),
        "iv": encryption["iv"].decode("utf-8"),
    })

    # Compute query parameters separately
    query_params = {
        'data': encrypted['data'],
        'sign': encrypted['sign'],
        'Action': '1',
        'LoginStatus': '0',
    }
    query_string = urlencode(query_params)
    url = f"{base_url.rstrip('/')}/cgi/login?{query_string}"

    response = requests.post(url, headers={"Referer": f"{base_url.rstrip('/')}/"})
    response.raise_for_status()

    set_cookie = response.headers.get("set-cookie")
    if set_cookie:
        start = set_cookie.find("=") + 1
        end = set_cookie.find(";", start)
        cookie_value = set_cookie[start:end]
        return cookie_value if cookie_value != "deleted" else None
    return None