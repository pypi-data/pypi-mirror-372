from .act import parse, stringify
from .client.fetch_cgi_gdpr import fetch_cgi_gdpr


async def execute(base_url, actions, encryption, sequence, session_id, token_id, auth_times=1):
    """
    Execute actions by sending a request to the cgi_gdpr endpoint and parsing the response.

    Args:
        base_url (str): The base URL of the API.
        actions (list): List of action tuples (type, oid, attributes, stack, pStack).
        encryption (dict): Encryption object from authenticate.
        sequence (int): Sequence number for encryption.
        session_id (str): Session ID from authentication.
        token_id (str): Token ID from authentication.
        auth_times (int): Number of authentication attempts (default: 1).

    Returns:
        dict: Parsed response with actions and optional error code.
    """
    payload = stringify(actions)

    response = await fetch_cgi_gdpr(
        base_url,
        payload,
        encryption=encryption,
        sequence=sequence,
        session_id=session_id,
        token_id=token_id,
        auth_times=auth_times
    )

    if response is None:
        return None

    result = parse(response)
    result["actions"] = [
        {
            "req": actions[item["action_index"]] if isinstance(item, dict) else actions[item[0]["action_index"]],
            "res": (
                [{k: v for k, v in d.items() if k != "action_index"} for d in item]
                if isinstance(item, list)
                else {k: v for k, v in item.items() if k != "action_index"} if item.get("attributes") else None
            )
        }
        for item in result["actions"]
    ]

    return result