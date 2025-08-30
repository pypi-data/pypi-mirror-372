#!/usr/bin/env python3
"""
Example MCP client for AI agents to interact with MicroRapid

This demonstrates how an AI agent would use the MCP server to:
1. List available operations
2. Get operation details
3. Execute API calls with policy enforcement
"""

import json
import requests
from typing import Any, Dict, Optional


class MCPClient:
    """Simple MCP client for demonstration"""
    
    def __init__(self, base_url: str = "http://localhost:3333"):
        self.base_url = base_url
        self.session = requests.Session()
        self.request_id = 0
    
    def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a JSON-RPC call to the MCP server"""
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        
        response = self.session.post(
            self.base_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"MCP Error: {result['error']['message']}")
        
        return result.get("result")


def main():
    # Create MCP client
    client = MCPClient()
    
    print("MicroRapid MCP Agent Example")
    print("============================\n")
    
    # 1. Check health
    print("1. Checking server health...")
    try:
        health = client.call("health")
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}\n")
    except Exception as e:
        print(f"   Error: {e}\n")
        return
    
    # 2. List available operations
    print("2. Listing available operations...")
    try:
        operations = client.call("list", {
            "filter": {
                "method": "GET"
            }
        })
        print(f"   Found {operations['total']} GET operations:")
        for op in operations['operations'][:5]:  # Show first 5
            print(f"   - {op['operation_id']}: {op['method']} {op['path']}")
        if operations['total'] > 5:
            print(f"   ... and {operations['total'] - 5} more")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 3. Get operation details
    print("3. Getting operation details for 'getUser'...")
    try:
        details = client.call("show", {
            "operation_id": "getUser"
        })
        print(f"   Operation: {details['operation_id']}")
        print(f"   Method: {details['method']}")
        print(f"   Path: {details['path']}")
        if details.get('parameters'):
            print("   Parameters:")
            for param in details['parameters']:
                print(f"   - {param['name']} ({param['location']}): {param.get('description', 'No description')}")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")
    
    # 4. Execute an operation (will be controlled by policy)
    print("4. Attempting to execute 'getUser' operation...")
    try:
        result = client.call("run", {
            "operation_id": "getUser",
            "parameters": {
                "userId": "123"
            },
            "auth_profile": "default-agent"
        })
        print("   Success! Response:")
        print(f"   Status: {result.get('status')}")
        if result.get('data'):
            print(f"   Data: {json.dumps(result['data'], indent=2)}")
        print()
    except Exception as e:
        print(f"   Error: {e}")
        print("   This is expected if the operation is denied by policy\n")
    
    # 5. Try a forbidden operation (should be denied by policy)
    print("5. Attempting a DELETE operation (should be denied)...")
    try:
        result = client.call("run", {
            "operation_id": "deleteUser",
            "parameters": {
                "userId": "123"
            },
            "auth_profile": "default-agent"
        })
        print("   Unexpected success - policy may be too permissive")
    except Exception as e:
        print(f"   Expected denial: {e}")
        print("   Policy is working correctly!\n")
    
    # 6. Get available tools
    print("6. Listing available MCP tools...")
    try:
        tools = client.call("tools")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")


if __name__ == "__main__":
    main()