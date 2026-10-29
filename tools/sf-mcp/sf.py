"""sf CLI calls to a single dev sandbox, with trimmed output to save tokens."""
import json
import os
import re
import subprocess

from mcp.server.mcpserver.exceptions import ToolError

TARGET_ORG = os.environ.get("SF_TARGET_ORG", "my-dev-sandbox")
MAX_ROWS = 200
AUTH_HINTS = ("expired", "No authorization information", "INVALID_SESSION_ID")


class SfError(ToolError):  # ToolError: the SDK passes the message to the model instead of hiding it
    pass


def run_sf(args: list[str], allow_failure: bool = False) -> dict:
    # Argument list, no shell: a value like "Account; rm -rf /" stays a single argument.
    proc = subprocess.run(["sf", *args, "--target-org", TARGET_ORG, "--json"],
                          capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise SfError(proc.stderr.strip() or "Unreadable sf response")
    if payload.get("status", 0) != 0:
        # A failed validation is not a crash: return the payload so errors can be listed.
        if allow_failure and payload.get("name") == "FailedValidationError":
            return payload
        message = payload.get("message", "Unknown sf error")
        if any(hint in message for hint in AUTH_HINTS):
            message += f"\nRun: sf org login web -a {TARGET_ORG}"
        raise SfError(message)
    return payload.get("result") or {}


def trim_describe(result: dict) -> list[dict]:
    return [{
        "name": f["name"],
        "label": f["label"],
        "type": f["type"],
        "length": f.get("length"),
        "required": not f["nillable"] and f["createable"] and not f["defaultedOnCreate"],
        "referenceTo": f.get("referenceTo", []),
    } for f in result["fields"]]


def _strip_attributes(value):
    if isinstance(value, dict):
        return {k: _strip_attributes(v) for k, v in value.items() if k != "attributes"}
    if isinstance(value, list):
        return [_strip_attributes(v) for v in value]
    return value


def trim_query(result: dict) -> dict:
    records = result.get("records", [])
    return {
        "totalSize": result.get("totalSize", len(records)),
        "records": _strip_attributes(records[:MAX_ROWS]),
        "truncated": len(records) > MAX_ROWS,
    }


def trim_retrieve(result: dict) -> list[str]:
    return [f["filePath"] for f in result.get("files", [])]


# sf error line: "Error in <component> - <problem> (<line>:<column>)", position optional.
ERROR_LINE = re.compile(r"Error in (.+?) - (.*?)(?: \((\d+):\d+\))?$")


def trim_validate(result: dict) -> dict:
    if result.get("name") != "FailedValidationError":
        return {"success": bool(result.get("success")), "errors": []}
    detail = result["message"].split("Due To:", 1)[-1]
    errors = []
    for line in detail.splitlines():
        match = ERROR_LINE.match(line.strip())
        if match:
            file, problem, num = match.groups()
            errors.append({"file": file, "problem": problem, "line": int(num) if num else None})
    # Apex test or coverage failure: no "Error in" line, return the text as is.
    if not errors:
        errors.append({"file": None, "problem": detail.strip(), "line": None})
    return {"success": False, "errors": errors}
