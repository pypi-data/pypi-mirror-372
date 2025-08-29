#!/usr/bin/env python3

import argparse
import logging
import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.spinner import Spinner
from rich.live import Live
import time
import threading


from .oorb_qa_system import ROSQASystem
from .config import (
    AZURE_OPENAI_MODELS, OLLAMA_MODELS, AZURE_OPENAI_API_KEY, OPENAI_API_KEY, OPENAI_MODELS, RETRIEVAL_API_BASE_URL,
    get_best_available_backend, get_default_model_for_backend,
    check_backend_availability, validate_config, get_available_backends,
    SUPPORTED_ROS_DISTROS, USER_ROS_DISTRO, get_retrieval_endpoint
)


import time
from .tool_display import ToolExecutionDisplay

#config functions 
from .config import ROS_Distro, get_ubuntu_version, is_ros_installed, get_available_backends


# Setup logging
logging.basicConfig(level=logging.ERROR)  # Only show errors
logger = logging.getLogger(__name__)

console = Console()
tool_display = ToolExecutionDisplay()

# Available models from your configuration
LLM_BACKENDS = ["azure", "openai", "ollama"]

stop_event = threading.Event()
query_result = {}


class ROSChatbotCLI:
    def __init__(self, retrieval_endpoint: str = None):
        self.qa_system = None
        self.retrieval_endpoint = retrieval_endpoint
        # Auto-initialize the system
        self._load_system()

    def _load_system(self):
        """Load QA system"""
        try:
            from .config import get_retrieval_endpoint
            endpoint = get_retrieval_endpoint(self.retrieval_endpoint)
            
            # Initialize QA system with updated parameters
            self.qa_system = ROSQASystem(
                use_retrieval=True,
                collection_name="beaglemind_w_chonkie",
                enable_tools=True,
                retrieval_api_url=endpoint
            )
        except Exception as e:
            # If loading fails, system won't be available
            console.print(f"[yellow]Warning: Could not load system: {e}[/yellow]")
            self.qa_system = None

    def check_initialization(self) -> bool:
        """Check if the system is available"""
        if not self.qa_system:
            console.print("[yellow]⚠ ROS Chatbot system is not available. Please check your configuration.[/yellow]")
            return False
        return True

    def list_models(self, backend: str = None):
        """List available models for specified backend or all backends"""
        table = Table(title="Available ROS Chatbot Models")
        table.add_column("Backend", style="cyan", no_wrap=True)
        table.add_column("Model Name", style="magenta")
        table.add_column("Type", style="green") 
        table.add_column("Status", style="yellow")

        def add_models_to_table(backend_name: str, models: List[str], model_type: str):
            for model in models:
                # Check if model is available (basic check)
                status = self._check_model_availability(backend_name, model)
                table.add_row(backend_name.upper(), model, model_type, status)

        if backend:
            backend = backend.lower()
            if backend == "azure":
                add_models_to_table("azure", AZURE_OPENAI_MODELS, "Cloud")
            elif backend == "openai":
                add_models_to_table("openai", OPENAI_MODELS, "Cloud")
            elif backend == "ollama":
                add_models_to_table("ollama", OLLAMA_MODELS, "Local")
            else:
                console.print(f"[red]Unknown backend: {backend}. Available: {', '.join(LLM_BACKENDS)}[/red]")
                return
        else:
            # Show all backends
            add_models_to_table("azure", AZURE_OPENAI_MODELS, "Cloud")
            add_models_to_table("openai", OPENAI_MODELS, "Cloud")
            add_models_to_table("ollama", OLLAMA_MODELS, "Local")

        console.print(table)

    def _check_model_availability(self, backend: str, model: str) -> str:
        """Check if a model is available (basic check)"""
        try:

            if backend.lower() == "azure":
                # Check if Azure OpenAI API key is set
                if AZURE_OPENAI_API_KEY:
                    return "✓ Available"
                else:
                    return "✗ No API Key"
            elif backend.lower() == "openai":
                # Check if OpenAI API key is set
                if OPENAI_API_KEY:
                    return "✓ Available"
                else:
                    return "✗ No API Key"
            elif backend.lower() == "ollama":
                # Try to ping Ollama service
                import requests
                try:
                    response = requests.get("http://localhost:11434/api/tags", timeout=2)
                    if response.status_code == 200:
                        # Check if model is actually available
                        tags = response.json()
                        available_models = [tag.get("name", "") for tag in tags.get("models", [])]
                        if any(model in available_model for available_model in available_models):
                            return "✓ Available"
                        else:
                            return "⚠ Not Downloaded"
                    else:
                        return "✗ Service Down"
                except:
                    return "✗ Service Down"
            return "? Unknown"
        except Exception:
            return "? Unknown"

    def chat(self, prompt: str, backend: str = None, model: str = None,
             temperature: float = None, use_tools: bool = None, distro: str = None):
        """Chat with ROS Chatbot using the specified parameters"""

        if not self.check_initialization():
            return

        # Validate and set ROS distro
        from .config import validate_ros_distro, ROS_Distro, get_ros_distro_info
        
        if distro:
            is_valid, message = validate_ros_distro(distro)
            if not is_valid:
                console.print(f"[red]Error: {message}[/red]")
                return
            current_distro = distro.lower()
            console.print(f"[cyan] Using ROS distro: {current_distro.upper()}[/cyan]")
        else:
            current_distro = ROS_Distro()
            if current_distro:
                console.print(f"[dim] Auto-detected ROS distro: {current_distro.upper()}[/dim]")
            else:
                console.print("[yellow]  No ROS distro detected. Specify with --distro or set OORB_ROS_DISTRO[/yellow]")

        if not prompt.strip():
            console.print("[red]Error: Prompt cannot be empty[/red]")
            return

        available_backends = get_available_backends()
        backends_str = ", ".join(available_backends)
        backend_model = get_default_model_for_backend(available_backends[0]) if available_backends else None
        # Use provided parameters or defaults
        backend = backend_model  or "not configured"   

        model = model or AZURE_OPENAI_MODELS[0]
        temperature = temperature if temperature is not None else 0.3

        if backend == "azure":
            azure_model_mapping = {
                "gpt-4o-mini": "gpt-4o-mini",
                "gpt-3.5-turbo": "gpt-35-turbo",
                "gpt-4-turbo": "gpt-4"
            }
            if model in azure_model_mapping:
                original_model = model
                model = azure_model_mapping[model]
                console.print(f"[dim] Mapped {original_model} → {model} for Azure[/dim]")

        # Determine if tools should be used
        if backend in ["azure", "openai"]:
            has_tool_system = self.qa_system and self.qa_system.tool_system is not None
            has_openai_access = self.qa_system and self.qa_system.openai_client is not None
            use_tools = use_tools if use_tools is not None else (has_tool_system and has_openai_access)

            if not has_tool_system:
                console.print(f"[dim]  Tool system not available for {backend}[/dim]")
            elif not has_openai_access:
                console.print(f"[dim]  OpenAI client not available for {backend}[/dim]")
        else:
            use_tools = False

        # Check if the selected backend is available
        backend_available, backend_msg = check_backend_availability(backend)
        if not backend_available:
            console.print(f"[red]Error: {backend_msg}[/red]")

            # Try to fall back to an available backend
            available_backend = get_best_available_backend()
            if available_backend != backend:
                console.print(f"[yellow]Falling back to {available_backend.upper()} backend...[/yellow]")
                backend = available_backend
                model = get_default_model_for_backend(backend)
                if backend not in ["azure", "openai"]:
                    use_tools = False
            else:
                console.print(f"[red]No backends available. Please set API keys or ensure Ollama is running.[/red]")
                return

        # Validate backend and model
        if backend not in LLM_BACKENDS:
            console.print(f"[red]Error: Invalid backend '{backend}'. Available: {', '.join(LLM_BACKENDS)}[/red]")
            return

        if backend == "azure":
            available_models = AZURE_OPENAI_MODELS
        elif backend == "openai":
            available_models = OPENAI_MODELS
        else:
            available_models = OLLAMA_MODELS

        if model not in available_models:
            console.print(f"[red]Error: Model '{model}' not available for backend '{backend}'[/red]")
            console.print(f"Available models: {', '.join(available_models)}")
            return

        # Show OORB ASCII art
        console.print("""
[bold cyan]
 ██████╗  ██████╗ ██████╗ ██████╗
██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗
██║   ██║██║   ██║██████╔╝██████╔╝
██║   ██║██║   ██║██╔══██╗██╔══██╗
╚██████╔╝╚██████╔╝██║  ██║██████╔╝
 ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝
[/bold cyan]
        """)

        # Show query info
        query_info = (
            f"[bold]Query:[/bold] {prompt}\n"
            f"[dim]Backend:[/dim] {backend.upper()}\n"
            f"[dim]Model:[/dim] {model}\n"
            f"[dim]Temperature:[/dim] {temperature}\n"
            f"[dim]Tools:[/dim] {' Enabled' if use_tools else ' Disabled'}\n"
            f"[dim]Retrieval:[/dim] {' Enabled' if self.qa_system.use_retrieval else ' Disabled'}"
        )
        
        query_panel = Panel(
            query_info,
            title=" Processing ROS Query",
            border_style="blue"
        )
        console.print(query_panel)

        try:
            # Show spinner while processing
            spinner_text = " Generating ROS response with advanced tools..." if use_tools else " Generating ROS response with context retrieval..."
            
            #with console.status(f"[bold green]{spinner_text}[/bold green]", spinner="dots"):
                # Use unified ask_question method
            result = self.qa_system.ask_question(
                question=prompt,
                model_name=model,
                temperature=temperature,
                llm_backend=backend,
                use_context=True,
                context_filters=None,
                max_context_chunks=5,
                expand_query=True,
                enable_tools=use_tools,
                max_tool_iterations=5,
                distro=current_distro
            )

            answer = result.get("answer", "No answer generated.")

            # Check if distro selection is needed
            if result.get("need_distro_selection"):
                distro_panel = Panel(
                    f"[yellow] ROS2 Distro Selection Required[/yellow]\n\n"
                    f"{answer}\n\n"
                    f"[bold]Available distros:[/bold] {', '.join(result.get('available_distros', []))}\n\n"
                    f"[dim]Please specify a distro in your next question (e.g., 'in humble' or 'for jazzy')[/dim]",
                    title=" OORB Response",
                    border_style="yellow"
                )
                console.print(distro_panel)
                return

            # Display tool execution sequence if tools were used
            if result.get("used_tools") and result.get("tool_calls"):
                console.print("\n[bold yellow] Tool Execution Analysis[/bold yellow]")
                tool_display.display_tool_sequence(result["tool_calls"])

            # Display answer with nice formatting
            console.print("\n" + "="*60)
            console.print(f"[bold green] OORB Response:[/bold green]")
            console.print("="*60)
            console.print(Markdown(answer))
            console.print("="*60)

            # Show tool usage information if tools were used
            if result.get("used_tools") and result.get("tool_calls"):
                tools_used = len(result["tool_calls"])
                iterations = result.get("iterations_used", 0)

                tools_panel = Panel(
                    f" Used {tools_used} tool{'s' if tools_used != 1 else ''} across {iterations} iteration{'s' if iterations != 1 else ''}\n" +
                    "\n".join([f"• {call['tool']} - {call['result'].get('success', 'Failed')}"
                              for call in result["tool_calls"][:5]]) +
                    (f"\n... and {tools_used - 5} more" if tools_used > 5 else ""),
                    title="  Tool Usage",
                    border_style="cyan"
                )
                console.print(tools_panel)

            # Show retrieval information if available
            if result.get("used_retrieval") and result.get("context_sources"):
                sources_info = f" Used {result.get('total_context_chunks', 0)} context sources"
                if result.get('context_quality'):
                    sources_info += f" (Quality: {result['context_quality']:.2f})"
                
                # Add distro information if available
                if result.get('selected_distro'):
                    sources_info += f"\n ROS2 Distro: [cyan]{result['selected_distro'].upper()}[/cyan]"
                    if result.get('distro_detected'):
                        sources_info += " [dim](auto-detected)[/dim]"
                    else:
                        sources_info += " [dim](user specified)[/dim]"

                # Handle context_sources properly
                context_sources = result.get('context_sources', [])
                source_lines = []
                
                for i, source in enumerate(context_sources[:3]):
                    if isinstance(source, dict):
                        source_name = source.get('file_name', 'Unknown')
                        source_score = source.get('score', 0.0)
                        source_lines.append(f"• {source_name} (Score: {source_score:.3f})")
                    else:
                        source_lines.append(f"• {source}")

                sources_panel = Panel(
                    sources_info + "\n" + "\n".join(source_lines),
                    title=" Knowledge Sources",
                    border_style="green"
                )
                console.print(sources_panel)

        except Exception as e:
            console.print(f"[red] Error during chat: {e}[/red]")
    
    def interactive_chat(self, backend: str = None, model: str = None,
                        temperature: float = None, use_tools: bool = None, distro: str = None):
        """Start an interactive chat session with the ROS Chatbot"""
   
        # Available data from config 
        available_backends = get_available_backends()
        backend_model = get_default_model_for_backend(available_backends[0]) if available_backends else None
    
        # Use provided parameters or defaults

        backend = backend or (available_backends[0] if available_backends else "not configured")

        model = backend_model
        temperature = temperature if temperature is not None else 0.3
        ros_distro = ROS_Distro() or "ROS is not initialized"

        # Auto-correct model for Azure backend
        if backend == "azure":
            azure_model_mapping = {
                "gpt-4o-mini": "gpt-4o-mini",
                "gpt-3.5-turbo": "gpt-35-turbo",
                "gpt-4-turbo": "gpt-4"
            }
            if model in azure_model_mapping:
                original_model = model
                model = azure_model_mapping[model]
                console.print(f"[dim] Mapped {original_model} → {model} for Azure[/dim]")

        # Determine if tools should be used
        if backend in ["azure", "openai"]:
            has_tool_system = self.qa_system and self.qa_system.tool_system is not None
            has_openai_access = self.qa_system and self.qa_system.openai_client is not None
            
            # Match the behavior of chat method - default to False
            use_tools = use_tools if use_tools is not None else False
            
            if not has_tool_system:
                console.print(f"[dim]  Tool system not available for {backend}[/dim]")
            elif not has_openai_access:
                console.print(f"[dim]  OpenAI client not available for {backend}[/dim]")
            elif has_tool_system and has_openai_access and not use_tools:
                console.print(f"[dim]  Tools available but disabled. Use /tools to enable[/dim]")
        else:
            use_tools = False

        # Show welcome banner
        console.print("""
[bold cyan]
 ██████╗  ██████╗ ██████╗ ██████╗     ██████╗██╗  ██╗ █████╗ ████████╗
██╔═══██╗██╔═══██╗██╔══██╗██╔══██╗   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝
██║   ██║██║   ██║██████╔╝██████╔╝   ██║     ███████║███████║   ██║
██║   ██║██║   ██║██╔══██╗██╔══██╗   ██║     ██╔══██║██╔══██║   ██║
╚██████╔╝╚██████╔╝██║  ██║██████╔╝   ╚██████╗██║  ██║██║  ██║   ██║
 ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═════╝     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
[/bold cyan]

[bold yellow] Welcome to OORB Interactive Chat![/bold yellow]
[dim]Your intelligent assistant for ROS2 development[/dim]
        """)

        # Show session configuration
        backend_model = get_default_model_for_backend(available_backends[0]) if available_backends else None
        session_panel = Panel(
            f"[bold]Session Configuration:[/bold]\n"
            f"[dim]Backend:[/dim] {backend}\n"
            f"[dim]Model:[/dim] {model}\n"
            f"[dim]Temperature:[/dim] {temperature}\n"
            f"[dim]ROS Distro:[/dim] {ros_distro.upper()}\n"
            f"[dim]Tools:[/dim] {' Enabled' if use_tools else ' Disabled'}\n"
            f"[dim]Retrieval:[/dim] {' Enabled' if self.qa_system.use_retrieval else ' Disabled'}",
            title=" Active Configuration",
            border_style="blue"
        )
        console.print(session_panel)

        # Show help information
        help_panel = Panel(
            "[bold]Commands:[/bold]\n"
            "• Type your ROS questions naturally\n"
            "• [cyan]/help[/cyan] - Show this help\n"
            "• [cyan]/clear[/cyan] - Clear screen\n"
            "• [cyan]/config[/cyan] - Show current configuration\n"
            "• [cyan]/tools[/cyan] - Toggle tool usage (if available)\n"
            "• [cyan]/exit[/cyan] or [cyan]/quit[/cyan] - Exit chat\n"
            "• [cyan]Ctrl+C[/cyan] - Force exit\n\n"
            "[bold]Example questions:[/bold]\n"
            "• Create a ROS2 publisher node for sensor data\n"
            "• How do I setup a launch file for multiple nodes?\n"
            "• Generate a package for robot navigation",
            title=" Quick Help",
            border_style="green"
        )
        console.print(help_panel)

        console.print("\n[bold green] Chat started! Ask me anything about ROS2...[/bold green]")
        console.print("[dim]Tip: Be specific about your ROS distro and what you want to accomplish![/dim]\n")
        console.print("[dim]Tip: Press Ctrl+C during query processing to cancel and start a new question![/dim]\n")
       
        def check_for_interruption(stop_event):
            """Check for Ctrl+C during query processing"""
            try:
                while not stop_event.is_set():
                    time.sleep(0.1)  # Check every 100ms
            except KeyboardInterrupt:
                console.print("\n[yellow]⏹  Query cancelled by user[/yellow]")
                stop_event.set()
                return True
            return False

        # Chat loop
        conversation_count = 0
        try:
            while True:
                try:
                    # Get user input
                    prompt = console.input(f"[bold cyan]You[{conversation_count + 1}]:[/bold cyan] ")

                    if not prompt.strip():
                        continue

                    # Handle special commands
                    if prompt.lower() in ['/exit', '/quit']:
                        console.print("[yellow] Thanks for using OORB! Goodbye![/yellow]")
                        break
                    elif prompt.lower() == '/help':
                        console.print(help_panel)
                        continue
                    elif prompt.lower() == '/clear':
                        os.system('clear' if os.name == 'posix' else 'cls')
                        console.print("[green] Screen cleared![/green]")
                        continue
                    elif prompt.lower() == '/config':
                        console.print(session_panel)
                        continue
                    elif prompt.lower() == '/tools':
                        if backend in ["azure", "openai"]:
                            #use_tools = not use_tools
                            status = " Enabled" if use_tools else " Disabled"
                            console.print(f"[cyan] Tools: {status}[/cyan]")
                        else:
                            console.print("[yellow]  Tools not available for this backend[/yellow]")
                        continue

                    conversation_count += 1

                    # Process the question
                    console.print(f"\n[bold green] OORB[{conversation_count}]:[/bold green]")

                    stop_event = threading.Event()
                    query_result = {}
                    query_cancelled = False
                        
                    def run_query():
                        try:    
                            result = self.qa_system.ask_question(
                                question=prompt,
                                model_name=model,
                                temperature=temperature,
                                llm_backend=backend,
                                use_context=True,
                                context_filters=None,
                                max_context_chunks=5,
                                expand_query=True,
                                enable_tools=use_tools,
                                max_tool_iterations=5,
                                distro=None,
                                stop_event=stop_event
                            )
                            query_result.update(result)
                        except Exception as e:
                            if stop_event.is_set():
                                query_result["cancelled"] = True
                            else:
                                query_result["error"] = str(e)


                    #start thread 
                    query_thread = threading.Thread(target=run_query, daemon=True)
                    console.print("[dim] Processing your question... (Press Ctrl+C to cancel)[/dim]")
                    query_thread.start()

                   # Wait for completion or cancellation
                    try:
                        while query_thread.is_alive():
                            time.sleep(0.1)
                            if stop_event.is_set():
                                break
                    except KeyboardInterrupt:
                        console.print("\n[yellow]⏹  Cancelling query...[/yellow]")
                        stop_event.set()
                        query_cancelled = True
                        
                        # Wait a bit for graceful shutdown
                        query_thread.join(timeout=2)
                        if query_thread.is_alive():
                            console.print("[red]  Query may still be running in background[/red]")
                        
                        console.print("[green] Ready for your next question![/green]\n")
                        continue

                    # Handle timeout
                    if query_thread.is_alive():
                        console.print("[yellow] Query taking longer than expected, cancelling...[/yellow]")
                        stop_event.set()
                        query_thread.join(timeout=5)
                        console.print("[green] Ready for your next question![/green]\n")
                        continue

                    # Handle cancellation
                    if query_result.get("cancelled") or stop_event.is_set():
                        console.print("[yellow]⏹  Query was cancelled[/yellow]")
                        console.print("[green] Ready for your next question![/green]\n")
                        continue

                    # Handle errors
                    if "error" in query_result:
                        console.print(f"[red] An error occurred: {query_result['error']}[/red]")
                        console.print("[green] Ready for your next question![/green]\n")
                        continue

                    result = query_result
                    answer = result.get("answer", "No answer generated.")
                    
                    # Check if distro selection is needed
                    if result.get("need_distro_selection"):
                        distro_panel = Panel(
                            f"[yellow] ROS2 Distro Selection Required[/yellow]\n\n"
                            f"{answer}\n\n"
                            f"[bold]Available distros:[/bold] {', '.join(result.get('available_distros', []))}\n\n"
                            f"[dim]Please specify a distro in your next question (e.g., 'in humble' or 'for jazzy')[/dim]",
                            title=" OORB Response",
                            border_style="yellow"
                        )
                        console.print(distro_panel)
                        continue
                    
                    console.print(Markdown(answer))

                    # Show tool execution if tools were used
                    if result.get("used_tools") and result.get("tool_calls"):
                        console.print("\n[bold cyan] Tool Execution Summary[/bold cyan]")
                        # Show compact tool summary for interactive mode
                        for i, tool_call in enumerate(result["tool_calls"], 1):
                            tool_name = tool_call.get("tool")
                            tool_result = tool_call.get("result", {})
                            status = "Success" if tool_result.get("success") else "Failed"
                            console.print(f"  {i}. {status} {tool_name}")

                    # Show compact tool/context info
                    info_parts = []
                    if result.get("used_tools") and result.get("tool_calls"):
                        tools_used = len(result["tool_calls"])
                        successful_tools = sum(1 for call in result["tool_calls"] if call["result"].get("success"))
                        info_parts.append(f" Tools: {successful_tools}/{tools_used}")

                    if result.get("used_retrieval") and result.get("total_context_chunks", 0) > 0:
                        chunks = result.get("total_context_chunks", 0)
                        quality = result.get("context_quality", 0)
                        distro_info = ""
                        if result.get("selected_distro"):
                            distro_info = f" | Distro: {result['selected_distro'].upper()}"
                        info_parts.append(f" Context: {chunks} chunks (Q:{quality:.2f}){distro_info}")

                    if info_parts:
                        console.print(f"[dim]{' | '.join(info_parts)}[/dim]")

                    console.print()  # Add spacing

                except KeyboardInterrupt:
                    console.print("\n[yellow]  Use /exit to quit gracefully, or Ctrl+C again to force exit[/yellow]")
                    try:
                        response = console.input("[dim]Press Enter to continue or type 'exit': [/dim]")
                        if response.lower() in ['exit', 'quit']:
                            break
                    except KeyboardInterrupt:
                        console.print("\n[red] Force exit. Goodbye![/red]")
                        break
                    continue
                except EOFError:
                    console.print("\n[yellow] Session ended. Goodbye![/yellow]")
                    break
                except Exception as e:
                    console.print(f"\n[red] An error occurred: {e}[/red]")
                    console.print("[dim]You can continue chatting or type /exit to quit[/dim]")
                    continue

        except Exception as e:
            console.print(f"\n[red] Chat session error: {e}[/red]")

        # Session summary
        if conversation_count > 0:
            console.print(f"\n[bold blue] Session Summary:[/bold blue]")
            console.print(f"[dim]• Conversations: {conversation_count}[/dim]")
            console.print(f"[dim]• Configuration: {backend.upper()} | {model} | Tools: {'Success' if use_tools else 'failed'}[/dim]")

        console.print("[green] Thanks for using OORB! Happy ROS development! [/green]")

