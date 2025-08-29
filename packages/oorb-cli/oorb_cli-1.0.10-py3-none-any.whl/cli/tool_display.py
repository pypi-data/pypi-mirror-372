#!/usr/bin/env python3
"""
Enhanced tool execution display with animations and detailed descriptions
"""

import time
import json
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.spinner import Spinner
import threading

console = Console()

class ToolExecutionDisplay:
    """Enhanced display system for tool execution with animations"""
    
    def __init__(self):
        self.tool_descriptions = {
            "read_file": {
                "description": "Reading file contents from filesystem",
                "action": "Analyzing file structure and content",
                "details": "Loads file with UTF-8 encoding, provides metadata"
            },
            "write_file": {
                "description": "Writing content to file",
                "action": "Creating/updating file with new content",
                "details": "Atomic write operation with directory creation"
            },
            "edit_file_lines": {
                "description": "Editing specific lines in file",
                "action": "Performing line-by-line modifications",
                "details": "Supports replace, insert, delete operations"
            },
            "list_directory": {
                "description": "Listing directory contents",
                "action": "Scanning filesystem structure",
                "details": "Recursive scan with file filtering capabilities"
            },
            "search_in_files": {
                "description": "Searching for patterns in files",
                "action": "Pattern matching across file contents", 
                "details": "Regex and text search with context"
            },
            "generate_ros_node": {
                "description": "Generating ROS node code",
                "action": "Creating production-ready ROS node",
                "details": "Full node with publishers, subscribers, services"
            },
            "generate_launch_file": {
                "description": "Creating ROS launch configuration",
                "action": "Building launch file structure",
                "details": "Multi-node launch with parameters"
            },
            "create_ros_package": {
                "description": "Creating ROS package structure",
                "action": "Setting up package hierarchy",
                "details": "Package.xml, CMake, directory structure"
            },
            "run_command": {
                "description": "Executing shell command",
                "action": "Running system command",
                "details": "Subprocess execution with timeout"
            },
            "analyze_code": {
                "description": "Analyzing code quality and patterns",
                "action": "Performing static code analysis", 
                "details": "Syntax, style, and ROS pattern checking"
            }
        }
    
    def animate_tool_execution(self, tool_name: str, arguments: Dict[str, Any], 
                             result: Dict[str, Any], duration: float = 2.0):
        """Create animated display of tool execution"""
        
        tool_info = self.tool_descriptions.get(tool_name, {
            "description": f"Executing {tool_name}",
            "action": "Processing request",
            "details": "Generic tool execution"
        })
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = Text(f"{tool_info['icon']} OORB Tool Execution", style="bold cyan")
        layout["header"].update(Align.center(header_text))
        
        # Main content with tool details
        main_panel = self._create_tool_panel(tool_name, tool_info, arguments, result)
        layout["main"].update(main_panel)
        
        # Footer with progress
        footer_text = Text(" Processing...", style="yellow")
        layout["footer"].update(Align.center(footer_text))
        
        # Animate
        with Live(layout, console=console, refresh_per_second=10) as live:
            # Simulate execution phases
            phases = [
                (" Initializing...", 0.3),
                ("  Processing arguments...", 0.4), 
                (" Executing tool...", 0.8),
                (" Completing operation...", 0.3),
                (" Analyzing results...", 0.2)
            ]
            
            for phase_text, phase_duration in phases:
                footer_text = Text(phase_text, style="yellow")
                layout["footer"].update(Align.center(footer_text))
                live.update(layout)
                time.sleep(phase_duration)
            
            # Final result
            if result.get("success"):
                footer_text = Text(" Tool execution completed successfully!", style="green")
            else:
                footer_text = Text(" Tool execution failed!", style="red")
            
            layout["footer"].update(Align.center(footer_text))
            layout["main"].update(self._create_result_panel(tool_name, tool_info, arguments, result))
            live.update(layout)
            time.sleep(1.0)
    
    def _create_tool_panel(self, tool_name: str, tool_info: Dict[str, Any], 
                          arguments: Dict[str, Any], result: Dict[str, Any]) -> Panel:
        """Create detailed tool information panel"""
        
        # Create table for tool details
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value", style="white")
        
        table.add_row("Tool", f"{tool_info['icon']} {tool_name}")
        table.add_row("Description", tool_info['description'])
        table.add_row("Action", tool_info['action'])
        table.add_row("Details", tool_info['details'])
        
        # Add key arguments
        if arguments:
            table.add_row("", "")  # Spacer
            table.add_row("Arguments", "")
            for key, value in arguments.items():
                if isinstance(value, (str, int, float, bool)):
                    display_value = str(value)
                    if len(display_value) > 50:
                        display_value = display_value[:47] + "..."
                    table.add_row(f"  {key}", display_value)
                elif isinstance(value, (list, dict)):
                    table.add_row(f"  {key}", f"{type(value).__name__} with {len(value)} items")
        
        return Panel(
            table,
            title=f"🔧 Tool Execution: {tool_name}",
            border_style="blue",
            padding=(1, 2)
        )
    
    def _create_result_panel(self, tool_name: str, tool_info: Dict[str, Any],
                           arguments: Dict[str, Any], result: Dict[str, Any]) -> Panel:
        """Create result display panel"""
        
        # Create table for results
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value", style="white")
        
        # Status
        if result.get("success"):
            table.add_row("Status", " Success")
        else:
            table.add_row("Status", " Failed")
            if result.get("error"):
                table.add_row("Error", str(result["error"])[:100])
        
        # Tool-specific result details
        if tool_name == "read_file" and result.get("success"):
            table.add_row("File Size", f"{result.get('size', 0)} bytes")
            table.add_row("Lines", str(result.get('lines', 0)))
            table.add_row("Encoding", result.get('encoding', 'unknown'))
        
        elif tool_name == "write_file" and result.get("success"):
            table.add_row("Bytes Written", str(result.get('bytes_written', 0)))
            table.add_row("Lines Written", str(result.get('lines_written', 0)))
        
        elif tool_name == "edit_file_lines" and result.get("success"):
            table.add_row("Operations", f"{result.get('operations_performed', 0)}/{result.get('operations_requested', 0)}")
            table.add_row("Line Changes", str(result.get('line_difference', 0)))
            if result.get('changes_made'):
                table.add_row("Changes", f"{len(result['changes_made'])} modifications")
        
        elif tool_name == "list_directory" and result.get("success"):
            table.add_row("Total Items", str(result.get('total_items', 0)))
            table.add_row("Files", str(len(result.get('files', []))))
            table.add_row("Directories", str(len(result.get('directories', []))))
        
        elif tool_name == "search_in_files" and result.get("success"):
            table.add_row("Files Found", str(result.get('files_with_matches', 0)))
            table.add_row("Total Matches", str(result.get('total_matches', 0)))
        
        elif tool_name == "generate_ros_node" and result.get("success"):
            table.add_row("Node Name", result.get('node_name', ''))
            table.add_row("Language", result.get('language', ''))
            table.add_row("ROS Version", result.get('ros_version', ''))
            table.add_row("Content Size", f"{result.get('content_length', 0)} chars")
        
        # LLM Processing Analysis
        table.add_row("", "")  # Spacer
        table.add_row("LLM Analysis", "")
        table.add_row("  Reasoning", self._analyze_llm_reasoning(tool_name, arguments, result))
        table.add_row("  Next Steps", self._predict_next_steps(tool_name, arguments, result))
        
        border_style = "green" if result.get("success") else "red"
        title = f" Results: {tool_name}"
        
        return Panel(
            table,
            title=title,
            border_style=border_style,
            padding=(1, 2)
        )
    
    def _analyze_llm_reasoning(self, tool_name: str, arguments: Dict[str, Any], 
                              result: Dict[str, Any]) -> str:
        """Analyze why the LLM called this tool"""
        
        reasoning_map = {
            "list_directory": "Exploring workspace structure to understand project layout",
            "read_file": "Examining file contents to understand current implementation",
            "edit_file_lines": "Modifying specific lines based on user requirements", 
            "write_file": "Creating new file with generated content",
            "search_in_files": "Looking for specific patterns or references in codebase",
            "generate_ros_node": "Creating ROS node as requested by user",
            "generate_launch_file": "Setting up launch configuration for ROS system",
            "create_ros_package": "Establishing proper ROS package structure",
            "run_command": "Executing system command for build/test operations",
            "analyze_code": "Checking code quality and ROS compliance"
        }
        
        base_reasoning = reasoning_map.get(tool_name, "Performing requested operation")
        
        # Add context-specific analysis
        if tool_name == "list_directory" and "navigation_pkg" in arguments.get("directory", ""):
            return f"{base_reasoning} - Focusing on navigation package structure"
        
        return base_reasoning
    
    def _predict_next_steps(self, tool_name: str, arguments: Dict[str, Any],
                           result: Dict[str, Any]) -> str:
        """Predict what the LLM might do next"""
        
        if tool_name == "list_directory" and result.get("success"):
            if result.get("files"):
                return "Likely to read existing files to understand current implementation"
            else:
                return "May create new files or examine package structure"
        
        elif tool_name == "read_file" and result.get("success"):
            return "Will analyze content and suggest modifications or improvements"
        
        elif tool_name == "edit_file_lines" and result.get("success"):
            return "May test changes or create additional complementary files"
        
        elif tool_name == "generate_ros_node" and result.get("success"):
            return "Likely to create launch files or additional supporting code"
        
        elif tool_name == "search_in_files" and result.get("success"):
            return "Will use findings to inform code generation or modifications"
        
        return "Continue with user's requested workflow"
    
    def display_tool_sequence(self, tool_calls: List[Dict[str, Any]]):
        """Display a sequence of tool calls with relationships"""
        
        console.print("\n" + "="*80)
        console.print("[bold cyan]🔧 OORB Tool Execution Sequence[/bold cyan]")
        console.print("="*80)
        
        for i, tool_call in enumerate(tool_calls, 1):
            tool_name = tool_call.get("tool", "unknown")
            arguments = tool_call.get("arguments", {})
            result = tool_call.get("result", {})
            
            console.print(f"\n[bold blue]Step {i}: {tool_name}[/bold blue]")
            
            # Show tool execution animation
            self.animate_tool_execution(tool_name, arguments, result)
            
            # Show relationship to previous tools
            if i > 1:
                relationship = self._analyze_tool_relationship(tool_calls[i-2], tool_call)
                console.print(f"[dim]🔗 Relationship: {relationship}[/dim]")
            
            time.sleep(0.5)  # Brief pause between tools
        
        console.print(f"\n[bold green]✅ Completed {len(tool_calls)} tool operations[/bold green]")
        console.print("="*80)
    
    def _analyze_tool_relationship(self, prev_tool: Dict[str, Any], 
                                  curr_tool: Dict[str, Any]) -> str:
        """Analyze relationship between consecutive tool calls"""
        
        prev_name = prev_tool.get("tool", "")
        curr_name = curr_tool.get("tool", "")
        
        relationships = {
            ("list_directory", "read_file"): "Discovered files, now examining content",
            ("read_file", "edit_file_lines"): "Analyzed existing code, making targeted changes",
            ("read_file", "write_file"): "Based on existing file, creating new version",
            ("search_in_files", "edit_file_lines"): "Found patterns, now modifying code",
            ("generate_ros_node", "generate_launch_file"): "Created node, now setting up launch",
            ("create_ros_package", "generate_ros_node"): "Package ready, adding node implementation",
            ("edit_file_lines", "run_command"): "Code modified, testing changes",
        }
        
        return relationships.get((prev_name, curr_name), "Sequential workflow step")

# Example usage function
def demo_tool_display():
    """Demonstrate the tool execution display system"""
    
    display = ToolExecutionDisplay()
    
    # Simulate some tool calls
    sample_tools = [
        {
            "tool": "list_directory",
            "arguments": {"directory": "/home/fayez/ros_workspace/src/navigation_pkg"},
            "result": {"success": True, "total_items": 5, "files": ["node.py"], "directories": ["scripts"]}
        },
        {
            "tool": "read_file", 
            "arguments": {"file_path": "/home/fayez/ros_workspace/src/navigation_pkg/scripts/random_coords_publisher.py"},
            "result": {"success": True, "size": 740, "lines": 25, "encoding": "utf-8"}
        },
        {
            "tool": "edit_file_lines",
            "arguments": {
                "file_path": "/home/fayez/ros_workspace/src/navigation_pkg/scripts/random_coords_publisher.py",
                "edits": [{"line_number": 5, "operation": "replace", "new_content": "# Enhanced ROS node"}]
            },
            "result": {"success": True, "operations_performed": 1, "line_difference": 0}
        }
    ]
    
    display.display_tool_sequence(sample_tools)

if __name__ == "__main__":
    demo_tool_display()