#!/usr/bin/env python3
"""
ML Training Init MCP Server
Sequential thinking pattern for ML training script generation
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from pathlib import Path
import subprocess
import threading
import queue
import sys

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types


class MLTrainingServer:
    """MCP Server for ML training script initialization with file locking"""
    
    def __init__(self):
        self.locked_file: Optional[str] = None
        self.checkpoints: Dict[str, Dict[str, Any]] = {}
        self.current_checkpoint: Optional[str] = None
        self.generated_files: List[str] = []
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.current_execution: Optional[subprocess.Popen] = None
        
    def create_checkpoint(self, file_path: str, content: str) -> str:
        """Create a checkpoint for rollback capability"""
        checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.checkpoints[checkpoint_id] = {
            "file_path": file_path,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.current_checkpoint = checkpoint_id
        return checkpoint_id

    async def execute_command(self, command: str, use_locked_file: bool = True) -> Dict[str, Any]:
        """Execute a flexible command with optional locked file inclusion"""
        if not self.locked_file:
            return {
                "status": "failure",
                "message": "No file is locked. Initialize a training file first."
            }
        
        # Suggest uv if .venv exists and not already using it
        if os.path.exists('.venv') and 'uv run' not in command and 'source' not in command:
            suggestion = f"Note: .venv exists at workspace root. Consider using 'uv run {command}' for better dependency management."
        else:
            suggestion = None
        
        # Build the command - if use_locked_file is True and the locked file isn't in the command, append it
        full_command = command
        if use_locked_file and self.locked_file not in command:
            # Check if command needs the file path appended
            if not command.endswith('.py'):
                full_command = f"{command} {self.locked_file}"
            else:
                full_command = command
        
        # Create execution ID
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Execute and capture output
        try:
            process = subprocess.Popen(
                full_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.current_execution = process
            
            # Capture output in real-time
            output_lines = []
            error_lines = []
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output:
                    output_lines.append(output.strip())
                
                error = process.stderr.readline()
                if error:
                    error_lines.append(error.strip())
                
                # Check if process has finished
                if output == '' and error == '' and process.poll() is not None:
                    break
            
            exit_code = process.returncode
            
            # Store execution results
            self.executions[execution_id] = {
                "command": full_command,
                "output": "\n".join(output_lines),
                "errors": "\n".join(error_lines),
                "exit_code": exit_code,
                "timestamp": datetime.now().isoformat()
            }
            
            result = {
                "status": "success" if exit_code == 0 else "failure",
                "execution_id": execution_id,
                "output": "\n".join(output_lines[-100:]),  # Last 100 lines
                "errors": "\n".join(error_lines),
                "exit_code": exit_code
            }
            if suggestion:
                result["suggestion"] = suggestion
            return result
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Execution error: {str(e)}"
            }
    
    async def fix_error_in_file(self, error_trace: str, fix_instructions: str = "") -> Dict[str, Any]:
        """Analyze error and fix it in the locked file"""
        if not self.locked_file:
            return {
                "status": "failure",
                "message": "No file is locked."
            }
        
        # Read current content
        with open(self.locked_file, 'r') as f:
            current_content = f.read()
        
        # Parse common Python errors and apply fixes
        fixes_applied = []
        modified_content = current_content
        
        # Common error patterns and fixes
        if "ModuleNotFoundError" in error_trace:
            module = error_trace.split("'")[1] if "'" in error_trace else ""
            if module:
                # Add import statement if missing
                if f"import {module}" not in modified_content and f"from {module}" not in modified_content:
                    import_line = f"import {module}\n"
                    # Add after other imports
                    lines = modified_content.split('\n')
                    import_idx = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            import_idx = i + 1
                    lines.insert(import_idx, import_line)
                    modified_content = '\n'.join(lines)
                    fixes_applied.append(f"Added missing import: {module}")
        
        elif "NameError" in error_trace:
            # Extract undefined name
            if "name '" in error_trace:
                undefined = error_trace.split("name '")[1].split("'")[0]
                fixes_applied.append(f"Detected undefined name: {undefined}")
                # Add TODO comment for manual fix
                modified_content = f"# TODO: Fix NameError - '{undefined}' is not defined\n{modified_content}"
        
        elif "SyntaxError" in error_trace:
            # Extract line number if available
            if "line " in error_trace:
                try:
                    line_num = int(error_trace.split("line ")[1].split()[0])
                    fixes_applied.append(f"Syntax error at line {line_num}")
                    # Add TODO comment
                    lines = modified_content.split('\n')
                    if 0 <= line_num - 1 < len(lines):
                        lines[line_num - 1] = f"# TODO: Fix syntax error here\n{lines[line_num - 1]}"
                        modified_content = '\n'.join(lines)
                except:
                    pass
        
        # Apply custom fix instructions if provided
        if fix_instructions:
            modified_content = f"# Applied fix: {fix_instructions}\n{modified_content}"
            fixes_applied.append(f"Applied custom fix: {fix_instructions}")
        
        # Write fixed content back to file
        if fixes_applied:
            with open(self.locked_file, 'w') as f:
                f.write(modified_content)
            
            # Create checkpoint
            checkpoint_id = self.create_checkpoint(self.locked_file, modified_content)
            
            return {
                "status": "success",
                "message": f"Applied {len(fixes_applied)} fixes",
                "fixes": fixes_applied,
                "checkpoint_id": checkpoint_id
            }
        else:
            return {
                "status": "failure",
                "message": "Could not automatically fix the error. Manual intervention needed.",
                "error_trace": error_trace
            }
    
    async def handle_initialize_training_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize_training_file tool call - Creates ONE file and locks permanently"""
        try:
            file_name = arguments["file_name"]
            content = arguments["content"]
            reference = arguments.get("reference", "")
            
            # STRICT CHECK: Ensure no file is already locked
            if self.locked_file:
                return {
                    "status": "failure",
                    "message": f"CONSTRAINT VIOLATION: Already permanently locked to file: {self.locked_file}. You CANNOT create any new files. Use enhance_code or get_current_file to work with the existing locked file only."
                }
            
            # Create the file with the provided content
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Lock to this file
            self.locked_file = file_path
            self.generated_files.append(file_path)
            
            # Store reference if provided
            if reference:
                # Could store reference metadata for tracking purposes
                pass
            
            # Create checkpoint
            checkpoint_id = self.create_checkpoint(file_path, content)
            
            return {
                "status": "success",
                "file_path": file_path,
                "checkpoint_id": checkpoint_id,
                "locked_file": file_path,
                "message": f"Successfully created and locked to {file_name}",
                "reference": reference if reference else None
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error creating training file: {str(e)}"
            }
    
    async def handle_execute_training(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute_training tool call"""
        command = arguments["command"]
        use_locked_file = arguments.get("use_locked_file", True)
        
        return await self.execute_command(command, use_locked_file)
    
    async def handle_monitor_and_fix(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle monitor_and_fix tool call"""
        error_trace = arguments["error_trace"]
        execution_id = arguments.get("execution_id")
        fix_instructions = arguments.get("fix_instructions", "")
        
        # If execution_id provided, get error from that execution
        if execution_id and execution_id in self.executions:
            stored_errors = self.executions[execution_id].get("errors", "")
            if stored_errors:
                error_trace = stored_errors
        
        return await self.fix_error_in_file(error_trace, fix_instructions)
    
    async def handle_get_current_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_current_file tool call"""
        try:
            if not self.locked_file:
                return {
                    "status": "failure",
                    "message": "No file is locked. Please initialize a training file first."
                }
            
            with open(self.locked_file, 'r') as f:
                content = f.read()
            
            return {
                "file_path": self.locked_file,
                "content": content,
                "checkpoint_id": self.current_checkpoint
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error reading file: {str(e)}"
            }


async def main():
    """Main entry point for the MCP server"""
    server = Server("ml-training-init")
    ml_server = MLTrainingServer()
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="initialize_training_file",
                description="CRITICAL: Creates ONE training file and permanently locks ALL future operations to ONLY this file. After calling this, you CANNOT create any other files - all subsequent operations MUST modify ONLY this locked file. The AI agent analyzes the reference and provides the complete training script content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "Name of the training script file (e.g., 'train.py')"
                        },
                        "content": {
                            "type": "string",
                            "description": "Complete training script content generated by the AI agent based on the reference"
                        },
                        "reference": {
                            "type": "string",
                            "description": "Reference used (GitHub URL, HuggingFace model name, or model card URL)"
                        }
                    },
                    "required": ["file_name", "content", "reference"]
                }
            ),
            types.Tool(
                name="execute_training",
                description="[DEPRECATED - Use your native Bash tool instead for better control] Legacy execution tool kept for compatibility. AI agents should use their native Bash tool to execute commands like 'uv run python train.py' or 'source .venv/bin/activate && python train.py'. This provides better control over execution, environment activation, and error handling.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Full command to execute. PREFER 'uv run python' when .venv exists. Examples: 'uv run python', 'uv run accelerate launch', 'uv run torchrun --nproc_per_node=2', 'source .venv/bin/activate && python'"
                        },
                        "use_locked_file": {
                            "type": "boolean",
                            "description": "If true, automatically appends the locked file path to command if not already present (default: true)"
                        }
                    },
                    "required": ["command"]
                }
            ),
            types.Tool(
                name="monitor_and_fix",
                description="Analyzes execution errors and fixes them in the locked file. Parses error traces and applies automated fixes where possible. ALL fixes are applied ONLY to the single locked file.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {
                            "type": "string",
                            "description": "ID of the execution to get errors from"
                        },
                        "error_trace": {
                            "type": "string",
                            "description": "Error trace to analyze and fix"
                        },
                        "fix_instructions": {
                            "type": "string",
                            "description": "Specific instructions for fixing the error"
                        }
                    },
                    "required": ["error_trace"]
                }
            ),
            types.Tool(
                name="get_current_file",
                description="Returns content of the SINGLE locked file. This is the ONLY file you can work with after initialization. Use this to read the file instead of trying to create new ones.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(
        name: str,
        arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool calls"""
        if arguments is None:
            arguments = {}
        
        result = {}
        if name == "initialize_training_file":
            result = await ml_server.handle_initialize_training_file(arguments)
        elif name == "execute_training":
            result = await ml_server.handle_execute_training(arguments)
        elif name == "monitor_and_fix":
            result = await ml_server.handle_monitor_and_fix(arguments)
        elif name == "get_current_file":
            result = await ml_server.handle_get_current_file(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ml-training-init",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
