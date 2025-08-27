from .client.fetch_info import fetch_info
from .client.fetch_public_key import fetch_public_key
from .client.encryption import create_encryption
from .client.fetch_busy import fetch_busy
from .client.fetch_session_id import fetch_session_id
from .client.fetch_token_id import fetch_token_id

async def authenticate(base_url, username="admin", password=None, force_login=True):
    info = await fetch_info(base_url)

    key_parameters = await fetch_public_key(base_url)
    sequence = key_parameters.pop("sequence")
    encryption = create_encryption(**key_parameters, username=username, password=password)

    busy_status = await fetch_busy(base_url)
    if busy_status["is_logged_in"] and not force_login:
        return None

    session_id = await fetch_session_id(
        base_url, encryption=encryption, sequence=sequence, username=username, password=password
    )
    if not session_id:
        return None

    token_id = await fetch_token_id(base_url, auth_times=info["authTimes"], session_id=session_id)

    return {
        "encryption": encryption,
        "sequence": sequence,
        "info": info,
        "session_id": session_id,
        "token_id": token_id,
    }