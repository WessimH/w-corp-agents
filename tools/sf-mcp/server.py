"""Home-made MCP: four sf CLI tools, all targeting the dev sandbox (SF_TARGET_ORG)."""
from mcp.server.mcpserver import MCPServer

import sf

mcp = MCPServer("sf-mcp")


@mcp.tool()
def describe_object(object_name: str) -> list[dict]:
    """Fields of a Salesforce object: name, label, type, length, required, referenced object."""
    return sf.trim_describe(sf.run_sf(["sobject", "describe", "--sobject", object_name]))


@mcp.tool()
def soql(query: str) -> dict:
    """Runs a SOQL query. Returns at most 200 records, without technical attributes."""
    return sf.trim_query(sf.run_sf(["data", "query", "--query", query]))


@mcp.tool()
def retrieve(metadata: list[str]) -> list[str]:
    """Retrieves metadata into force-app (e.g. "CustomObject:Invoice__c"). Returns the files written."""
    args = ["project", "retrieve", "start"]
    for m in metadata:
        args += ["--metadata", m]
    return sf.trim_retrieve(sf.run_sf(args))


@mcp.tool()
def validate_deploy(source_dir: str = "force-app") -> dict:
    """Check-only deployment to the dev sandbox (nothing is applied), running only the related Apex tests.
    Returns success or the list of errors."""
    # Not RunLocalTests: tests already broken in the org would fail every validation.
    return sf.trim_validate(sf.run_sf(
        ["project", "deploy", "validate", "--source-dir", source_dir, "--test-level", "RunRelevantTests"],
        allow_failure=True))


if __name__ == "__main__":
    mcp.run()
