import asyncio
from .authenticate import authenticate
from .execute import execute
from .act import ACT

def do_escape_char_encode(text):
    """
    Encode newline and carriage return characters in a string.
    Replaces '\n' with chr(18) and '\r' with chr(17).
    """
    result = ""
    for char in text:
        if char == "\n":
            result += chr(18)
        elif char == "\r":
            result += chr(17)
        else:
            result += char
    return result

def do_escape_char_decode(text):
    """
    Decode newline and carriage return characters in a string.
    Replaces chr(18) with '\n' and chr(17) with '\r'.
    """
    result = ""
    for char in text:
        if char == chr(18):
            result += "\n"
        elif char == chr(17):
            result += "\r"
        else:
            result += char
    return result

class TPLinkSMSClient:
    def __init__(self, base_url, password, username="admin"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.context = None
        self.info = None

    async def authenticate(self):
        """Authenticate with the router and update context."""
        auth_result = await authenticate(self.base_url, password=self.password, username=self.username)
        if auth_result is None:
            raise Exception("Authentication failed")
        self.info = auth_result["info"]
        self.context = {k: v for k, v in auth_result.items() if k != "info"}
        return self.info

    async def get_sms_config(self):
        """Get SMS configuration settings."""
        await self.authenticate()
        actions = [
            (
                ACT.GET,
                "LTE_SMS_CONFIG",
                ["enable", "centerNumber"],
                "0,0,0,0,0,0",
                "0,0,0,0,0,0"
            )
        ]
        return await execute(
            self.base_url,
            actions,
            encryption=self.context["encryption"],
            sequence=self.context["sequence"],
            session_id=self.context["session_id"],
            token_id=self.context["token_id"],
            auth_times=self.info["authTimes"]
        )

    async def get_total_messages(self, box_type):
        """Get the total number of messages in a specified SMS box."""
        oid_map = {
            "unread": "LTE_SMS_UNREADMSGBOX",
            "received": "LTE_SMS_RECVMSGBOX",
            "sent": "LTE_SMS_SENDMSGBOX",
            "draft": "LTE_SMS_DRAFTMSGBOX"
        }
        await self.authenticate()
        actions = [
            (
                ACT.GET,
                oid_map[box_type],
                ["totalNumber"],
                "0,0,0,0,0,0",
                "0,0,0,0,0,0"
            )
        ]
        result = await execute(
            self.base_url,
            actions,
            encryption=self.context["encryption"],
            sequence=self.context["sequence"],
            session_id=self.context["session_id"],
            token_id=self.context["token_id"],
            auth_times=self.info["authTimes"]
        )
        if result and result.get("error") == 0:
            for action in result.get("actions", []):
                if action["req"][1] == oid_map[box_type]:
                    return int(action["res"]["attributes"].get("totalNumber", 0))
        return 0

    async def read_messages(self, box_type, page_number=1):
        """Read messages from a specified SMS box for a specific page."""
        oid_map = {
            "unread": ("LTE_SMS_UNREADMSGBOX", "LTE_SMS_UNREADMSGENTRY"),
            "received": ("LTE_SMS_RECVMSGBOX", "LTE_SMS_RECVMSGENTRY"),
            "sent": ("LTE_SMS_SENDMSGBOX", "LTE_SMS_SENDMSGENTRY"),
            "draft": ("LTE_SMS_DRAFTMSGBOX", "LTE_SMS_DRAFTMSGENTRY")
        }
        await self.authenticate()
        box_oid, entry_oid = oid_map[box_type]
        actions = [
            (
                ACT.SET,
                box_oid,
                {"pageNumber": page_number},
                "0,0,0,0,0,0",
                "0,0,0,0,0,0"
            ),
            (
                ACT.GS,
                entry_oid,
                ["index", "from", "content", "receivedTime", "unread"],
                "0,0,0,0,0,0",
                "0,0,0,0,0,0"
            )
        ]
        result = await execute(
            self.base_url,
            actions,
            encryption=self.context["encryption"],
            sequence=self.context["sequence"],
            session_id=self.context["session_id"],
            token_id=self.context["token_id"],
            auth_times=self.info["authTimes"]
        )
        if result and result.get("error") == 0:
            for action in result.get("actions", []):
                if action["req"][1] == entry_oid:
                    for entry in action["res"].get("attributes", []):
                        if "content" in entry:
                            entry["content"] = do_escape_char_decode(entry["content"])
        return result

    async def send_sms(self, to, message):
        """Send an SMS message."""
        await self.authenticate()
        encoded_message = do_escape_char_encode(message)
        actions = [
            (
                ACT.SET,
                "LTE_SMS_SENDNEWMSG",
                ["index=1", f"to={to}", f"textContent={encoded_message}"],
                "0,0,0,0,0,0",
                "0,0,0,0,0,0"
            )
        ]
        return await execute(
            self.base_url,
            actions,
            encryption=self.context["encryption"],
            sequence=self.context["sequence"],
            session_id=self.context["session_id"],
            token_id=self.context["token_id"],
            auth_times=self.info["authTimes"]
        )

    async def send_ussd_code(self, ussd_code):
        """Send a USSD code and retrieve the response."""
        await self.authenticate()
        encoded_code = do_escape_char_encode(ussd_code)
        actions = [
            (
                ACT.SET,
                "LTE_USSD",
                [f"ussdContent={encoded_code}"],
                "0,0,0,0,0,0",
                "0,0,0,0,0,0"
            )
        ]
        result = await execute(
            self.base_url,
            actions,
            encryption=self.context["encryption"],
            sequence=self.context["sequence"],
            session_id=self.context["session_id"],
            token_id=self.context["token_id"],
            auth_times=self.info["authTimes"]
        )
        if result and result.get("error") == 0:
            for action in result.get("actions", []):
                if action["req"][1] == "LTE_USSD":
                    for entry in action["res"].get("attributes", []):
                        if "ussdContent" in entry:
                            entry["ussdContent"] = do_escape_char_decode(entry["ussdContent"])
        return result