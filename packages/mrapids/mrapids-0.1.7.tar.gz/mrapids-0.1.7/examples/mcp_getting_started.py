#!/usr/bin/env python3
"""
MCP Getting Started Example

This example shows how to interact with the MicroRapid MCP server
to safely execute API operations through an AI agent interface.

Prerequisites:
1. Start the MCP server: 
   cd agent && cargo run -- --config-dir .mrapids
   
2. Have an API spec in .mrapids/api.yaml
"""

import requests
import json
from typing import Dict, Any, Optional

class MicroRapidMCP:
    """Simple client for MicroRapid MCP server"""
    
    def __init__(self, url: str = "http://localhost:8080"):
        self.url = url
        self.session = requests.Session()
        self.id_counter = 1
    
    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a JSON-RPC call to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.id_counter
        }
        self.id_counter += 1
        
        response = self.session.post(self.url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if "error" in result:
            raise Exception(f"MCP Error {result['error']['code']}: {result['error']['message']}")
        
        return result.get("result", {})
    
    def list_operations(self, method: Optional[str] = None, pattern: Optional[str] = None):
        """List available API operations"""
        params = {}
        if method or pattern:
            params["filter"] = {}
            if method:
                params["filter"]["method"] = method
            if pattern:
                params["filter"]["pattern"] = pattern
        
        return self._call("tools/list", params)
    
    def show_operation(self, operation_id: str):
        """Get details about a specific operation"""
        return self._call("tools/show", {"operation_id": operation_id})
    
    def run_operation(self, operation_id: str, parameters: Optional[Dict] = None, 
                     body: Optional[Any] = None, auth_profile: Optional[str] = None):
        """Execute an API operation"""
        params = {"operation_id": operation_id}
        if parameters:
            params["parameters"] = parameters
        if body:
            params["body"] = body
        if auth_profile:
            params["auth_profile"] = auth_profile
        
        return self._call("tools/run", params)

def main():
    """Example usage of MicroRapid MCP"""
    
    # Initialize client
    mcp = MicroRapidMCP()
    
    print("🚀 MicroRapid MCP Getting Started")
    print("=" * 50)
    
    # Example 1: List all GET operations
    print("\n1. Listing all GET operations:")
    try:
        result = mcp.list_operations(method="GET")
        operations = result.get("operations", [])
        print(f"Found {len(operations)} GET operations:")
        for op in operations[:5]:  # Show first 5
            print(f"  - {op['operation_id']:30} {op['path']}")
        if len(operations) > 5:
            print(f"  ... and {len(operations) - 5} more")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Search for user-related operations
    print("\n2. Searching for user operations:")
    try:
        result = mcp.list_operations(pattern="user")
        operations = result.get("operations", [])
        print(f"Found {len(operations)} user-related operations:")
        for op in operations:
            print(f"  - {op['operation_id']:30} {op['method']:6} {op['path']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Get operation details
    print("\n3. Getting operation details:")
    try:
        # First, find an operation
        result = mcp.list_operations()
        if result["operations"]:
            first_op = result["operations"][0]
            op_id = first_op["operation_id"]
            
            print(f"Details for '{op_id}':")
            details = mcp.show_operation(op_id)
            
            print(f"  Method: {details.get('method')}")
            print(f"  Path: {details.get('path')}")
            if details.get('summary'):
                print(f"  Summary: {details.get('summary')}")
            
            params = details.get('parameters', [])
            if params:
                print(f"  Parameters:")
                for param in params:
                    required = " (required)" if param.get('required') else ""
                    print(f"    - {param['name']}: {param.get('type', 'string')}{required}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Execute a safe operation (if available)
    print("\n4. Executing a safe read operation:")
    try:
        # Look for a simple GET operation without parameters
        result = mcp.list_operations(method="GET")
        safe_ops = [op for op in result["operations"] 
                   if "{" not in op["path"]]  # No path parameters
        
        if safe_ops:
            op = safe_ops[0]
            print(f"Executing: {op['operation_id']}")
            
            try:
                result = mcp.run_operation(op["operation_id"])
                print("Success! Response:")
                print(json.dumps(result, indent=2)[:200] + "...")
            except Exception as e:
                print(f"Execution failed: {e}")
                print("This might be due to:")
                print("  - Policy restrictions")
                print("  - Missing authentication")
                print("  - API endpoint requirements")
        else:
            print("No simple GET operations found to test")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Demonstrate policy enforcement
    print("\n5. Testing policy enforcement:")
    try:
        # Try to access an admin endpoint (should fail)
        print("Attempting to access admin endpoint...")
        result = mcp.run_operation("deleteAllUsers")  # Hypothetical admin operation
        print("Unexpected success - check your policies!")
    except Exception as e:
        if "1001" in str(e):  # Policy deny error code
            print("✅ Policy correctly denied access to admin operation")
            print(f"   Error: {e}")
        else:
            print(f"Other error: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Getting started complete!")
    print("\nNext steps:")
    print("1. Add your API spec to .mrapids/api.yaml")
    print("2. Configure policies in .mrapids/policy.yaml")
    print("3. Set up auth profiles in .mrapids/auth/")
    print("4. Integrate with your AI agent framework")

if __name__ == "__main__":
    main()