from typing import Any, Dict, Tuple, Union, Optional
import httpx
import asyncio
import json
import logging
import argparse
import re
import os
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, create_model, Field

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(description="Run FastN MCP server with specified API credentials and use case.")
    parser.add_argument("--api_key", help="API key for authentication.")
    parser.add_argument("--space_id", help="Space ID for the target environment.")
    parser.add_argument("--tenant_id", help="Tenant ID for the target environment.")
    parser.add_argument("--auth_token", help="Auth token for the target environment.")
    return parser

# API Endpoints
GET_TOOLS_URL = "https://live.fastn.ai/api/ucl/getTools"
EXECUTE_TOOL_URL = "https://live.fastn.ai/api/ucl/executeTool"

class FastNServer:
    def __init__(self, api_key: str = None, space_id: str = None, tenant_id: str = None, auth_token: str = None):
        self.api_key = api_key
        self.space_id = space_id
        self.tenant_id = tenant_id
        self.auth_token = auth_token
        self.mcp = FastMCP("fastn")
        
        # Common headers
        self.headers = {
            "Content-Type": "application/json",
            "x-fastn-space-id": space_id,
            "stage": "LIVE",
            "x-fastn-custom-auth": "true"
        }
        
        # Add authentication headers based on provided credentials
        if api_key:
            # API key authentication
            self.headers["x-fastn-api-key"] = api_key
            self.headers["x-fastn-space-tenantid"] = ""
        else:
            # Tenant authentication
            if auth_token and not auth_token.startswith('Bearer '):
                auth_token = "Bearer " + auth_token
            
            self.headers["x-fastn-api-key"] = auth_token.replace("Bearer ", "")
            self.headers["x-fastn-space-tenantid"] = tenant_id
            self.headers["authorization"] = auth_token

    async def fetch_tools(self) -> list:
        """Fetch tool definitions from the getTools API endpoint."""
        data = {
            "input": {
                "spaceId": self.space_id
            }
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(GET_TOOLS_URL, headers=self.headers, json=data)
                response.raise_for_status()
                tools = response.json()
                logging.info(f"Fetched {len(tools)} tools.")
                return tools
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                logging.error(f"Request error: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
        return []

    async def execute_tool(self, action_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by calling the executeTool API."""
        data = {"input": {"actionId": action_id, "parameters": parameters}}
        logging.info(f"Executing tool with parameters: {json.dumps(parameters)}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(EXECUTE_TOOL_URL, headers=self.headers, json=data)
                response.raise_for_status()
                result = response.json()
                return json.dumps(result)
            except httpx.HTTPStatusError as e:
                logging.error(f"Execution failed: {e.response.status_code} - {e.response.text}")
                return json.dumps({"error": f"HTTP error: {e.response.status_code}"})
            except Exception as e:
                logging.error(f"Unexpected execution error: {e}")
                return json.dumps({"error": str(e)})

    def validate_tool_name(self, name: str) -> str:
        """
        Validate and sanitize tool name to match pattern '^[a-zA-Z0-9_-]{1,64}$'.
        Returns sanitized name or raises ValueError if name can't be sanitized.
        """
        if re.match(r'^[a-zA-Z0-9_-]{1,64}$', name):
            return name
        
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        
        if len(sanitized) > 64:
            sanitized = sanitized[:64]
        
        if not sanitized:
            sanitized = "tool_" + str(hash(name))[:10]
        
        logging.warning(f"Tool name sanitized: '{name}' → '{sanitized}'")
        return sanitized

    def register_tool(self, tool_def: Dict[str, Any]):
        """Dynamically create and register a tool based on the tool definition."""
        try:
            action_id = tool_def["actionId"]
            function_info = tool_def["function"]
            original_name = function_info["name"]
            
            try:
                function_name = self.validate_tool_name(original_name)
            except ValueError as e:
                logging.error(f"Invalid tool name '{original_name}': {e}. Skipping tool.")
                return
                
            parameters_schema = function_info.get("parameters", {})
            description = function_info.get("description", "")

            @self.mcp.tool(name=function_name, description=description)
            async def dynamic_tool(params_obj = parameters_schema) -> str:
                """Dynamically created tool function."""
                try:
                    logging.info(f"Tool {function_name} called with params: {params_obj}")
                    return await self.execute_tool(action_id, params_obj)
                except Exception as e:
                    logging.error(f"Error in {function_name}: {e}")
                    return json.dumps({"error": str(e)})

            dynamic_tool.__name__ = function_name
            
            logging.info(f"Registered tool: {function_name}")
            logging.info(f"Description: {description}")
        except KeyError as e:
            logging.error(f"Invalid tool definition missing key: {e}")
        except Exception as e:
            logging.error(f"Error registering tool: {e}")

    async def initialize_tools(self):
        """Fetch tools and register them."""
        tools_data = await self.fetch_tools()
        for tool_def in tools_data:
            self.register_tool(tool_def)

    def run(self):
        """Run the FastN MCP server."""
        asyncio.run(self.initialize_tools())
        self.mcp.run(transport='stdio')

def main():
    """Main entry point for the FastN server CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Get values from arguments or environment variables
    api_key = args.api_key or os.getenv('FASTN_API_KEY')
    space_id = args.space_id or os.getenv('FASTN_SPACE_ID')
    tenant_id = args.tenant_id or os.getenv('FASTN_TENANT_ID')
    auth_token = args.auth_token or os.getenv('FASTN_AUTH_TOKEN')
    
    # Validate that space_id is provided
    if not space_id:
        parser.error("--space_id must be provided as argument or FASTN_SPACE_ID environment variable")
    
    # Validate authentication credentials
    if not api_key and not (tenant_id and auth_token):
        parser.error("Either --api_key (or FASTN_API_KEY env var) OR both --tenant_id and --auth_token (or FASTN_TENANT_ID and FASTN_AUTH_TOKEN env vars) must be provided")
    
    server = FastNServer(
        api_key=api_key, 
        space_id=space_id,
        tenant_id=tenant_id,
        auth_token=auth_token
    )
    server.run()

if __name__ == "__main__":
    main() 