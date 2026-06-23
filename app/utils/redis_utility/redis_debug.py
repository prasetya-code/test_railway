import socket
import traceback
from urllib.parse import urlparse


# =========================
# DEBUG: PARSE REDIS URL
# =========================
def debug_redis_url(url):
    try:
        parsed = urlparse(url)

        print("[REDIS DEBUG] Parsed URL:")
        print(f"  - scheme : {parsed.scheme}")
        print(f"  - host   : {parsed.hostname}")
        print(f"  - port   : {parsed.port}")
        print(f"  - db     : {parsed.path}")

    except Exception as e:
        print(f"[REDIS DEBUG ERROR] Failed to parse URL: {e}")
        traceback.print_exc()


# =========================
# DEBUG: CHECK PORT
# =========================
def debug_check_port(host, port):
    try:
        print(f"[REDIS DEBUG] Checking connection to {host}:{port} ...")

        s = socket.socket()
        s.settimeout(2)
        s.connect((host, port))

        print("[REDIS DEBUG] Port is OPEN ✅")
        s.close()

    except Exception as e:
        print(f"[REDIS DEBUG] Port is CLOSED ❌: {e}")
        traceback.print_exc()
