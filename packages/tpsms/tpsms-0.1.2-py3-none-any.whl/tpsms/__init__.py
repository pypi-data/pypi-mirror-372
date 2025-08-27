# Remove proxy env vars if present
import os

for var in ["http_proxy", "https_proxy", "ftp_proxy", "all_proxy",
            "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY", "ALL_PROXY"]:
    os.environ.pop(var, None)