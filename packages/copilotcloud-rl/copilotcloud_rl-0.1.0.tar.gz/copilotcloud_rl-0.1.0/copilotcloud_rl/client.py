import os
from typing import Any, Dict, Optional

import requests

# Use Private API Key header
COPILOT_CLOUD_PRIVATE_API_KEY_HEADER = "X-CopilotCloud-Private-Api-Key"
COPILOT_CLOUD_PUBLIC_API_KEY_HEADER = "X-CopilotCloud-Public-Api-Key"

DEFAULT_TIMEOUT_SECONDS = 15


def _get_base_url(explicit_url: Optional[str] = None) -> str:
    base = explicit_url or os.getenv("COPILOTCLOUD_API_URL")
    if not base:
        raise ValueError(
            "Missing CopilotCloud API base URL. Set COPILOTCLOUD_API_URL or pass api_url."
        )
    return base.rstrip("/")


def _get_public_api_key(explicit_key: Optional[str] = None) -> str:
    key = explicit_key or os.getenv("COPILOTCLOUD_PUBLIC_API_KEY")
    if not key:
        raise ValueError(
            "Missing CopilotCloud public API key. Set COPILOTCLOUD_PUBLIC_API_KEY or pass public_api_key."
        )
    return key


def _get_private_api_key(explicit_key: Optional[str] = None) -> str:
    key = explicit_key or os.getenv("COPILOTCLOUD_PRIVATE_API_KEY")
    if not key:
        raise ValueError(
            "Missing CopilotCloud private API key. Set COPILOTCLOUD_PRIVATE_API_KEY or pass private_api_key."
        )
    return key


def getLearningContext(
    prompt: str,
    agentName: str,
    *,
    api_url: Optional[str] = None,
    public_api_key: Optional[str] = None,
    private_api_key: Optional[str] = None,
    limit: Optional[int] = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """
    Call CopilotCloud Reinforcement Learning context endpoint.

    POST {api_url}/reinforcement-learning/v1/context
    Headers: X-CopilotCloud-Private-Api-Key: <key>
    Body: { agentName: string, prompt: string, limit?: number }

    Returns JSON (e.g., { "learningContext": str }).
    """

    if not isinstance(prompt, str) or not prompt:
        raise ValueError("prompt must be a non-empty string")
    if not isinstance(agentName, str) or not agentName:
        raise ValueError("agentName must be a non-empty string")

    base_url = _get_base_url(api_url)
    public_key = _get_public_api_key(public_api_key)
    private_key = _get_private_api_key(private_api_key)

    url = f"{base_url}/reinforcement-learning/v1/context"
    headers = {
        COPILOT_CLOUD_PUBLIC_API_KEY_HEADER: public_key,
        COPILOT_CLOUD_PRIVATE_API_KEY_HEADER: private_key,
        "Content-Type": "application/json"
    }

    body: Dict[str, Any] = {"prompt": prompt, "agentName": agentName}
    if isinstance(limit, int) and limit > 0:
        body["limit"] = limit

    resp = requests.post(url, json=body, headers=headers, timeout=timeout_seconds)

    try:
        resp.raise_for_status()
    except requests.HTTPError as ex:
        # propagate structured error
        raise RuntimeError(
            f"CopilotCloud RL context request failed: {ex}; status={resp.status_code}; body={resp.text}"
        ) from ex

    try:
        data = resp.json()
    except Exception as ex:  # noqa: BLE001
        raise RuntimeError(f"Invalid JSON from CopilotCloud RL context: {resp.text}") from ex

    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected response format from CopilotCloud RL context: {data}")

    return data
