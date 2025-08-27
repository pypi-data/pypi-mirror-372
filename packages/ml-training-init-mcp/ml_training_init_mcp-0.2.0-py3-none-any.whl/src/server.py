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
    """MCP Server for ML training script initialization with managed file system"""
    
    def __init__(self):
        # Support 1 training file + up to 2 config files
        self.managed_files: Dict[str, Any] = {
            'training': None,  # Single training script
            'configs': []      # List of config files (max 2)
        }
        self.max_config_files = 2
        self.generated_files: List[str] = []
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.current_execution: Optional[subprocess.Popen] = None
        
        # Training status tracking
        self.training_start_time: Optional[datetime] = None
        self.last_output_time: Optional[datetime] = None
        self.status_check_interval_minutes = 5  # Configurable interval
        self.hang_threshold_minutes = 3  # No output for this long = possibly hung
        
        # Output buffering for background execution
        self.output_buffer: List[str] = []
        self.error_buffer: List[str] = []
        self.max_buffer_size = 1000  # Keep last 1000 lines
        
        # For backward compatibility
        self.locked_file: Optional[str] = None
        

    async def execute_command(self, command: str, use_locked_file: bool = True, background: bool = False) -> Dict[str, Any]:
        """Execute a flexible command with optional background execution"""
        if not self.managed_files['training']:
            return {
                "status": "failure",
                "message": "No training file initialized. Initialize a training file first."
            }
        
        # Use training file as the primary file for execution
        primary_file = self.managed_files['training']
        
        # Suggest uv if .venv exists and not already using it
        if os.path.exists('.venv') and 'uv run' not in command and 'source' not in command:
            suggestion = f"Note: .venv exists at workspace root. Consider using 'uv run {command}' for better dependency management."
        else:
            suggestion = None
        
        # Build the command - if use_locked_file is True and the primary file isn't in the command, append it
        full_command = command
        if use_locked_file and primary_file not in command:
            # Check if command needs the file path appended
            if not command.endswith('.py'):
                full_command = f"{command} {primary_file}"
            else:
                full_command = command
        
        # Create execution ID
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Track training start time
        self.training_start_time = datetime.now()
        self.last_output_time = datetime.now()
        
        # Clear buffers for new execution
        self.output_buffer = []
        self.error_buffer = []
        
        # Execute and capture output
        try:
            import fcntl
            import select
            
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
            
            # Store initial execution info
            self.executions[execution_id] = {
                "command": full_command,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "pid": process.pid
            }
            
            # If background mode, return immediately
            if background:
                # Set pipes to non-blocking
                fcntl.fcntl(process.stdout, fcntl.F_SETFL, 
                           fcntl.fcntl(process.stdout, fcntl.F_GETFL) | os.O_NONBLOCK)
                fcntl.fcntl(process.stderr, fcntl.F_SETFL,
                           fcntl.fcntl(process.stderr, fcntl.F_GETFL) | os.O_NONBLOCK)
                
                return {
                    "status": "started",
                    "execution_id": execution_id,
                    "pid": process.pid,
                    "message": f"Training started in background with PID {process.pid}",
                    "command": full_command
                }
            
            # Blocking mode (original behavior)
            output_lines = []
            error_lines = []
            
            while True:
                output = process.stdout.readline()
                if output:
                    output_lines.append(output.strip())
                    self.output_buffer.append(output.strip())
                    if len(self.output_buffer) > self.max_buffer_size:
                        self.output_buffer.pop(0)
                    self.last_output_time = datetime.now()
                
                error = process.stderr.readline()
                if error:
                    error_lines.append(error.strip())
                    self.error_buffer.append(error.strip())
                    if len(self.error_buffer) > self.max_buffer_size:
                        self.error_buffer.pop(0)
                    self.last_output_time = datetime.now()
                
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
                "status": "completed" if exit_code == 0 else "failed",
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
    
    async def fix_error_in_file(self, error_trace: str, fix_instructions: str = "", file_name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze error and return context for AI-driven regeneration"""
        # Determine which file to analyze
        target_file = None
        if file_name:
            # Check if file_name is managed
            if self.managed_files['training'] and os.path.basename(self.managed_files['training']) == file_name:
                target_file = self.managed_files['training']
            else:
                for config_file in self.managed_files['configs']:
                    if os.path.basename(config_file) == file_name:
                        target_file = config_file
                        break
            if not target_file:
                return {
                    "status": "failure",
                    "message": f"File '{file_name}' is not a managed file."
                }
        else:
            # Default to training file
            if not self.managed_files['training']:
                return {
                    "status": "failure",
                    "message": "No training file initialized."
                }
            target_file = self.managed_files['training']
        
        # Read current content
        with open(target_file, 'r') as f:
            current_content = f.read()
        
        # Parse error for context
        error_analysis = {
            "type": "unknown",
            "details": {},
            "line_number": None
        }
        
        # Analyze error type and extract details
        if "ModuleNotFoundError" in error_trace:
            module = error_trace.split("'")[1] if "'" in error_trace else ""
            error_analysis["type"] = "ModuleNotFoundError"
            error_analysis["details"]["missing_module"] = module
            error_analysis["suggestion"] = f"Add 'import {module}' or install the module"
        
        elif "NameError" in error_trace:
            if "name '" in error_trace:
                undefined = error_trace.split("name '")[1].split("'")[0]
                error_analysis["type"] = "NameError"
                error_analysis["details"]["undefined_name"] = undefined
                error_analysis["suggestion"] = f"Define '{undefined}' or import it"
        
        elif "SyntaxError" in error_trace:
            error_analysis["type"] = "SyntaxError"
            if "line " in error_trace:
                try:
                    line_num = int(error_trace.split("line ")[1].split()[0])
                    error_analysis["line_number"] = line_num
                except:
                    pass
            error_analysis["suggestion"] = "Fix syntax error in the code"
        
        elif "TypeError" in error_trace:
            error_analysis["type"] = "TypeError"
            if "missing" in error_trace.lower() and "argument" in error_trace.lower():
                error_analysis["details"]["issue"] = "missing_argument"
                error_analysis["suggestion"] = "Add missing arguments to function call"
        
        elif "AttributeError" in error_trace:
            error_analysis["type"] = "AttributeError"
            if "has no attribute" in error_trace:
                parts = error_trace.split("has no attribute")
                if len(parts) > 1:
                    attr = parts[1].strip().strip("'\"")
                    error_analysis["details"]["missing_attribute"] = attr
            error_analysis["suggestion"] = "Check attribute name or object type"
        
        # Return context for AI to regenerate the file
        return {
            "status": "needs_ai_regeneration",
            "current_code": current_content,
            "error_trace": error_trace,
            "error_analysis": error_analysis,
            "fix_instructions": fix_instructions,
            "file_path": target_file,
            "file_name": os.path.basename(target_file),
            "message": "AI agent should analyze this context and regenerate the corrected code using regenerate_file_with_fixes tool"
        }
    
    async def handle_initialize_training_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize_training_file tool call - Creates the main training file"""
        try:
            file_name = arguments["file_name"]
            content = arguments["content"]
            reference = arguments.get("reference", "")
            
            # Check if training file already exists
            if self.managed_files['training']:
                return {
                    "status": "failure",
                    "message": f"Training file already initialized: {self.managed_files['training']}. Use get_managed_files or get_file_content to work with existing files."
                }
            
            # Create the file with the provided content
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Store as training file
            self.managed_files['training'] = file_path
            self.locked_file = file_path  # Backward compatibility
            self.generated_files.append(file_path)
            
            # Store reference if provided
            if reference:
                # Could store reference metadata for tracking purposes
                pass
            
            return {
                "status": "success",
                "file_path": file_path,
                "file_type": "training",
                "message": f"Successfully created training file: {file_name}",
                "reference": reference if reference else None,
                "managed_files": {
                    "training": file_name,
                    "configs": [os.path.basename(f) for f in self.managed_files['configs']]
                }
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error creating training file: {str(e)}"
            }
    
    async def handle_execute_training(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle execute_training tool call - defaults to background execution"""
        command = arguments["command"]
        use_locked_file = arguments.get("use_locked_file", True)
        background = arguments.get("background", True)  # Default to background mode
        
        return await self.execute_command(command, use_locked_file, background)
    
    async def handle_monitor_and_fix(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle monitor_and_fix tool call"""
        error_trace = arguments["error_trace"]
        execution_id = arguments.get("execution_id")
        fix_instructions = arguments.get("fix_instructions", "")
        file_name = arguments.get("file_name")  # Optional: specify which file to fix
        
        # If execution_id provided, get error from that execution
        if execution_id and execution_id in self.executions:
            stored_errors = self.executions[execution_id].get("errors", "")
            if stored_errors:
                error_trace = stored_errors
        
        return await self.fix_error_in_file(error_trace, fix_instructions, file_name)
    
    async def handle_create_config_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_config_file tool call - Creates config files (max 2)"""
        try:
            file_name = arguments["file_name"]
            content = arguments["content"]
            config_type = arguments.get("config_type", "general")
            
            # Check if we've reached max config files
            if len(self.managed_files['configs']) >= self.max_config_files:
                return {
                    "status": "failure",
                    "message": f"Cannot create more config files. Maximum {self.max_config_files} config files allowed. Current configs: {[os.path.basename(f) for f in self.managed_files['configs']]}"
                }
            
            # Validate file extension for common config types
            valid_extensions = ['.yaml', '.yml', '.json', '.toml', '.ini', '.env', '.config', '.conf']
            if not any(file_name.endswith(ext) for ext in valid_extensions + ['.py', '.txt']):
                return {
                    "status": "warning",
                    "message": f"Unusual config file extension. Common extensions: {valid_extensions}"
                }
            
            # Create the config file
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Add to managed configs
            self.managed_files['configs'].append(file_path)
            self.generated_files.append(file_path)
            
            return {
                "status": "success",
                "file_path": file_path,
                "file_type": "config",
                "config_type": config_type,
                "message": f"Successfully created config file: {file_name}",
                "managed_files": {
                    "training": os.path.basename(self.managed_files['training']) if self.managed_files['training'] else None,
                    "configs": [os.path.basename(f) for f in self.managed_files['configs']]
                }
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error creating config file: {str(e)}"
            }
    
    async def handle_get_managed_files(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_managed_files tool call - Returns all managed files"""
        try:
            result = {
                "status": "success",
                "managed_files": {
                    "training": None,
                    "configs": []
                }
            }
            
            # Add training file info
            if self.managed_files['training']:
                result["managed_files"]["training"] = {
                    "file_name": os.path.basename(self.managed_files['training']),
                    "file_path": self.managed_files['training']
                }
            
            # Add config files info  
            for config_path in self.managed_files['configs']:
                result["managed_files"]["configs"].append({
                    "file_name": os.path.basename(config_path),
                    "file_path": config_path
                })
            
            result["message"] = f"Found {1 if self.managed_files['training'] else 0} training file and {len(self.managed_files['configs'])} config file(s)"
            
            return result
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error retrieving managed files: {str(e)}"
            }
    
    async def handle_get_file_content(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_file_content tool call - Get content of a specific managed file"""
        try:
            file_name = arguments["file_name"]
            
            # Find the file in managed files
            target_file = None
            file_type = None
            
            # Check training file
            if self.managed_files['training'] and os.path.basename(self.managed_files['training']) == file_name:
                target_file = self.managed_files['training']
                file_type = "training"
            
            # Check config files
            if not target_file:
                for config_path in self.managed_files['configs']:
                    if os.path.basename(config_path) == file_name:
                        target_file = config_path
                        file_type = "config"
                        break
            
            if not target_file:
                return {
                    "status": "failure",
                    "message": f"File '{file_name}' is not a managed file. Use get_managed_files to see available files."
                }
            
            # Read file content
            with open(target_file, 'r') as f:
                content = f.read()
            
            return {
                "status": "success",
                "file_name": file_name,
                "file_path": target_file,
                "file_type": file_type,
                "content": content
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error reading file: {str(e)}"
            }
    
    async def handle_get_current_file(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_current_file tool call - Returns the training file content"""
        try:
            if not self.managed_files['training']:
                return {
                    "status": "failure",
                    "message": "No training file initialized. Please initialize a training file first."
                }
            
            with open(self.managed_files['training'], 'r') as f:
                content = f.read()
            
            return {
                "file_path": self.managed_files['training'],
                "content": content
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error reading file: {str(e)}"
            }
    
    async def handle_regenerate_file_with_fixes(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle regenerate_file_with_fixes tool call - Replace file with AI-corrected version"""
        try:
            file_name = arguments["file_name"]
            new_content = arguments["new_content"]
            backup = arguments.get("backup", True)
            
            # Find the target file
            target_file = None
            if self.managed_files['training'] and os.path.basename(self.managed_files['training']) == file_name:
                target_file = self.managed_files['training']
                file_type = "training"
            else:
                for config_file in self.managed_files['configs']:
                    if os.path.basename(config_file) == file_name:
                        target_file = config_file
                        file_type = "config"
                        break
            
            if not target_file:
                return {
                    "status": "failure",
                    "message": f"File '{file_name}' is not a managed file."
                }
            
            # Backup original if requested
            backup_path = None
            if backup and os.path.exists(target_file):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{target_file}.backup_{timestamp}"
                with open(target_file, 'r') as src:
                    original_content = src.read()
                with open(backup_path, 'w') as dst:
                    dst.write(original_content)
            
            # Write new content
            with open(target_file, 'w') as f:
                f.write(new_content)
            
            # Reset training state for fresh start
            self.training_start_time = None
            self.current_execution = None
            
            return {
                "status": "success",
                "message": f"Successfully regenerated {file_type} file with fixes",
                "file_path": target_file,
                "file_name": file_name,
                "backup_path": backup_path if backup_path else None,
                "note": "Training state reset for fresh execution"
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error regenerating file: {str(e)}"
            }
    
    async def handle_update_hyperparameters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_hyperparameters tool call - Return context for AI to regenerate with new params"""
        try:
            updates = arguments["updates"]  # Dict of param updates like {"epochs": 2, "batch_size": 8}
            file_name = arguments.get("file_name")
            
            # Determine target file
            if file_name:
                if self.managed_files['training'] and os.path.basename(self.managed_files['training']) == file_name:
                    target_file = self.managed_files['training']
                else:
                    # Check configs
                    target_file = None
                    for config_file in self.managed_files['configs']:
                        if os.path.basename(config_file) == file_name:
                            target_file = config_file
                            break
                    if not target_file:
                        return {
                            "status": "failure",
                            "message": f"File '{file_name}' is not a managed file."
                        }
            else:
                # Default to training file
                if not self.managed_files['training']:
                    return {
                        "status": "failure",
                        "message": "No training file initialized."
                    }
                target_file = self.managed_files['training']
            
            # Read current content
            with open(target_file, 'r') as f:
                current_content = f.read()
            
            # Return context for AI regeneration
            return {
                "status": "needs_ai_update",
                "current_content": current_content,
                "requested_updates": updates,
                "file_path": target_file,
                "file_name": os.path.basename(target_file),
                "message": "AI agent should regenerate the code with updated hyperparameters using regenerate_file_with_fixes tool",
                "suggestions": [
                    "For faster feedback during development, consider:",
                    "- epochs: 1-3 for quick testing",
                    "- batch_size: smaller values (8-16) for faster iterations",
                    "- learning_rate: start with default, adjust if needed",
                    "- max_steps: limit to 10-50 for initial testing"
                ]
            }
            
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Error preparing hyperparameter update: {str(e)}"
            }
    
    def read_process_output(self) -> Dict[str, Any]:
        """Read available output from running process without blocking"""
        if not self.current_execution:
            return {"stdout": [], "stderr": []}
        
        import select
        new_output = []
        new_errors = []
        
        try:
            # Check if there's data to read from stdout
            while True:
                ready, _, _ = select.select([self.current_execution.stdout], [], [], 0)
                if ready:
                    line = self.current_execution.stdout.readline()
                    if line:
                        stripped = line.strip()
                        new_output.append(stripped)
                        self.output_buffer.append(stripped)
                        if len(self.output_buffer) > self.max_buffer_size:
                            self.output_buffer.pop(0)
                        self.last_output_time = datetime.now()
                    else:
                        break
                else:
                    break
            
            # Check if there's data to read from stderr
            while True:
                ready, _, _ = select.select([self.current_execution.stderr], [], [], 0)
                if ready:
                    line = self.current_execution.stderr.readline()
                    if line:
                        stripped = line.strip()
                        new_errors.append(stripped)
                        self.error_buffer.append(stripped)
                        if len(self.error_buffer) > self.max_buffer_size:
                            self.error_buffer.pop(0)
                        self.last_output_time = datetime.now()
                    else:
                        break
                else:
                    break
        except Exception:
            pass  # Process might have ended
        
        return {"stdout": new_output, "stderr": new_errors}
    
    async def handle_get_training_output(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_training_output tool call - Get recent output from running training"""
        try:
            lines = arguments.get("lines", 50)  # Default to last 50 lines
            
            # Check if training is running
            if not self.current_execution:
                return {
                    "status": "no_execution",
                    "message": "No training is currently running"
                }
            
            # Read any new output
            new_data = self.read_process_output()
            
            # Check process status
            poll_result = self.current_execution.poll()
            if poll_result is not None:
                status = "completed" if poll_result == 0 else "failed"
            else:
                status = "running"
            
            # Get recent output
            recent_output = self.output_buffer[-lines:] if len(self.output_buffer) > 0 else []
            recent_errors = self.error_buffer[-lines:] if len(self.error_buffer) > 0 else []
            
            return {
                "status": status,
                "recent_output": recent_output,
                "recent_errors": recent_errors,
                "new_output": new_data["stdout"],
                "new_errors": new_data["stderr"],
                "total_output_lines": len(self.output_buffer),
                "total_error_lines": len(self.error_buffer),
                "pid": self.current_execution.pid if self.current_execution else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting training output: {str(e)}"
            }
    
    async def handle_check_training_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle check_training_status tool call - Simple time tracker"""
        try:
            # Optional: allow custom interval
            interval_minutes = arguments.get("interval_minutes", self.status_check_interval_minutes)
            
            # Check if training has started
            if not self.training_start_time:
                return {
                    "status": "not_started",
                    "message": "No training execution has been started yet"
                }
            
            # Calculate elapsed time
            elapsed = datetime.now() - self.training_start_time
            elapsed_minutes = elapsed.total_seconds() / 60
            
            # Read any new output from the process
            if self.current_execution:
                self.read_process_output()
            
            # Check if process is still running
            base_status = "still_running"
            if self.current_execution:
                poll_result = self.current_execution.poll()
                if poll_result is not None:
                    base_status = "completed" if poll_result == 0 else "failed"
            
            # Check for potential hang (no output for threshold time)
            last_output_minutes_ago = None
            suggestion_type = "none"
            
            if self.last_output_time and base_status == "still_running":
                output_elapsed = datetime.now() - self.last_output_time
                last_output_minutes_ago = output_elapsed.total_seconds() / 60
                
                # Determine if it's hung or just slow
                if last_output_minutes_ago > self.hang_threshold_minutes:
                    base_status = "possibly_hung"
                    suggestion_type = "check_for_hang"
                elif elapsed_minutes > interval_minutes:
                    suggestion_type = "reduce_hyperparameters"
            
            # Build response message
            message = f"Training has been running for {elapsed_minutes:.1f} minutes"
            
            # Add interval-based message
            intervals_passed = int(elapsed_minutes // interval_minutes)
            if intervals_passed > 0 and base_status in ["still_running", "possibly_hung"]:
                message += f" ({intervals_passed} x {interval_minutes} minute intervals passed)"
            
            # Add hang detection message
            if last_output_minutes_ago and last_output_minutes_ago > 1:
                message += f", no output for {last_output_minutes_ago:.1f} minutes"
            
            result = {
                "status": base_status,
                "elapsed_time_minutes": round(elapsed_minutes, 2),
                "interval_minutes": interval_minutes,
                "intervals_passed": intervals_passed,
                "suggestion_type": suggestion_type,
                "message": message,
                "training_start_time": self.training_start_time.isoformat() if self.training_start_time else None
            }
            
            # Add output timing info if available
            if last_output_minutes_ago is not None:
                result["last_output_minutes_ago"] = round(last_output_minutes_ago, 2)
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking training status: {str(e)}"
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
                description="[ML TRAINING WORKFLOW] Creates the main training script file for machine learning model training. This is the primary file that will be executed. After creation, you can also add up to 2 config files if needed. AI agent should use this when setting up ML training workflows.",
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
                description="[ML TRAINING WORKFLOW] Execute training script with tracking. Runs in background by default, allowing you to monitor progress. AI determines the best command based on setup (e.g., 'uv run python', 'python', 'accelerate launch'). Returns immediately with execution_id for monitoring.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Command to execute. Examples: 'uv run python' (preferred with .venv), 'python', 'accelerate launch', 'torchrun --nproc_per_node=2'"
                        },
                        "use_locked_file": {
                            "type": "boolean",
                            "description": "Auto-append training file path if not in command (default: true)"
                        },
                        "background": {
                            "type": "boolean",
                            "description": "Run in background for monitoring (default: true)",
                            "default": true
                        }
                    },
                    "required": ["command"]
                }
            ),
            types.Tool(
                name="get_training_output",
                description="[ML TRAINING WORKFLOW] Get recent output from running training. Call this periodically to see training logs, metrics, and errors. Works with background execution from execute_training.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "lines": {
                            "type": "number",
                            "description": "Number of recent lines to return (default: 50)",
                            "default": 50
                        }
                    }
                }
            ),
            types.Tool(
                name="create_config_file",
                description="[ML TRAINING WORKFLOW] Creates a configuration file for the ML training setup. Supports YAML, JSON, TOML, .env and other config formats. Maximum 2 config files allowed per training session. Use this for hyperparameters, model configs, or environment settings.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "Name of config file (e.g., 'config.yaml', 'hyperparams.json', '.env')"
                        },
                        "content": {
                            "type": "string",
                            "description": "Configuration file content"
                        },
                        "config_type": {
                            "type": "string",
                            "description": "Type of configuration (e.g., 'hyperparameters', 'model_config', 'environment')"
                        }
                    },
                    "required": ["file_name", "content"]
                }
            ),
            types.Tool(
                name="get_managed_files",
                description="[ML TRAINING WORKFLOW] Returns list of all managed files in the current ML training session (training script + config files). Use this to see what files are available.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="get_file_content",
                description="[ML TRAINING WORKFLOW] Get the content of a specific managed file by name. Works for both training script and config files.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "Name of the file to read (e.g., 'train.py', 'config.yaml')"
                        }
                    },
                    "required": ["file_name"]
                }
            ),
            types.Tool(
                name="monitor_and_fix",
                description="[ML TRAINING WORKFLOW] Analyzes execution errors and returns context for AI regeneration. Parses error details and provides current code for AI to regenerate corrected version. Use with regenerate_file_with_fixes to apply fixes.",
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
                        },
                        "file_name": {
                            "type": "string",
                            "description": "Specific file to fix (optional, defaults to training file)"
                        }
                    },
                    "required": ["error_trace"]
                }
            ),
            types.Tool(
                name="get_current_file",
                description="[ML TRAINING WORKFLOW] Returns content of the main training file. Quick access to the primary training script.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="check_training_status",
                description="[ML TRAINING WORKFLOW] Check training status with hang detection. Returns elapsed time, last output time, and suggestions. Detects if training is slow (needs hyperparameter reduction) or possibly hung (no output for 3+ minutes). AI agents use this to decide whether to adjust parameters or check for hangs.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "interval_minutes": {
                            "type": "number",
                            "description": "Check interval in minutes (default: 5). Used to determine if adjustments might be needed."
                        }
                    }
                }
            ),
            types.Tool(
                name="regenerate_file_with_fixes",
                description="[ML TRAINING WORKFLOW] Replace managed file with AI-corrected version. Used after monitor_and_fix identifies issues. AI provides complete regenerated code. Automatically backs up original and resets training state for fresh execution.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "Name of the file to regenerate (e.g., 'train.py')"
                        },
                        "new_content": {
                            "type": "string",
                            "description": "Complete regenerated content with fixes applied by AI"
                        },
                        "backup": {
                            "type": "boolean",
                            "description": "Whether to backup original file (default: true)"
                        }
                    },
                    "required": ["file_name", "new_content"]
                }
            ),
            types.Tool(
                name="update_hyperparameters",
                description="[ML TRAINING WORKFLOW] Request hyperparameter updates for faster feedback. Returns current code and requested changes for AI to regenerate. Use when training takes too long and you need to reduce epochs, batch_size, or other parameters for quicker iteration.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of parameter updates (e.g., {'epochs': 2, 'batch_size': 8})"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "File to update (optional, defaults to training file)"
                        }
                    },
                    "required": ["updates"]
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
        elif name == "create_config_file":
            result = await ml_server.handle_create_config_file(arguments)
        elif name == "execute_training":
            result = await ml_server.handle_execute_training(arguments)
        elif name == "get_training_output":
            result = await ml_server.handle_get_training_output(arguments)
        elif name == "monitor_and_fix":
            result = await ml_server.handle_monitor_and_fix(arguments)
        elif name == "get_managed_files":
            result = await ml_server.handle_get_managed_files(arguments)
        elif name == "get_file_content":
            result = await ml_server.handle_get_file_content(arguments)
        elif name == "get_current_file":
            result = await ml_server.handle_get_current_file(arguments)
        elif name == "check_training_status":
            result = await ml_server.handle_check_training_status(arguments)
        elif name == "regenerate_file_with_fixes":
            result = await ml_server.handle_regenerate_file_with_fixes(arguments)
        elif name == "update_hyperparameters":
            result = await ml_server.handle_update_hyperparameters(arguments)
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
