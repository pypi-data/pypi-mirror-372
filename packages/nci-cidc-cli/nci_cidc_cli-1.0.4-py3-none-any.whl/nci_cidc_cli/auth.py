import base64
import json

import click

from . import api
from . import cache


TOKEN = "id_token"


class AuthError(click.ClickException):
    pass


def unauthenticated() -> AuthError:
    return AuthError(
        "You are not authenticated. Please login with:\n"
        "   $ nci-cidc login [YOUR PORTAL TOKEN]"
    )


def validate_token(id_token: str):
    """
    Raises AuthError if id_token is not valid
    """
    try:
        error = api.check_auth(id_token)
    except api.ApiError as e:
        raise AuthError(str(e))


def validate_and_cache_token(id_token: str):
    """
    If a token is valid, cache it for use in future commands.
    """
    # Validate the id token
    validate_token(id_token)

    # Save the provided token
    cache.store(TOKEN, id_token)


def get_id_token() -> str:
    """
    Look for a cached id_token for this user. If no token is cached,
    exit and prompt the user to log in. Otherwise, return the cached token.
    """
    # Try to find a cached token
    id_token = cache.get(TOKEN)

    # If there's no cached token, the user needs to log in
    if not id_token:
        raise unauthenticated()

    return id_token


def get_user_email() -> str:
    """Extract a user's email from their id token."""
    token = get_id_token()

    try:
        encoded_parts = token.split(".")
        encoded_claims = encoded_parts[1]
        decoded_claims = base64.b64decode(encoded_claims.encode("utf-8") + b"==")
    except Exception:
        raise unauthenticated()

    return json.loads(decoded_claims)["email"]