@click.group()
@click.version_option(version="1.0.9", prog_name="ROS Chatbot CLI")
def cli():
    """
     OORB CLI - Intelligent Assistant for ROS and ROS2
    Enhanced with Vector Search & Retrieval Augmented Generation
    """
    pass

@cli.command("list-models")
@click.option('--backend', '-b', type=click.Choice(['groq', 'ollama'], case_sensitive=False),
              help='Show models for specific backend only')
def list_models(backend):
    """List all available models for different backends"""
    ros_chatbot = ROSChatbotCLI()
    ros_chatbot.list_models(backend)

@cli.command("list-distros")
def list_distros():
    """List all supported ROS distributions"""
    from .config import SUPPORTED_ROS_DISTROS, get_ros_distro_info, ROS_Distro
    
    console.print("[bold blue] Supported ROS Distributions[/bold blue]")
    console.print("=" * 50)
    
    table = Table(title="ROS Distributions")
    table.add_column("Distro", style="cyan", no_wrap=True)
    table.add_column("Version", style="magenta")
    table.add_column("LTS", style="green")
    table.add_column("Ubuntu", style="yellow")
    table.add_column("Status", style="white")
    
    current_distro = ROS_Distro()
    
    for distro in SUPPORTED_ROS_DISTROS:
        info = get_ros_distro_info(distro)
        lts_status = "✅" if info.get("lts") else "❌"
        ubuntu_versions = ", ".join(info.get("ubuntu", ["N/A"]))
        
        if distro == current_distro:
            status = "🎯 Current"
        elif info.get("version") == "ROS2":
            status = "✅ Active"
        else:
            status = "⚠️  Legacy"
            
        table.add_row(
            distro.capitalize(),
            info.get("version", "Unknown"),
            lts_status,
            ubuntu_versions,
            status
        )
    
    console.print(table)
    
    if current_distro:
        console.print(f"\n[bold green]Current distro:[/bold green] {current_distro.upper()}")
    else:
        console.print(f"\n[yellow]No ROS distro detected. Set with:[/yellow]")
        console.print(f"  • [cyan]export OORB_ROS_DISTRO=humble[/cyan]")
        console.print(f"  • [cyan]oorb chat --distro humble[/cyan]")

