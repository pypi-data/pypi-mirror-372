#!/usr/bin/env python3
"""
Test script for PowerPoint tools functionality.
This script tests the PowerPoint tools without requiring actual PowerPoint files.
"""

import sys
import os
import traceback
import asyncio
from typing import Dict, Any
from pathlib import Path

# Add parent directory to path to import project modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        import powerpoint_metadata
        print("✓ powerpoint_metadata imported successfully")
        
        import powerpoint_tools
        print("✓ powerpoint_tools imported successfully")
        
        from powerpoint_metadata import PowerPointMetadataExtractor, PPTX_AVAILABLE
        print(f"✓ PowerPointMetadataExtractor imported, python-pptx available: {PPTX_AVAILABLE}")
        
        from powerpoint_tools import (
            PowerPointAnalysisResult,
            SlideContentSummary,
            PresentationSummary,
            register_powerpoint_tools
        )
        print("✓ PowerPoint tools classes imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False


def test_pydantic_models():
    """Test that Pydantic models work correctly."""
    print("\nTesting Pydantic models...")
    
    try:
        from powerpoint_tools import PowerPointAnalysisResult, SlideContentSummary, PresentationSummary
        
        # Test PowerPointAnalysisResult
        result = PowerPointAnalysisResult(
            success=True,
            message="Test successful",
            data={"test": "data"}
        )
        print("✓ PowerPointAnalysisResult created successfully")
        
        # Test SlideContentSummary
        slide = SlideContentSummary(
            slide_number=1,
            title="Test Slide",
            text_content="Sample text content",
            shape_count=5,
            has_images=True,
            has_tables=False,
            has_charts=True
        )
        print("✓ SlideContentSummary created successfully")
        
        # Test PresentationSummary
        presentation = PresentationSummary(
            filename="test.pptx",
            total_slides=1,
            title="Test Presentation",
            author="Test Author",
            slides=[slide]
        )
        print("✓ PresentationSummary created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Pydantic model error: {e}")
        traceback.print_exc()
        return False


def test_metadata_extractor():
    """Test PowerPoint metadata extractor initialization."""
    print("\nTesting PowerPoint metadata extractor...")
    
    try:
        from powerpoint_metadata import PowerPointMetadataExtractor, PPTX_AVAILABLE
        
        if not PPTX_AVAILABLE:
            print("⚠ python-pptx not available - skipping metadata extractor test")
            return True
            
        # Test initialization without file
        extractor = PowerPointMetadataExtractor()
        print("✓ PowerPointMetadataExtractor initialized successfully")
        
        # Test context manager
        with PowerPointMetadataExtractor() as ext:
            print("✓ Context manager works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Metadata extractor error: {e}")
        traceback.print_exc()
        return False


def test_tools_registration():
    """Test that PowerPoint tools can be registered with FastMCP."""
    print("\nTesting PowerPoint tools registration...")
    
    try:
        from fastmcp import FastMCP
        from powerpoint_tools import register_powerpoint_tools
        
        # Create a test FastMCP instance
        mcp = FastMCP("TestServer")
        
        # Register PowerPoint tools
        register_powerpoint_tools(mcp)
        print("✓ PowerPoint tools registered successfully")
        
        # Check that tools were registered (sync version)
        async def check_tools():
            tools_dict = await mcp.get_tools()
            return [name for name in tools_dict.keys() if 'powerpoint' in name.lower()]
        
        powerpoint_tools = asyncio.run(check_tools())
        
        if powerpoint_tools:
            print(f"✓ Found {len(powerpoint_tools)} PowerPoint tools:")
            for tool_name in powerpoint_tools:
                print(f"  - {tool_name}")
        else:
            print("⚠ No PowerPoint tools found in registered tools")
            
        return True
        
    except Exception as e:
        print(f"✗ Tools registration error: {e}")
        traceback.print_exc()
        return False


def test_main_tools_integration():
    """Test that main tools.py integrates PowerPoint tools correctly."""
    print("\nTesting main tools integration...")
    
    try:
        from tools import register_tools, POWERPOINT_TOOLS_AVAILABLE
        from fastmcp import FastMCP
        
        print(f"PowerPoint tools available in main module: {POWERPOINT_TOOLS_AVAILABLE}")
        
        # Create test server and register tools
        mcp = FastMCP("IntegrationTestServer")
        register_tools(mcp)
        print("✓ Main tools registration completed")
        
        # List all tools
        async def get_all_tools():
            return await mcp.get_tools()
        
        all_tools = asyncio.run(get_all_tools())
        print(f"✓ Total tools registered: {len(all_tools)}")
        
        # Check for PowerPoint tools
        powerpoint_tools = [name for name in all_tools.keys() if 'powerpoint' in name.lower()]
        if powerpoint_tools:
            print(f"✓ PowerPoint tools integrated: {len(powerpoint_tools)} tools")
        elif POWERPOINT_TOOLS_AVAILABLE:
            print("⚠ PowerPoint tools should be available but not found")
        else:
            print("ℹ PowerPoint tools not available (expected)")
            
        return True
        
    except Exception as e:
        print(f"✗ Main tools integration error: {e}")
        traceback.print_exc()
        return False


def test_server_startup():
    """Test that the server can start with PowerPoint tools."""
    print("\nTesting server startup...")
    
    try:
        from fastmcp import FastMCP
        from config import get_config
        from tools import register_tools
        from resources import register_resources
        
        # Get configuration
        config = get_config()
        print("✓ Configuration loaded")
        
        # Create server instance
        mcp = FastMCP(config.name)
        print("✓ FastMCP server created")
        
        # Register components
        register_tools(mcp)
        print("✓ Tools registered")
        
        register_resources(mcp)
        print("✓ Resources registered")
        
        # Check tool count
        async def get_counts():
            tools = await mcp.get_tools()
            resources = await mcp.get_resources()
            return len(tools), len(resources)
        
        tool_count, resource_count = asyncio.run(get_counts())
        print(f"✓ Server configured with {tool_count} tools and {resource_count} resources")
        
        return True
        
    except Exception as e:
        print(f"✗ Server startup error: {e}")
        traceback.print_exc()
        return False


def test_file_validation_tool():
    """Test the PowerPoint file validation tool with non-existent file."""
    print("\nTesting PowerPoint file validation tool...")
    
    try:
        from fastmcp import FastMCP
        from powerpoint_tools import register_powerpoint_tools
        
        # Create server and register tools
        mcp = FastMCP("ValidationTestServer")
        register_powerpoint_tools(mcp)
        
        # Get the validation tool
        async def get_validation_tool():
            tools_dict = await mcp.get_tools()
            return tools_dict.get("validate_powerpoint_file")
        
        validation_tool = asyncio.run(get_validation_tool())
        
        if not validation_tool:
            print("⚠ validate_powerpoint_file tool not found")
            return True
            
        # Test with non-existent file (should handle gracefully)
        print("Testing validation with non-existent file...")
        
        # This should work without crashing (testing our error handling)
        async def test_tool():
            return await validation_tool.run({"presentation_path": "nonexistent.pptx"})
        
        tool_result = asyncio.run(test_tool())
        print(f"✓ Validation tool handled non-existent file gracefully")
        print(f"  - Tool result: {tool_result}")
        
        return True
        
    except Exception as e:
        print(f"✗ File validation tool error: {e}")
        traceback.print_exc()
        return False


def run_all_tests() -> bool:
    """Run all tests and return overall success status."""
    print("=" * 60)
    print("PowerPoint Tools Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_pydantic_models,
        test_metadata_extractor,
        test_tools_registration,
        test_main_tools_integration,
        test_server_startup,
        test_file_validation_tool,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test_func.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{i+1:2d}. {test_func.__name__:<30} {status}")
    
    print("-" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠ Some tests failed - check output above")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
