#!/usr/bin/env python3
"""
Test script for the new AI-driven regeneration workflow
"""

import asyncio
import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent / 'src'))

from server import MLTrainingServer

async def test_regeneration_workflow():
    """Test the complete error analysis and regeneration workflow"""
    server = MLTrainingServer()
    
    print("=== Testing AI-Driven Regeneration Workflow ===\n")
    
    # Step 1: Initialize a training file with an intentional error
    print("1. Creating training file with missing import...")
    init_result = await server.handle_initialize_training_file({
        "file_name": "test_train.py",
        "content": """#!/usr/bin/env python3
# Test training script with intentional error

def main():
    # This will cause ModuleNotFoundError
    import torch
    import argparse
    
    parser = argparse.ArgumentParser()
    # Missing --logging_steps argument
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    
    # This will cause NameError
    print(f"Training for {epochs} epochs")  # Should be args.epochs
    
if __name__ == "__main__":
    main()
""",
        "reference": "test_example"
    })
    print(f"Result: {init_result['status']}")
    print(f"File created: {init_result.get('file_path')}\n")
    
    # Step 2: Simulate an error
    print("2. Simulating ModuleNotFoundError...")
    error_trace = """Traceback (most recent call last):
  File "test_train.py", line 6, in <module>
    import torch
ModuleNotFoundError: No module named 'torch'"""
    
    # Step 3: Call monitor_and_fix to get analysis context
    print("3. Analyzing error with monitor_and_fix...")
    analysis = await server.handle_monitor_and_fix({
        "error_trace": error_trace,
        "fix_instructions": "Add torch to imports or install it"
    })
    
    print(f"Status: {analysis['status']}")
    if analysis['status'] == 'needs_ai_regeneration':
        print("Error Analysis:")
        print(f"  - Type: {analysis['error_analysis']['type']}")
        print(f"  - Details: {analysis['error_analysis']['details']}")
        print(f"  - Suggestion: {analysis['error_analysis'].get('suggestion')}")
        print(f"  - Message: {analysis['message']}\n")
    
    # Step 4: Simulate AI regenerating the code
    print("4. AI regenerates corrected code...")
    corrected_content = """#!/usr/bin/env python3
# Test training script - CORRECTED VERSION

def main():
    # Fixed: torch import moved to top level
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--logging_steps", type=int, default=10)  # Added missing argument
    args = parser.parse_args()
    
    # Fixed: using args.epochs instead of undefined 'epochs'
    print(f"Training for {args.epochs} epochs")
    print(f"Logging every {args.logging_steps} steps")
    
    # Note: torch import removed as it's not actually used
    print("Training simulation complete!")
    
if __name__ == "__main__":
    main()
"""
    
    # Step 5: Apply the regenerated code
    print("5. Applying regenerated code with regenerate_file_with_fixes...")
    regen_result = await server.handle_regenerate_file_with_fixes({
        "file_name": "test_train.py",
        "new_content": corrected_content,
        "backup": True
    })
    
    print(f"Status: {regen_result['status']}")
    print(f"Message: {regen_result['message']}")
    if regen_result.get('backup_path'):
        print(f"Backup saved: {regen_result['backup_path']}")
    print(f"Note: {regen_result.get('note')}\n")
    
    # Step 6: Test hyperparameter update request
    print("6. Testing hyperparameter update request...")
    hyper_result = await server.handle_update_hyperparameters({
        "updates": {
            "epochs": 2,
            "batch_size": 8,
            "max_steps": 50
        }
    })
    
    print(f"Status: {hyper_result['status']}")
    if hyper_result['status'] == 'needs_ai_update':
        print("Hyperparameter Update Context:")
        print(f"  - Requested changes: {hyper_result['requested_updates']}")
        print(f"  - Message: {hyper_result['message']}")
        print("  - Suggestions:")
        for suggestion in hyper_result.get('suggestions', []):
            print(f"    {suggestion}")
    
    print("\n=== Workflow Test Complete ===")
    
    # Cleanup
    import os
    if os.path.exists("test_train.py"):
        os.remove("test_train.py")
    # Remove backup files
    for file in Path(".").glob("test_train.py.backup_*"):
        file.unlink()
    
    print("Cleaned up test files.")

if __name__ == "__main__":
    asyncio.run(test_regeneration_workflow())