@cli.command("test-retrieval")
@click.option('--endpoint', '-e', help='Retrieval endpoint to test (default: current configured endpoint)')
def test_retrieval(endpoint):
    """Test retrieval API endpoint connectivity and features"""
    from .config import get_retrieval_endpoint, validate_retrieval_endpoint, get_retrieval_endpoint_info
    
    test_endpoint = endpoint or get_retrieval_endpoint()
    
    console.print(f"[bold blue]🔍 Testing Retrieval Endpoint[/bold blue]")
    console.print("=" * 50)
    console.print(f"[bold]Endpoint:[/bold] {test_endpoint}")
    
    # Validate endpoint
    is_valid, message = validate_retrieval_endpoint(test_endpoint)
    
    if is_valid:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ {message}[/red]")
        return
    
    # Get detailed info
    info = get_retrieval_endpoint_info(test_endpoint)
    
    # Create status table
    table = Table(title="Endpoint Information")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    table.add_row("URL", info["endpoint"])
    table.add_row("Accessible", "✅ Yes" if info["accessible"] else "❌ No")
    table.add_row("Status Code", str(info["status_code"]) if info["status_code"] else "N/A")
    
    if info.get("error"):
        table.add_row("Error", info["error"])
    
    if info.get("features"):
        table.add_row("Available Endpoints", ", ".join(info["features"]))
    else:
        table.add_row("Available Endpoints", "None detected")
    
    console.print(table)
    
    # Show configuration help
    console.print(f"\n[bold green]💡 Configuration Options:[/bold green]")
    console.print(f"  • [cyan]export OORB_RETRIEVAL_ENDPOINT={test_endpoint}[/cyan]")
    console.print(f"  • [cyan]export RETRIEVAL_API_BASE_URL={test_endpoint}[/cyan]")
    console.print(f"  • [cyan]oorb chat --retrieval-endpoint {test_endpoint}[/cyan]")

