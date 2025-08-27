#!/usr/bin/env python3
"""
MCP Client Test Script for VoluteMCP Server

This script tests the MCP server by acting as a simple MCP client,
allowing you to verify the server works correctly with MCP protocol.
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class SimpleMCPClient:
    """Simple MCP client for testing our server."""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
    
    async def start_server(self):
        """Start the MCP server process."""
        print("🚀 Starting MCP server...")
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path(__file__).parent
        )
        print("✅ Server started")
    
    async def send_request(self, method: str, params: Optional[Dict] = None) -> Dict[Any, Any]:
        """Send a JSON-RPC request to the server."""
        if not self.process:
            raise RuntimeError("Server not started")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        print(f"📤 Sending: {method}")
        
        # Send request
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("No response from server")
        
        try:
            response = json.loads(response_line.decode().strip())
            print(f"📥 Received response for {method}")
            return response
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse response: {e}")
            print(f"Raw response: {response_line}")
            raise
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            print("🛑 Stopping server...")
            self.process.terminate()
            await self.process.wait()
            print("✅ Server stopped")


async def test_mcp_integration():
    """Test MCP server integration."""
    print("=" * 60)
    print("🧪 MCP Integration Test Suite")
    print("=" * 60)
    
    # Server command
    server_cmd = [sys.executable, "server.py", "stdio"]
    client = SimpleMCPClient(server_cmd)
    
    try:
        # Start server
        await client.start_server()
        
        # Test 1: Initialize
        print("\n🔄 Test 1: Server Initialization")
        init_response = await client.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        if "result" in init_response:
            print("✅ Server initialized successfully")
            print(f"   Server name: {init_response['result'].get('serverInfo', {}).get('name', 'Unknown')}")
            print(f"   Protocol version: {init_response['result'].get('protocolVersion', 'Unknown')}")
        else:
            print(f"❌ Initialization failed: {init_response}")
            return False
        
        # Test 2: List Tools
        print("\n🔧 Test 2: List Available Tools")
        tools_response = await client.send_request("tools/list")
        
        if "result" in tools_response and "tools" in tools_response["result"]:
            tools = tools_response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            
            powerpoint_tools = 0
            for tool in tools[:10]:  # Show first 10 tools
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:60]}...")
                if 'powerpoint' in tool.get('name', '').lower():
                    powerpoint_tools += 1
            
            if len(tools) > 10:
                print(f"   ... and {len(tools) - 10} more tools")
            
            print(f"   📊 PowerPoint tools found: {powerpoint_tools}")
            
            if powerpoint_tools == 0:
                print("⚠️  Warning: No PowerPoint tools found")
        else:
            print(f"❌ Failed to list tools: {tools_response}")
            return False
        
        # Test 3: List Resources
        print("\n📁 Test 3: List Available Resources")
        resources_response = await client.send_request("resources/list")
        
        if "result" in resources_response and "resources" in resources_response["result"]:
            resources = resources_response["result"]["resources"]
            print(f"✅ Found {len(resources)} resources:")
            for resource in resources[:5]:  # Show first 5 resources
                print(f"   - {resource.get('uri', 'Unknown')}: {resource.get('description', 'No description')[:50]}...")
            
            if len(resources) > 5:
                print(f"   ... and {len(resources) - 5} more resources")
        else:
            print(f"❌ Failed to list resources: {resources_response}")
        
        # Test 4: Test a Simple Tool
        print("\n🧮 Test 4: Test Simple Tool (calculate)")
        tool_response = await client.send_request("tools/call", {
            "name": "calculate",
            "arguments": {
                "expression": "2 + 3 * 4"
            }
        })
        
        if "result" in tool_response:
            print("✅ Tool execution successful")
            print(f"   Result: {tool_response['result']}")
        else:
            print(f"❌ Tool execution failed: {tool_response}")
        
        # Test 5: Test PowerPoint Tool (if available)
        print("\n📊 Test 5: Test PowerPoint Tool (validation)")
        pp_response = await client.send_request("tools/call", {
            "name": "validate_powerpoint_file",
            "arguments": {
                "presentation_path": "nonexistent.pptx"
            }
        })
        
        if "result" in pp_response:
            print("✅ PowerPoint tool execution successful")
            print(f"   Result type: {type(pp_response['result'])}")
            if isinstance(pp_response['result'], dict):
                print(f"   Success: {pp_response['result'].get('success', 'Unknown')}")
        else:
            print(f"❌ PowerPoint tool execution failed: {pp_response}")
        
        # Test 6: Test Resource Access
        print("\n📄 Test 6: Test Resource Access")
        resource_response = await client.send_request("resources/read", {
            "uri": "config://server"
        })
        
        if "result" in resource_response:
            print("✅ Resource access successful")
            print(f"   Resource type: {type(resource_response['result'])}")
        else:
            print(f"❌ Resource access failed: {resource_response}")
        
        print("\n" + "=" * 60)
        print("🎉 MCP Integration Test Complete!")
        print("✅ Your server is ready to integrate with MCP clients")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await client.stop_server()


def print_integration_instructions():
    """Print instructions for integrating with different MCP clients."""
    print("\n" + "🔗 " + "=" * 58)
    print("  INTEGRATION INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 1. CLAUDE DESKTOP INTEGRATION:")
    print("   Add this to your Claude Desktop MCP config:")
    print("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print()
    config_path = Path(__file__).parent / "claude_mcp_config.json"
    print(f"   Use the config file: {config_path}")
    print("   Then restart Claude Desktop")
    
    print("\n🌐 2. HTTP CLIENT TESTING:")
    print("   Start HTTP server: python server.py")
    print("   Test endpoint: http://localhost:8000/health")
    print("   MCP over HTTP: http://localhost:8000")
    
    print("\n🧪 3. CUSTOM MCP CLIENT:")
    print("   Use any MCP-compatible client library")
    print("   Connect via STDIO: python server.py stdio")
    print("   Connect via HTTP: http://localhost:8000")
    
    print("\n📱 4. DEVELOPMENT TESTING:")
    print("   Run this test: python test_mcp_client.py")
    print("   Run unit tests: python run_tests.py")
    print("   Manual testing: python server.py stdio")


if __name__ == "__main__":
    # Check if we should run the test or just show instructions
    if len(sys.argv) > 1 and sys.argv[1] == "--instructions":
        print_integration_instructions()
    else:
        # Run the integration test
        success = asyncio.run(test_mcp_integration())
        
        # Show integration instructions
        print_integration_instructions()
        
        sys.exit(0 if success else 1)
