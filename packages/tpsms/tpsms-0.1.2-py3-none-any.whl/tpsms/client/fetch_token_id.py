import requests
import re

async def fetch_token_id(base_url, auth_times=1, session_id=None):
    url = f"{base_url.rstrip('/')}/"
    response = requests.get(
        url,
        headers={
            "Referer": url,
            "Cookie": f"loginErrorShow={auth_times}; JSESSIONID={session_id}",
        },
    )


    response.raise_for_status()

    html = response.text

    match = re.search(r'var token="([^"]*)"', html)
    if match:
        return match.group(1)
    return None