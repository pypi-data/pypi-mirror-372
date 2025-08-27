# TP-Link SMS Client

A Python package for interacting with SMS and USSD functionality on TP-Link routers, such as the TL-MR6400. This package allows you to send SMS messages, read messages (unread, received, sent, draft), retrieve SMS configuration, and send USSD codes via the router's API.

This project is a Python port of the node-tplink-api Node.js library, adapted for Python with asynchronous HTTP requests and special character encoding for compatibility with TP-Link routers.

## Features

- Authenticate with the TP-Link router's admin interface.
- Send SMS messages with proper encoding for newline (`\n`) and carriage return (`\r`) characters.
- Read SMS messages from various boxes (unread, received, sent, draft) with pagination support.
- Retrieve SMS configuration settings (e.g., enable status, service center number).
- Send and receive USSD codes (e.g., `*123#` for balance checks).

## Installation

### Prerequisites

- Python 3.7 or higher
- A TP-Link router with SMS/USSD support (e.g., TL-MR6400)
- Network access to the router (e.g., `http://192.168.1.1`)

### Install via pip

1. Clone the repository or download the package:

   ```bash
   git clone https://github.com/mosiiisom/tplink_sms.git
   cd tplink_sms
   ```

2. Install the package locally:

   ```bash
   pip install .
   ```

   For development, use editable mode:

   ```bash
   pip install -e .
   ```

### Dependencies

Listed in `requirements.txt`:

- `requests>=2.28.0`

If you use `aiohttp` for asynchronous HTTP requests, add:

- `aiohttp>=3.8.0`

Install dependencies manually if needed:

```bash
pip install -r requirements.txt
```

## Usage

The `TPLinkSMSClient` class provides a high-level interface for interacting with the router's SMS and USSD features. Below are example usage scenarios.

### Example: Basic Operations

```python
import asyncio
from tplink_sms.client import TPLinkSMSClient

async def main():
    # Initialize the client
    client = TPLinkSMSClient(
        base_url="http://192.168.1.1",
        password="your_router_password",
        username="admin"
    )

    # Get SMS configuration
    config = await client.get_sms_config()
    print("SMS Config:", config)

    # Get total number of unread messages
    total_unread = await client.get_total_messages("unread")
    print(f"Total Unread Messages: {total_unread}")

    # Read unread messages (first page)
    messages = await client.read_messages("unread", page_number=1)
    print("Unread Messages:", messages)

    # Send an SMS
    result = await client.send_sms("9123456789", "Hello,\nTest message.")
    print("Send SMS Result:", result)

    # Send a USSD code
    ussd_result = await client.send_ussd_code("*123#")
    print("USSD Result:", ussd_result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example: Reading All Messages with Pagination

```python
import asyncio
from tplink_sms.client import TPLinkSMSClient

async def main():
    client = TPLinkSMSClient(
        base_url="http://192.168.1.1",
        password="your_router_password"
    )

    # Read all received messages
    box_types = ["unread", "received", "sent", "draft"]
    page_size = 10  # Adjust based on router's page size
    for box_type in box_types:
        total = await client.get_total_messages(box_type)
        print(f"Total {box_type} messages: {total}")

        messages = []
        for page in range(1, (total // page_size) + 2):
            result = await client.read_messages(box_type, page_number=page)
            if result and result.get("error") == 0:
                for action in result.get("actions", []):
                    if action["req"][1].endswith("MSGENTRY"):
                        messages.extend(action["res"].get("attributes", []))
            print(f"{box_type.capitalize()} messages page {page}:", result)
        
        print(f"All {box_type} messages:", messages)

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

- **Base URL**: The router's IP address (e.g., `http://192.168.1.1`). Ensure your machine is on the same network.
- **Password**: The admin password for the router's web interface.
- **Username**: Typically `"admin"` (default for TP-Link routers).
- **Character Encoding**: The package automatically encodes newlines (`\n`) as `chr(18)` and carriage returns (`\r`) as `chr(17`) for SMS and USSD content, as required by the TL-MR6400.

## Notes

- **Authentication**: The client re-authenticates before each operation to ensure session validity. This is necessary due to the router's session timeout behavior.
- **Pagination**: The router may limit messages per page (default assumed to be 10). Adjust `page_size` if needed.
- **Error Handling**: Check the `error` field in API responses (`0` indicates success). Debug issues by enabling logging in `fetch_cgi_gdpr.py`.
## Contributing

Contributions are welcome! To contribute:

1. Fork the repository: `https://github.com/mosiiisom/tplink_sms`
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request.

Please include tests and update documentation as needed.

## Issues

Report bugs or feature requests at: https://github.com/mosiiisom/tplink_sms/issues

For sensitive issues, contact the maintainer via a private email (not the `noreply` address) or through GitHub Issues.

## License

MIT License