import requests
from urllib.parse import urlencode


async def fetch_cgi_gdpr(base_url, payload, encryption, sequence, session_id, token_id, auth_times=1):
    """
    Send a POST request to the cgi_gdpr endpoint with an encrypted payload.

    Args:
        base_url (str): The base URL of the API.
        payload (str): Stringified actions to send.
        encryption (dict): Encryption object from authenticate.
        sequence (int): Sequence number for encryption.
        session_id (str): Session ID from authentication.
        token_id (str): Token ID from authentication.
        auth_times (int): Number of authentication attempts (default: 1).

    Returns:
        str: Decrypted response, or None if the request fails.
    """
    # Encrypt the payload
    encrypted = encryption["encrypt"](payload.encode("utf-8"), sequence)

    # Construct the request body
    body = f"sign={encrypted['sign']}\r\ndata={encrypted['data']}\r\n"

    # Send the POST request
    url = f"{base_url.rstrip('/')}/cgi_gdpr"
    headers = {
        "Referer": f"{base_url.rstrip('/')}/",
        "Cookie": f"loginErrorShow={auth_times};JSESSIONID={session_id}",  # No space after semicolon
        "TokenID": token_id,
        "Content-Type": "text/plain",
    }

    # print("Request URL:", url)
    # print("Request headers:", headers)
    # print("Request payload:", repr(payload))
    # print("Request body:", repr(body))
    # print("Sequence:", sequence)

    response = requests.post(url, headers=headers, data=body)

    # print("Response status:", response.status_code)
    # print("Response headers:", response.headers)
    # print("Response text:", repr(response.text))

    if response.status_code != 200:
        return None

    # Decrypt the response
    encrypted_response = response.text
    return encryption["decrypt"](encrypted_response)