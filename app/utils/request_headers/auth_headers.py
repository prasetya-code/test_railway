"""
API Authentication Headers

Handles:

* Authorization
* X-API-Key

Purpose:

* Read authentication headers from incoming requests.
* Validate authentication credentials.
* Provide authentication context to the application.

Notes:

* This module does NOT write response headers.
* This module does NOT perform authorization (RBAC/permissions).
* This module only performs authentication.
"""

import traceback

from flask import request

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

AUTHORIZATION_REQUIRED = False

API_KEY_REQUIRED = False

EXPECTED_API_KEY = None

# ---------------------------------------------------------------------------
# AUTHORIZATION HEADER
# ---------------------------------------------------------------------------


def get_authorization_header():
    """
    Read Authorization header.

    Example:
        Authorization: Bearer <token>
    """

    try:
        value = request.headers.get("Authorization")

        return value

    except Exception:
        print("[ERROR][auth][authorization] failed reading Authorization header")

        traceback.print_exc()

        return None


# ---------------------------------------------------------------------------
# API KEY HEADER
# ---------------------------------------------------------------------------


def get_api_key_header():
    """
    Read X-API-Key header.

    Example:
        X-API-Key: abc123
    """

    try:
        value = request.headers.get("X-API-Key")

        return value

    except Exception:
        print("[ERROR][auth][api_key] failed reading X-API-Key header")

        traceback.print_exc()

        return None


# ---------------------------------------------------------------------------
# AUTHORIZATION VALIDATION
# ---------------------------------------------------------------------------


def validate_authorization():
    """
    Validate Authorization header exists.

    Token validation should be implemented
    separately (JWT, OAuth, etc).
    """

    try:
        if not AUTHORIZATION_REQUIRED:
            return True

        authorization = get_authorization_header()

        return bool(authorization)

    except Exception:
        print("[ERROR][auth][authorization] validation failed")

        traceback.print_exc()

        return False


# ---------------------------------------------------------------------------
# API KEY VALIDATION
# ---------------------------------------------------------------------------


def validate_api_key():
    """
    Validate X-API-Key header.
    """

    try:
        if not API_KEY_REQUIRED:
            return True

        api_key = get_api_key_header()

        if not api_key:
            return False

        if EXPECTED_API_KEY is None:
            return False

        return api_key == EXPECTED_API_KEY

    except Exception:
        print("[ERROR][auth][api_key] validation failed")

        traceback.print_exc()

        return False


# ---------------------------------------------------------------------------
# AUTHENTICATION
# ---------------------------------------------------------------------------


def authenticate_request():
    """
    Authenticate incoming request.

    Returns:
        bool
    """

    try:
        if not validate_authorization():
            return False

        if not validate_api_key():
            return False

        return True

    except Exception:
        print("[ERROR][auth] authentication failed")

        traceback.print_exc()

        return False
