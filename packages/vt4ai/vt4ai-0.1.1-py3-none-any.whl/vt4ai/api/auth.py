from typing import Annotated

from fastapi import Header, HTTPException


def get_api_key(x_apikey: Annotated[str | None, Header()] = None) -> str:
    """Extract and validate API key from headers."""
    if not x_apikey:
        raise HTTPException(status_code=401, detail="API key required in x-apikey header")
    return x_apikey