@cli.command()
@click.option('--backend', '-b', type=click.Choice(LLM_BACKENDS, case_sensitive=False),
              help='LLM backend to use (azure, openai, or ollama)')
@click.option('--model', '-m', help='Specific model to use')
@click.option('--temperature', '-t', type=float,
              help='Temperature for response generation (0.0-1.0)')
@click.option('--use-tools/--no-tools', default=True,
              help='Enable/disable OpenAI function calling tools (auto-detected by default)')
@click.option('--distro', '-d', help='ROS distro to use (e.g., humble, jazzy, rolling)')
@click.option('--retrieval-endpoint', '-r', help='Retrieval API endpoint URL (e.g., http://localhost:8000)')
@click.option('--prompt', '-p', help='Single prompt (if not provided, enters interactive mode)')
def chat(backend, model, temperature, use_tools, distro, retrieval_endpoint, prompt):
    """Start interactive ROS Chatbot session or answer a single prompt"""
    
    # Validate retrieval endpoint if provided
    if retrieval_endpoint:
        from .config import validate_retrieval_endpoint
        is_valid, message = validate_retrieval_endpoint(retrieval_endpoint)
        if not is_valid:
            console.print(f"[red]Error: Retrieval endpoint validation failed: {message}[/red]")
            return
        console.print(f"[cyan]🔗 Using custom retrieval endpoint: {retrieval_endpoint}[/cyan]")
    
    ros_chatbot = ROSChatbotCLI(retrieval_endpoint=retrieval_endpoint)

    if prompt:
        # Single prompt mode (original behavior)
        ros_chatbot.chat(
            prompt=prompt,
            backend=backend,
            model=model,
            temperature=temperature,
            use_tools=use_tools,
            distro=distro
        )
    else:
        # Interactive mode
        ros_chatbot.interactive_chat(
            backend=backend,
            model=model,
            temperature=temperature,
            use_tools=use_tools,
            distro=distro
        )


