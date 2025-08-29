import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging
import openai
import ast
import re
import sys

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Confirm
    rich_available = True
    console = Console()
except ImportError:
    rich_available = False
    console = None

logger = logging.getLogger(__name__)

class ROSToolSystem:
    """
    Advanced tool system for ROS development using OpenAI function calling.
    Provides file operations, code generation, debugging, and ROS-specific utilities.
    """
    



    def __init__(self, openai_api_key: str, use_azure: bool = False, 
                 azure_endpoint: str = None, api_version: str = None):
        try:
            if use_azure:
                from .config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION
                endpoint = azure_endpoint or AZURE_OPENAI_ENDPOINT
                version = api_version or AZURE_OPENAI_API_VERSION
                
                if not endpoint:
                    raise ValueError("Azure endpoint is required when use_azure=True")
                
                self.client = openai.AzureOpenAI(
                    api_key=openai_api_key,
                    azure_endpoint=endpoint,
                    api_version=version
                )
            else:
                self.client = openai.OpenAI(api_key=openai_api_key)
            
            self.workspace_root = os.path.expanduser("~/ros_workspace")
            self.ensure_workspace()
        except Exception as e:
            raise Exception(f"Failed to initialize ROSToolSystem: {str(e)}")
        
    def ensure_workspace(self):
        """Ensure workspace directory exists"""
        os.makedirs(self.workspace_root, exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "src"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "launch"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "config"), exist_ok=True)


    #added this fucntion 
    def run_shell_commands(self, commands: str) -> dict:
        try:
            result = subprocess.run(commands, shell=True, check=True, capture_output=True, text=True)
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": str(e)
            }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Return the OpenAI function definitions for all available tools"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string", 
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file (creates new file or overwrites existing)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path where to write the file"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            },
                            "create_directories": {
                                "type": "boolean",
                                "description": "Whether to create parent directories if they don't exist",
                                "default": True
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_in_files",
                    "description": "Search for text patterns in files within a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in"
                            },
                            "pattern": {
                                "type": "string",
                                "description": "Text pattern to search for (supports regex)"
                            },
                            "file_extensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "File extensions to include in search (e.g., ['.py', '.cpp'])"
                            },
                            "is_regex": {
                                "type": "boolean",
                                "description": "Whether the pattern is a regex",
                                "default": False
                            }
                        },
                        "required": ["directory", "pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute a shell command and return the output",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Shell command to execute"
                            },
                            "working_directory": {
                                "type": "string",
                                "description": "Working directory for the command",
                                "default": None
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Timeout in seconds",
                                "default": 30
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_code",
                    "description": "Analyze code for syntax errors, style issues, and ROS best practices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the code file to analyze"
                            },
                            "language": {
                                "type": "string",
                                "enum": ["python", "cpp"],
                                "description": "Programming language of the file"
                            },
                            "check_ros_patterns": {
                                "type": "boolean",
                                "description": "Whether to check for ROS-specific patterns and best practices",
                                "default": True
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List contents of a directory with optional filtering",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Directory path to list"
                            },
                            "show_hidden": {
                                "type": "boolean",
                                "description": "Whether to show hidden files",
                                "default": False
                            },
                            "file_extensions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by file extensions"
                            },
                            "recursive": {
                                "type": "boolean", 
                                "description": "Whether to list recursively",
                                "default": False
                            }
                        },
                        "required": ["directory"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file_lines",
                    "description": "Edit specific lines of a file. Provide a dict of line numbers (as strings) to new content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to edit"
                            },
                            "edits": {
                                "type": "object",
                                "description": "Dictionary of line numbers (as strings) to new content (preserve spaces and newlines)",
                                "additionalProperties": {"type": "string"}
                            }
                        },
                        "required": ["file_path", "edits"]
                    }
                }
            }
        ]

    def _display_tool_call(self, tool_name, arguments):
        msg = f"[TOOL] Using: {tool_name} with arguments: {json.dumps(arguments, indent=2)}"
        if rich_available:
            panel = Panel(msg, title=f"🔧 Tool Call: {tool_name}", border_style="cyan")
            console.print(panel)
        else:
            print(f"\n==== TOOL CALL: {tool_name} ====")
            print(json.dumps(arguments, indent=2))
            print("==============================\n")

    def _ask_permission_for_file_change(self, tool_name, arguments):
        file_path = arguments.get("file_path") or arguments.get("directory") or arguments.get("package_name")
        msg = f"The tool [bold yellow]{tool_name}[/bold yellow] wants to make changes to [bold green]{file_path}[/bold green]."
        if rich_available:
            panel = Panel(msg, title="⚠️ File Change Permission", border_style="yellow")
            console.print(panel)
            return Confirm.ask("Allow this change?", default=True)
        else:
            resp = input(f"[!] {tool_name} wants to change {file_path}. Allow? [y/N]: ")
            return resp.strip().lower() in ("y", "yes")

    def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool function and return the result, with real-time display and permission for file changes"""
        self._display_tool_call(tool_name, arguments)
        file_changing_tools = ["write_file", "edit_file_lines"]
        if tool_name in file_changing_tools:
            if not self._ask_permission_for_file_change(tool_name, arguments):
                deny_msg = f"[User denied permission for {tool_name} on {arguments.get('file_path', arguments.get('directory', ''))}]"
                if rich_available:
                    console.print(Panel(deny_msg, title="❌ Change Denied", border_style="red"))
                else:
                    print(deny_msg)
                return {"error": "User denied permission for this file change."}
        try:
            if tool_name == "read_file":
                return self.read_file(**arguments)
            elif tool_name == "write_file":
                return self.write_file(**arguments)
            elif tool_name == "search_in_files":
                return self.search_in_files(**arguments)
            elif tool_name == "run_command":
                return self.run_command(**arguments)
            elif tool_name == "analyze_code":
                return self.analyze_code(**arguments)
            elif tool_name == "list_directory":
                return self.list_directory(**arguments)
            elif tool_name == "edit_file_lines":
                return self.edit_file_lines(**arguments)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file contents and return lines with line numbers"""
        try:
            expanded_path = os.path.expanduser(file_path)
            if not os.path.exists(expanded_path):
                return {"error": f"File not found: {file_path}"}
            
            with open(expanded_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Build a dict of line numbers (as strings) to line content (preserving spaces and newlines)
            numbered_lines = {str(i+1): line for i, line in enumerate(lines)}
            content = ''.join(lines)
            stat = os.stat(expanded_path)
            
            return {
                "success": True,
                "content": content,
                "file_path": expanded_path,
                "size": stat.st_size,
                "lines": len(lines),
                "encoding": "utf-8",
                "numbered_lines": numbered_lines
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def write_file(self, file_path: str, content: str, create_directories: bool = True) -> Dict[str, Any]:
        """Write content to file"""
        try:
            expanded_path = os.path.expanduser(file_path)
            
            if create_directories:
                os.makedirs(os.path.dirname(expanded_path), exist_ok=True)
            
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": expanded_path,
                "bytes_written": len(content.encode('utf-8')),
                "lines_written": len(content.splitlines())
            }
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}

    def search_in_files(self, directory: str, pattern: str, 
                       file_extensions: Optional[List[str]] = None,
                       is_regex: bool = False) -> Dict[str, Any]:
        """Search for patterns in files"""
        try:
            expanded_dir = os.path.expanduser(directory)
            if not os.path.exists(expanded_dir):
                return {"error": f"Directory not found: {directory}"}
            
            results = []
            
            # Prepare pattern
            if is_regex:
                compiled_pattern = re.compile(pattern, re.IGNORECASE)
            else:
                compiled_pattern = re.compile(re.escape(pattern), re.IGNORECASE)
            
            # Walk through directory
            for root, dirs, files in os.walk(expanded_dir):
                for file in files:
                    # Filter by extensions if specified
                    if file_extensions:
                        if not any(file.endswith(ext) for ext in file_extensions):
                            continue
                    
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        
                        file_matches = []
                        for line_num, line in enumerate(lines, 1):
                            if compiled_pattern.search(line):
                                file_matches.append({
                                    "line_number": line_num,
                                    "line_content": line.rstrip('\n'),
                                    "match_positions": [m.span() for m in compiled_pattern.finditer(line)]
                                })
                        
                        if file_matches:
                            results.append({
                                "file_path": file_path,
                                "relative_path": os.path.relpath(file_path, expanded_dir),
                                "matches": file_matches,
                                "match_count": len(file_matches)
                            })
                    
                    except Exception as e:
                        logger.warning(f"Could not search in {file_path}: {e}")
            
            return {
                "success": True,
                "pattern": pattern,
                "directory": expanded_dir,
                "files_with_matches": len(results),
                "total_matches": sum(r["match_count"] for r in results),
                "results": results
            }
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}

    def run_command(self, command: str, working_directory: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """Execute shell command"""
        try:
            import subprocess
            
            cwd = os.path.expanduser(working_directory) if working_directory else None
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": True,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "working_directory": cwd or os.getcwd()
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Command execution failed: {str(e)}"}

    def analyze_code(self, file_path: str, language: Optional[str] = None, 
                    check_ros_patterns: bool = True) -> Dict[str, Any]:
        """Analyze code for issues and ROS patterns"""
        try:
            expanded_path = os.path.expanduser(file_path)
            if not os.path.exists(expanded_path):
                return {"error": f"File not found: {file_path}"}
            
            with open(expanded_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect language if not provided
            if not language:
                if file_path.endswith('.py'):
                    language = 'python'
                elif file_path.endswith(('.cpp', '.hpp', '.cc', '.h')):
                    language = 'cpp'
                else:
                    language = 'unknown'
            
            issues = []
            suggestions = []
            
            if language == 'python':
                issues.extend(self._analyze_python_code(content))
            elif language == 'cpp':
                issues.extend(self._analyze_cpp_code(content))
            
            if check_ros_patterns:
                ros_analysis = self._analyze_ros_patterns(content, language)
                issues.extend(ros_analysis.get('issues', []))
                suggestions.extend(ros_analysis.get('suggestions', []))
            
            return {
                "success": True,
                "file_path": expanded_path,
                "language": language,
                "issues": issues,
                "suggestions": suggestions,
                "lines_analyzed": len(content.splitlines())
            }
        except Exception as e:
            return {"error": f"Code analysis failed: {str(e)}"}

    def _analyze_python_code(self, content: str) -> List[Dict[str, Any]]:
        """Analyze Python code for syntax and style issues"""
        issues = []
        
        try:
            # Check syntax
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "line": e.lineno,
                "message": str(e),
                "severity": "error"
            })
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if len(line) > 120:
                issues.append({
                    "type": "line_length",
                    "line": i,
                    "message": f"Line too long ({len(line)} characters)",
                    "severity": "warning"
                })
            
            if line.rstrip() != line:
                issues.append({
                    "type": "trailing_whitespace",
                    "line": i,
                    "message": "Trailing whitespace",
                    "severity": "info"
                })
        
        return issues

    def _analyze_cpp_code(self, content: str) -> List[Dict[str, Any]]:
        """Analyze C++ code for basic issues"""
        issues = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            # Basic checks
            if len(line) > 120:
                issues.append({
                    "type": "line_length",
                    "line": i,
                    "message": f"Line too long ({len(line)} characters)",
                    "severity": "warning"
                })
            
            # Check for missing semicolons (basic heuristic)
            if line.strip() and not line.strip().endswith((';', '{', '}', ':', '//', '/*', '*/', '#')):
                if any(keyword in line for keyword in ['return', 'int ', 'double ', 'float ', 'std::']):
                    issues.append({
                        "type": "possible_missing_semicolon",
                        "line": i,
                        "message": "Possible missing semicolon",
                        "severity": "warning"
                    })
        
        return issues

    def _analyze_ros_patterns(self, content: str, language: str) -> Dict[str, List]:
        """Analyze ROS-specific patterns and best practices"""
        issues = []
        suggestions = []
        
        # Check for ROS imports/includes
        if language == 'python':
            if 'rospy' in content or 'rclpy' in content:
                if 'rospy.init_node' not in content and 'rclpy.init' not in content:
                    issues.append({
                        "type": "ros_initialization",
                        "message": "ROS node not properly initialized",
                        "severity": "error"
                    })
                
                if 'rospy.spin' not in content and 'rclpy.spin' not in content:
                    suggestions.append({
                        "type": "ros_spin",
                        "message": "Consider adding rospy.spin() or rclpy.spin() to keep node alive"
                    })
        
        elif language == 'cpp':
            if 'ros/ros.h' in content or 'rclcpp/rclcpp.hpp' in content:
                if 'ros::init' not in content and 'rclcpp::init' not in content:
                    issues.append({
                        "type": "ros_initialization", 
                        "message": "ROS node not properly initialized",
                        "severity": "error"
                    })
        
        return {"issues": issues, "suggestions": suggestions}

    def list_directory(self, directory: str, show_hidden: bool = False,
                      file_extensions: Optional[List[str]] = None,
                      recursive: bool = False) -> Dict[str, Any]:
        """List directory contents with filtering"""
        try:
            expanded_dir = os.path.expanduser(directory)
            if not os.path.exists(expanded_dir):
                return {"error": f"Directory not found: {directory}"}
            
            if not os.path.isdir(expanded_dir):
                return {"error": f"Path is not a directory: {directory}"}
            
            results = []
            
            if recursive:
                for root, dirs, files in os.walk(expanded_dir):
                    # Filter hidden directories if needed
                    if not show_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if not show_hidden and file.startswith('.'):
                            continue
                        
                        if file_extensions and not any(file.endswith(ext) for ext in file_extensions):
                            continue
                        
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, expanded_dir)
                        stat = os.stat(file_path)
                        
                        results.append({
                            "name": file,
                            "path": file_path,
                            "relative_path": rel_path,
                            "type": "file",
                            "size": stat.st_size,
                            "modified": stat.st_mtime
                        })
            else:
                for item in os.listdir(expanded_dir):
                    if not show_hidden and item.startswith('.'):
                        continue
                    
                    item_path = os.path.join(expanded_dir, item)
                    stat = os.stat(item_path)
                    
                    is_dir = os.path.isdir(item_path)
                    
                    if not is_dir and file_extensions:
                        if not any(item.endswith(ext) for ext in file_extensions):
                            continue
                    
                    results.append({
                        "name": item,
                        "path": item_path,
                        "relative_path": item,
                        "type": "directory" if is_dir else "file",
                        "size": stat.st_size if not is_dir else None,
                        "modified": stat.st_mtime
                    })
            
            # Sort results
            results.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return {
                "success": True,
                "directory": expanded_dir,
                "total_items": len(results),
                "files": [r for r in results if r["type"] == "file"],
                "directories": [r for r in results if r["type"] == "directory"],
                "items": results
            }
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}

    def chat_with_tools(self, question: str, model: str = "gpt-4", max_iterations: int = 5) -> Dict[str, Any]:
        """
        Chat with OpenAI using function calling tools to help with ROS development.
        
        Args:
            question: User's question or request
            model: OpenAI model to use
            max_iterations: Maximum number of tool calls to allow
            
        Returns:
            Dictionary with the conversation and results
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are OORB, an expert ROS2 assistant with advanced file manipulation capabilities. 

You have access to powerful tools that allow you to:
- Read and write files
- Edit specific lines in files
- Search through codebases
- Run shell commands
- Analyze code for issues
- Create directory structures

When helping users:
1. Always use tools when they would be helpful (reading configs, analyzing code, etc.)
2. Provide complete, working solutions
3. Follow ROS best practices
4. Explain what you're doing with each tool call
5. Generate production-ready code with proper error handling

You work in a workspace located at ~/ros_workspace with standard ROS directory structure."""
                },
                {
                    "role": "user", 
                    "content": str(question) if question else "Hello, I need help with ROS development."
                }
            ]
            
            conversation = []
            tool_results = []
            
            for iteration in range(max_iterations):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=self.get_available_tools(),
                    tool_choice="auto",
                    temperature=0.3
                )
                
                message = response.choices[0].message
                
                # Ensure content is never null
                message_content = message.content or ""
                
                # Add the assistant message (with tool_calls if any)
                assistant_message = {
                    "role": "assistant",
                    "content": message_content
                }
                
                if message.tool_calls:
                    assistant_message["tool_calls"] = message.tool_calls
                
                messages.append(assistant_message)
                
                conversation.append({
                    "role": "assistant",
                    "content": message_content,
                    "tool_calls": []
                })
                
                # Check if the model wants to call tools
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Execute the tool
                        tool_result = self.execute_tool(function_name, function_args)
                        tool_results.append({
                            "tool": function_name,
                            "arguments": function_args,
                            "result": tool_result
                        })
                        
                        conversation[-1]["tool_calls"].append({
                            "function": function_name,
                            "arguments": function_args,
                            "result": tool_result
                        })
                        
                        # Add tool result to messages
                        tool_content = json.dumps(tool_result) if tool_result else "{}"
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_content
                        })
                    
                    # Continue the conversation to get the model's response to tool results
                    continue
                else:
                    # No more tool calls, we're done
                    break
            
            return {
                "success": True,
                "conversation": conversation,
                "tool_results": tool_results,
                "final_response": messages[-1]["content"] if messages and messages[-1].get("content") else "No response generated",
                "iterations_used": iteration + 1
            }
            
        except Exception as e:
            logger.error(f"Chat with tools failed: {e}")
            return {"error": f"Chat failed: {str(e)}"}

    def edit_file_lines(self, file_path=None, edits=None, **kwargs) -> Dict[str, Any]:
        """Edit specific lines of a file. Accepts (file_path, edits), a single dict, or kwargs.
        - If new_content is '', delete the line.
        - If new_content contains newlines, replace the line with multiple lines.
        - If new_content is whitespace or a single line, replace as is (preserving whitespace/newlines).
        Accepts both 'edits' and 'lines' as the key for the edits dictionary.
        """
        # Try to extract file_path and edits/lines from various argument formats
        # 1. If called with a single dict as the first argument
        if file_path is not None and edits is None and isinstance(file_path, dict):
            args = file_path
            file_path = args.get('file_path')
            edits = args.get('edits') or args.get('lines')
        # 2. If called with kwargs only
        if (file_path is None or edits is None):
            file_path = kwargs.get('file_path', file_path)
            edits = kwargs.get('edits') or kwargs.get('lines') or edits
        # 3. If edits is a string (e.g., from JSON), parse it
        if isinstance(edits, str):
            try:
                edits = json.loads(edits)
            except Exception:
                return {"error": "'edits' must be a dict or a JSON string representing a dict of line edits."}
        # 4. Validate
        if not file_path or not isinstance(edits, dict):
            return {"error": "edit_file_lines requires 'file_path' (str) and 'edits' (dict) or 'lines' (dict) arguments."}
        try:
            expanded_path = os.path.expanduser(file_path)
            if not os.path.exists(expanded_path):
                return {"error": f"File not found: {file_path}"}
            with open(expanded_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            # Sort line numbers descending so edits don't affect subsequent indices
            edit_items = sorted(edits.items(), key=lambda x: int(x[0]), reverse=True)
            for line_num_str, new_content in edit_items:
                idx = int(line_num_str) - 1
                if 0 <= idx < len(lines):
                    if new_content == '':
                        # Delete the line
                        del lines[idx]
                    elif '\n' in new_content:
                        # Replace with multiple lines (split, preserve newlines)
                        new_lines = [l if l.endswith('\n') else l+'\n' for l in new_content.splitlines()]
                        lines[idx:idx+1] = new_lines
                    else:
                        # Replace as is, preserve newline if original had it
                        if lines[idx].endswith('\n') and not new_content.endswith('\n'):
                            new_content += '\n'
                        lines[idx] = new_content
            with open(expanded_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return {
                "success": True,
                "file_path": expanded_path,
                "lines_edited": list(edits.keys()),
                "total_lines": len(lines)
            }
        except Exception as e:
            logger.error(f"edit_file_lines error: {e}")
            return {"error": f"Failed to edit file lines: {str(e)}"}