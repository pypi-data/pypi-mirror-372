import requests

MARKER = '<script type="text/javascript">'

async def fetch_info(base_url):
    url = f"{base_url.rstrip('/')}/"
    response = requests.get(url, headers={"Referer": url})
    response.raise_for_status()

    html = response.text
    js = html[html.rindex(MARKER) + len(MARKER):-9]

    entries = [
        line.split("=", 1)
        for line in (s.strip()[4:] for s in js.split(";") if s.strip())
    ]
    return {k: eval(v) for k, v in entries}  # Note: eval is used for simplicity; consider safer parsing for production