@cli.command("status")
def status():
    """Check system status and configuration"""
    console.print("[bold blue] ROS Chatbot CLI Status[/bold blue]")
    console.print("=" * 50)

    # Check configuration
    config_result = validate_config()

    # Display API key status
    console.print("\n[bold]API Key Status:[/bold]")
    if AZURE_OPENAI_API_KEY:
        console.print("   AZURE_OPENAI_API_KEY: Set")
    else:
        console.print("   AZURE_OPENAI_API_KEY: Not set")

    # Check OpenAI API key
    if OPENAI_API_KEY:
        console.print("   OPENAI_API_KEY: Set")
    else:
        console.print("   OPENAI_API_KEY: Not set")

    # Check Ollama status
    console.print("\n[bold]Ollama Status:[/bold]")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            console.print("   Ollama service: Running")
            tags = response.json()
            models = [tag.get("name", "") for tag in tags.get("models", [])]
            if models:
                console.print(f"   Available models: {', '.join(models[:3])}{'...' if len(models) > 3 else ''}")
            else:
                console.print("    No models downloaded")
        else:
            console.print("   Ollama service: Not responding")
    except:
        console.print("   Ollama service: Not running")

    # Check Retrieval API status
    console.print("\n[bold]Retrieval API Status:[/bold]")
    try:
        import requests
        response = requests.get(RETRIEVAL_API_BASE_URL, timeout=5)
        if response.status_code == 200:
            console.print("   Retrieval API: Running")
            console.print("   /retrieve endpoint: Available")
        else:
            console.print("   Retrieval API: Not responding")
    except:
        console.print("   Retrieval API: Not running")


    # Show warnings and errors
    if config_result["warnings"]:
        console.print("\n[bold yellow]  Warnings:[/bold yellow]")
        for warning in config_result["warnings"]:
            console.print(f"  • {warning}")

    if config_result["errors"]:
        console.print("\n[bold red] Errors:[/bold red]")
        for error in config_result["errors"]:
            console.print(f"  • {error}")

    # Show recommended actions
    console.print("\n[bold green] Quick Setup:[/bold green]")
    if not AZURE_OPENAI_API_KEY and not OPENAI_API_KEY:
        console.print("  1. Get Azure OpenAI or OpenAI API access")
        console.print("  2. Set Azure: export AZURE_OPENAI_API_KEY='your_key' and AZURE_OPENAI_ENDPOINT='your_endpoint'")
        console.print("  3. Or set OpenAI: export OPENAI_API_KEY='your_key_here'")
        console.print("  4. Or install Ollama for local inference")

    console.print("  5. Start chatting: oorb chat -p 'Hello!'")

    # Show available backends
    available_backends = get_available_backends()
    if available_backends:
        console.print(f"\n[bold]Available backends:[/bold] {', '.join(available_backends)}")
    else:
        console.print("\n[bold red]No backends available![/bold red]")


if __name__ == "__main__":
    cli()