#!/usr/bin/env python3
"""
Test script for the multi-file support in ML Training Init MCP Server
Tests creating 1 training file + 2 config files
"""

import json
import asyncio
from pathlib import Path

# Mock server instance for testing
from src.server import MLTrainingServer

async def test_multi_file_support():
    """Test the new multi-file management capabilities"""
    print("Testing ML Training Init MCP Server - Multi-file Support\n")
    print("=" * 50)
    
    server = MLTrainingServer()
    
    # Test 1: Create training file
    print("\n1. Creating training file...")
    result = await server.handle_initialize_training_file({
        "file_name": "train_model.py",
        "content": "# Training script\nimport torch\nprint('Training started')",
        "reference": "test_reference"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success", "Failed to create training file"
    
    # Test 2: Try to create another training file (should fail)
    print("\n2. Attempting to create second training file (should fail)...")
    result = await server.handle_initialize_training_file({
        "file_name": "train2.py",
        "content": "# Another training script",
        "reference": "test"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "failure", "Should not allow second training file"
    
    # Test 3: Create first config file
    print("\n3. Creating first config file...")
    result = await server.handle_create_config_file({
        "file_name": "config.yaml",
        "content": "learning_rate: 0.001\nbatch_size: 32",
        "config_type": "hyperparameters"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success", "Failed to create first config file"
    
    # Test 4: Create second config file
    print("\n4. Creating second config file...")
    result = await server.handle_create_config_file({
        "file_name": ".env",
        "content": "CUDA_VISIBLE_DEVICES=0\nWANDB_PROJECT=test",
        "config_type": "environment"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success", "Failed to create second config file"
    
    # Test 5: Try to create third config file (should fail)
    print("\n5. Attempting to create third config file (should fail)...")
    result = await server.handle_create_config_file({
        "file_name": "extra_config.json",
        "content": '{"extra": "config"}',
        "config_type": "extra"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "failure", "Should not allow third config file"
    
    # Test 6: Get all managed files
    print("\n6. Getting all managed files...")
    result = await server.handle_get_managed_files({})
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success", "Failed to get managed files"
    
    # Test 7: Get specific file content
    print("\n7. Getting specific file content (config.yaml)...")
    result = await server.handle_get_file_content({
        "file_name": "config.yaml"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success", "Failed to get file content"
    
    # Test 8: Get current file (training file)
    print("\n8. Getting current file (training script)...")
    result = await server.handle_get_current_file({})
    print(f"Result: {json.dumps(result, indent=2)}")
    assert "train_model.py" in result["file_path"], "Wrong training file returned"
    
    # Test 9: Fix error in specific file
    print("\n9. Testing monitor_and_fix with specific file...")
    result = await server.handle_monitor_and_fix({
        "error_trace": "ModuleNotFoundError: No module named 'numpy'",
        "file_name": "train_model.py"
    })
    print(f"Result: {json.dumps(result, indent=2)}")
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    
    # Cleanup
    for file in ["train_model.py", "config.yaml", ".env"]:
        if Path(file).exists():
            Path(file).unlink()
            print(f"Cleaned up: {file}")

if __name__ == "__main__":
    asyncio.run(test_multi_file_support())