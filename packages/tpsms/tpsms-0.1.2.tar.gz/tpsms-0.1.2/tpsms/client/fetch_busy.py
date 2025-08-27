import requests


async def fetch_busy(base_url):
    url = f"{base_url.rstrip('/')}/cgi/getBusy"
    response = requests.post(url, headers={"Referer": f"{base_url.rstrip('/')}/"})
    response.raise_for_status()

    js = response.text
    is_logged_in_line, is_busy_line,_ = [line.strip() for line in js.split("\n") if line.strip()]

    return {
        "is_logged_in": bool(int(is_logged_in_line[14:-1])),
        "is_busy": bool(int(is_busy_line[11:-1])),
    }