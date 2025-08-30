#!/usr/bin/env python3
"""
MCP Server Test Client

This script demonstrates how to interact with the MCP server
using Python and the JSON-RPC protocol.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

class MCPClient:
    """Simple client for testing the MCP server"""
    
    def __init__(self, url: str = "http://localhost:8080"):
        self.url = url
        self.session = requests.Session()
        self.id_counter = 1
        
    def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a JSON-RPC call to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.id_counter
        }
        self.id_counter += 1
        
        try:
            response = self.session.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy"""
        return self.call("health")
    
    def list_operations(self, filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List available operations"""
        params = {}
        if filter:
            params["filter"] = filter
        return self.call("tools/list", params)
    
    def show_operation(self, operation_id: str) -> Dict[str, Any]:
        """Show details for a specific operation"""
        return self.call("tools/show", {"operation_id": operation_id})
    
    def run_operation(self, operation_id: str, parameters: Optional[Dict[str, Any]] = None, 
                     body: Optional[Any] = None, auth_profile: Optional[str] = None) -> Dict[str, Any]:
        """Execute an operation"""
        params = {"operation_id": operation_id}
        if parameters:
            params["parameters"] = parameters
        if body:
            params["body"] = body
        if auth_profile:
            params["auth_profile"] = auth_profile
        return self.call("tools/run", params)


def main():
    """Run test scenarios"""
    client = MCPClient()
    
    print("🧪 MCP Server Test Client")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check:")
    result = client.health_check()
    print(json.dumps(result, indent=2))
    
    # Test 2: List all operations
    print("\n2. List All Operations:")
    result = client.list_operations()
    if "result" in result:
        ops = result["result"].get("operations", [])
        print(f"Found {len(ops)} operations:")
        for op in ops:
            print(f"  - {op['operation_id']} ({op['method']} {op['path']})")
    else:
        print(json.dumps(result, indent=2))
    
    # Test 3: List GET operations only
    print("\n3. List GET Operations:")
    result = client.list_operations(filter={"method": "GET"})
    if "result" in result:
        ops = result["result"].get("operations", [])
        print(f"Found {len(ops)} GET operations")
    else:
        print(json.dumps(result, indent=2))
    
    # Test 4: Show operation details
    print("\n4. Show Operation Details (health):")
    result = client.show_operation("health")
    if "result" in result:
        op = result["result"]
        print(f"Operation: {op.get('operation_id')}")
        print(f"Method: {op.get('method')}")
        print(f"Path: {op.get('path')}")
        if op.get("description"):
            print(f"Description: {op.get('description')}")
    else:
        print(json.dumps(result, indent=2))
    
    # Test 5: Test error handling
    print("\n5. Test Error Handling (nonexistent operation):")
    result = client.show_operation("nonexistent_operation")
    if "error" in result:
        error = result["error"]
        print(f"Error Code: {error.get('code')}")
        print(f"Error Message: {error.get('message')}")
    else:
        print(json.dumps(result, indent=2))
    
    # Test 6: Run an operation (if available)
    print("\n6. Run Operation Test:")
    # First, check if we have any operations
    list_result = client.list_operations()
    if "result" in list_result and list_result["result"]["operations"]:
        # Try to run the first GET operation
        for op in list_result["result"]["operations"]:
            if op["method"] == "GET" and not op["path"].count("{") > 0:  # No parameters
                print(f"Running operation: {op['operation_id']}")
                result = client.run_operation(op["operation_id"])
                print(json.dumps(result, indent=2))
                break
        else:
            print("No suitable operation found for testing")
    else:
        print("No operations available")
    
    print("\n✅ Tests complete!")
    
    # Interactive mode
    print("\n" + "=" * 50)
    print("Interactive Mode - Enter commands or 'quit' to exit")
    print("Commands: health, list, show <id>, run <id>, quit")
    print("=" * 50)
    
    while True:
        try:
            command = input("\n> ").strip()
            if command == "quit":
                break
            elif command == "health":
                print(json.dumps(client.health_check(), indent=2))
            elif command == "list":
                print(json.dumps(client.list_operations(), indent=2))
            elif command.startswith("show "):
                op_id = command[5:].strip()
                print(json.dumps(client.show_operation(op_id), indent=2))
            elif command.startswith("run "):
                op_id = command[4:].strip()
                print(json.dumps(client.run_operation(op_id), indent=2))
            else:
                print("Unknown command. Use: health, list, show <id>, run <id>, quit")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()