import requests

def _extract_variables(js):
    result = {"exponent": "", "modulus": "", "sequence": ""}
    for line in (line.strip() for line in js.split("\n") if line.strip()):
        if line.startswith("var ee="):
            result["exponent"] = line[8:-2]
        elif line.startswith("var nn="):
            result["modulus"] = line[8:-2]
        elif line.startswith("var seq="):
            result["sequence"] = line[9:-2]
    return result

async def fetch_public_key(base_url):
    url = f"{base_url.rstrip('/')}/cgi/getParm"
    response = requests.post(url, headers={"Referer": f"{base_url.rstrip('/')}/"})
    response.raise_for_status()

    js = response.text
    variables = _extract_variables(js)
    #
    # print("Modulus:", variables["modulus"])
    # print("Exponent:", variables["exponent"])
    # print("Sequence:", variables["sequence"])

    return {
        "exponent": bytes.fromhex(variables["exponent"]),
        "modulus": bytes.fromhex(variables["modulus"]),
        "sequence": int(variables["sequence"]),
    }