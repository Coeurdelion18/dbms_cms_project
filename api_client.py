import os
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = 15


class APIError(RuntimeError):
    pass


def _auth_headers():
    try:
        import streamlit as st
    except ImportError:
        return {}

    token = st.session_state.get("access_token")
    if not token:
        return {}

    return {"Authorization": f"Bearer {token}"}


def request(method, path, **kwargs):
    payload = kwargs.get("json")
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Content-Type": "application/json",
        **_auth_headers(),
    }
    http_request = Request(
        f"{API_BASE_URL}{path}",
        data=data,
        method=method,
        headers=headers,
    )

    try:
        with urlopen(http_request, timeout=REQUEST_TIMEOUT) as response:
            content = response.read()
    except HTTPError as exc:
        content = exc.read()
        try:
            body = json.loads(content)
            detail = body.get("detail", body) if isinstance(body, dict) else body
        except (ValueError, TypeError):
            detail = content.decode("utf-8", errors="replace") or exc.reason
        raise APIError(f"API request failed ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise APIError(f"Could not connect to the API at {API_BASE_URL}: {exc}") from exc

    if not content:
        return None
    return json.loads(content)


def get(path):
    return request("GET", path)


def post(path, payload=None):
    return request("POST", path, json=payload)


def put(path, payload=None):
    return request("PUT", path, json=payload)


def delete(path):
    return request("DELETE", path)
