import re
import requests
from typing import Dict, Any
from datetime import date
import uuid
import os

# regex for a very basic email validation
_EMAIL_RE = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


class PayloadValidationError(ValueError):
    """Raised when the payload is missing required fields or
    has invalid values."""


def _validate_payload(payload: Dict[str, Any]) -> None:
    # Top‐level required fields
    required = {
        "email_address": str,
        "user_name": str,
        "repo_object": dict,
    }
    for field, typ in required.items():
        if field not in payload:
            raise PayloadValidationError(f"Missing required field: '{field}'")
        if not isinstance(payload[field], typ):
            raise PayloadValidationError(
                f"Field '{field}' must be of type {typ.__name__}"
            )

    # email format
    if not _EMAIL_RE.match(payload["email_address"]):
        raise PayloadValidationError("Invalid email address format")

    # repo_object sub‐fields
    repo = payload["repo_object"]

    # *Required* sub-fields – must be present and right type
    required_repo_fields = {
        "repository_name": str,
        "repository_url": str,
        "branch": str,
        "size": str,
        "language": str,
        "source": str,
    }

    # *Optional* sub-fields – validate only if provided (can be None)
    optional_repo_fields = {
        "is_private": bool,
        "git_provider_type": str,
        "installation_id": str,  # ← now **optional**
        "refresh_token": str,
        "commit_hash": str,
        "commit_message": str,
        "commit_author": str,
        "directory_name": str,
        "personal_access_token": str,
    }
    # required loop
    for field, typ in required_repo_fields.items():
        if field not in repo:
            raise PayloadValidationError(f"Missing repo_object.{field}")
        if not isinstance(repo[field], typ):
            raise PayloadValidationError(f"repo_object.{field} must be {typ.__name__}")

    # optional loop
    for field, typ in optional_repo_fields.items():
        if (
            field in repo
            and repo[field] is not None
            and not isinstance(repo[field], typ)
        ):
            raise PayloadValidationError(f"repo_object.{field} must be {typ.__name__}")

    # you can add more checks here (URL validation, branch name patterns, etc.)


def _populate_metadata(payload: Dict[str, Any]) -> None:
    """Autofill metadata.created_by/on and updated_by/on."""
    user = payload["email_address"]
    today = date.today().isoformat()
    payload["metadata"] = {
        "created_by": user,
        "created_on": today,
        "updated_by": user,
        "updated_on": today,
    }
    payload["action"] = "code_to_wiki"

    # populate wiki if missing or incomplete
    wiki = payload.get("wiki", {})
    wiki.setdefault("wiki_name", payload["repo_object"]["repository_name"])
    wiki.setdefault("wiki_source", payload["repo_object"]["source"])  # new!
    wiki.setdefault("wiki_url", None)

    payload["wiki_object"] = wiki
    payload["request_id"] = str(uuid.uuid4())
    payload["request_type"] = "code_to_wiki"
    payload["status"] = "pending"
    if payload["service_name"] is None or payload["service_name"] == "":
        payload["service_name"] = payload["repo_object"]["repository_name"]


def post(
    endpoint: str, token: str, payload: Dict[str, Any], timeout: int = 30
) -> requests.Response:
    """
    Send a POST with validated payload and autopopulated metadata.

    Raises:
        PayloadValidationError: if payload is missing required data.
        requests.RequestException: on network failures.
    """
    # 1) Validate schema
    _validate_payload(payload)

    # 2) Add metadata
    _populate_metadata(payload)

    headers = {
        "x-api-key": token,
        "Content-Type": "application/json",
    }

    try:
        ip_address = requests.get("https://api.ipify.org").text
        geo = requests.get(f"https://ipapi.co/{ip_address}/json/").json()
        country = geo.get("country_name", "")
        if ip_address and ip_address != "":
            headers["x-ip"] = ip_address
        if country and country != "":
            headers["x-country"] = country
    except Exception as e:
        pass

    print("payload:", payload)
    print("testing")
    response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    print("response:", response.json())
    print("testing")
    return response
