#!/usr/bin/env python3
# qq.py

import sys
import argparse
import json
import os
from rich.console import Console
from rich.panel import Panel
import time
import asyncio
if sys.platform != 'win32':
    import termios
    import tty

import subprocess
from rich import box
from rich.text import Text
from rich.terminal_theme import TerminalTheme
from typing import List, Type
from pathlib import Path
from datetime import datetime
import warnings
import urllib3
from quickquestion.llm_lite_provider import (
    LLMProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GroqProvider,
    GrokProvider
)
from quickquestion.settings_manager import SettingsManager, get_settings
from quickquestion.utils import getch
from quickquestion.utils import clear_screen
from quickquestion.cache import provider_cache
from quickquestion.utils import enable_debug_printing, disable_debug_printing
from quickquestion.ui_library import UIOptionDisplay


class QuickQuestion:
    # In QuickQuestion.__init__
    def __init__(self, debug=False, settings=None, lazy_init=False):
        self.console = Console()
        self.debug = debug
        self.history_file = Path.home() / '.qq_history.json'
        self.settings = settings or get_settings(debug=debug)
        self.providers = []
        self.provider = None
        
        # In lazy init mode, defer provider initialization
        if lazy_init:
            return
            
        self._initialize_providers()
    
    def _initialize_providers(self, skip_status_if_cached=False):
        """Initialize providers with loading status if needed"""
        # For simple mode optimization: if we have cached providers, use them without status display
        if skip_status_if_cached:
            cached_providers = provider_cache.get('available_providers')
            if cached_providers:
                self.providers = cached_providers
                self._select_provider_from_settings()
                return
        
        # Show loading only if needed
        if not self.debug:
            with self.console.status("[bold blue]Initializing...[/bold blue]", spinner="dots"):
                self.providers = self._get_cached_or_new_providers()
        else:
            self.providers = self._get_cached_or_new_providers()

        if not self.providers:
            self.console.print("[red]Error: No LLM providers available")
            self.console.print("[yellow]Please make sure either LM Studio or Ollama is running")
            sys.exit(1)

        self._select_provider_from_settings()
    
    def _select_provider_from_settings(self):
        """Select provider based on settings with proper fallback"""
        default_provider = self.settings.get("default_provider", "")
        default_model = self.settings.get("default_model")
        
        if self.debug:
            print(f"\nDEBUG: Selecting provider from settings")
            print(f"DEBUG: Default provider setting: {default_provider}")
            print(f"DEBUG: Default model setting: {default_model}")
            print(f"DEBUG: Available providers: {[self.get_provider_name(p) for p in self.providers]}")
        
        # Try to find the configured default provider
        selected_provider = None
        for p in self.providers:
            if self.get_provider_name(p) == default_provider:
                selected_provider = p
                # Apply the default model from settings
                if default_model:
                    selected_provider.current_model = default_model
                    if self.debug:
                        print(f"DEBUG: Found matching provider: {default_provider}")
                        print(f"DEBUG: Applied model from settings: {default_model}")
                else:
                    if self.debug:
                        print(f"DEBUG: Found matching provider: {default_provider}")
                        print(f"DEBUG: Using provider's current model: {selected_provider.current_model}")
                break
        
        if not selected_provider:
            # Fallback: prioritize local providers
            for p in self.providers:
                if isinstance(p, (LMStudioProvider, OllamaProvider)):
                    selected_provider = p
                    if self.debug:
                        print(f"DEBUG: Using local provider fallback: {self.get_provider_name(p)}")
                    break
            
            # Final fallback: use first available provider
            if not selected_provider and self.providers:
                selected_provider = self.providers[0]
                if self.debug:
                    print(f"DEBUG: Using first available provider: {self.get_provider_name(selected_provider)}")
        
        self.provider = selected_provider

    def _get_cached_or_new_providers(self) -> List[LLMProvider]:
        """Get providers from cache or initialize new ones"""
        # First check the cache
        cached_providers = provider_cache.get('available_providers')
        if cached_providers is not None:
            if self.debug:
                cache_info = provider_cache.get_cache_info()
                print("\nDEBUG: Using cached providers")
                print(f"DEBUG: Cache age: {cache_info['available_providers']['age_seconds']:.1f} seconds")
                print(f"DEBUG: Cache expires in: {cache_info['available_providers']['expires_in_seconds']:.1f} seconds")
                for p in cached_providers:
                    print(f"DEBUG: Cached provider: {self.get_provider_name(p)}")
                    if hasattr(p, 'current_model'):
                        print(f"DEBUG: Provider model: {p.current_model}")
            return cached_providers

        if self.debug:
            print("\nDEBUG: No valid cache found, checking providers")

        # If no cache, do the full provider check
        providers = self._get_available_providers()

        # Cache the results if we found any providers
        if providers:
            if self.debug:
                print("\nDEBUG: Caching newly found providers:")
                for p in providers:
                    print(f"DEBUG: Caching provider: {self.get_provider_name(p)}")
                    if hasattr(p, 'current_model'):
                        print(f"DEBUG: Provider model: {p.current_model}")
            provider_cache.set('available_providers', providers)

        return providers

    def debug_print(self, message: str, data: any = None):
        """Print debug information if debug mode is enabled"""
        if self.debug:
            self.console.print(f"[cyan]DEBUG: {message}[/cyan]")
            if data is not None:
                if isinstance(data, (dict, list)):
                    self.console.print(Panel(
                        json.dumps(data, indent=2),
                        title="Debug Data",
                        border_style="cyan"
                    ))
                else:
                    self.console.print(Panel(
                        str(data),
                        title="Debug Data",
                        border_style="cyan"
                    ))

    def is_cloud_provider(self, provider: LLMProvider) -> bool:
        """Check if the provider is cloud-based"""
        return isinstance(provider, (OpenAIProvider, AnthropicProvider))

    def get_provider_name(self, provider=None) -> str:
        """Get the friendly name of the provider"""
        provider = provider or self.provider
        if isinstance(provider, OpenAIProvider):
            return "OpenAI"
        elif isinstance(provider, LMStudioProvider):
            return "LM Studio"
        elif isinstance(provider, OllamaProvider):
            return "Ollama"
        elif isinstance(provider, AnthropicProvider):
            return "Anthropic"
        elif isinstance(provider, GroqProvider):
            return "Groq"
        elif isinstance(provider, GrokProvider):
            return "Grok"
        return "Unknown Provider"

    def get_provider_type_message(self) -> str:
        """Get the provider type message with appropriate color"""
        return "[red]Cloud Based Provider[/red]" if self.is_cloud_provider(self.provider) else "[green]Local Provider[/green]"

    def print_banner(self):
        """Print the banner using UI library"""
        ui = UIOptionDisplay(self.console, debug=self.debug)
        
        # Check configured provider
        default_provider = self.settings['default_provider']
        provider_available = any(self.get_provider_name(p) == default_provider for p in self.providers)
        
        # Create subtitle lines
        subtitle = []
        
        if provider_available:
            subtitle.append(f"[yellow]Provider: {default_provider}[/yellow]")
        else:
            fallback_provider = self.get_provider_name()
            subtitle.append(f"[red]Provider: {default_provider} (Not Available) → Using: {fallback_provider}[/red]")
        
        subtitle.append(self.get_provider_type_message())
        subtitle.append(f"[yellow]Command Action: {self.settings.get('command_action', 'Run Command')}[/yellow]")
        
        ui.display_banner(
            "Quick Question",
            subtitle=subtitle,
            website="https://southbrucke.com"
        )

    def load_history(self) -> List[dict]:
        """Load command history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_to_history(self, command: str, question: str):
        """Save command to history with timestamp and question"""
        history = self.load_history()
        history.append({
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'question': question
        })
        # Keep only last 100 commands
        history = history[-100:]

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def display_history(self):
        """Display command history with interactive selection"""
        history = self.load_history()
        if not history:
            self.console.print("[yellow]No command history found[/yellow]")
            return

        selected = 0
        # Get last 10 entries in reverse order
        entries = list(reversed(history[-10:]))

        def render_screen():
            if not self.debug:  # Only clear screen if not in debug mode
                clear_screen()
            self.print_banner()
            self.console.print("[bold]Command History:[/bold]\n")

            # Show instructions
            self.console.print("\n[dim]↑/↓ to select, Enter to execute, [/dim][red]q[/red][dim] to cancel[/dim]\n")

            # Display each history entry
            for i, entry in enumerate(entries):
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
                style = "bold white on blue" if i == selected else "blue"
                self.console.print(
                    Panel(
                        f"[dim]{timestamp}[/dim]\nQ: {entry['question']}\n[green]$ {entry['command']}[/green]",
                        title=f"Entry {i + 1}",
                        border_style=style
                    )
                )

            # Add cancel option
            cancel_style = "bold white on red" if selected == len(entries) else "red"
            self.console.print(Panel("Cancel", title="Exit", border_style=cancel_style))

        while True:
            render_screen()
            c = self.getch()
            if self.debug:
                print(f"\nDEBUG UI - Received key: {repr(c)}")

            # Simple arrow key handling
            if c == '\x1b[A':  # Up arrow
                if self.debug:
                    print(f"DEBUG UI - Up arrow - Current selection: {selected}")
                if selected > 0:
                    selected -= 1
                    if self.debug:
                        print(f"DEBUG UI - New selection: {selected}")

            elif c == '\x1b[B':  # Down arrow
                if self.debug:
                    print(f"DEBUG UI - Down arrow - Current selection: {selected}")
                if selected < len(entries):
                    selected += 1
                    if self.debug:
                        print(f"DEBUG UI - New selection: {selected}")

            elif c == '\r':  # Enter key
                if selected == len(entries):  # If cancel is selected
                    clear_screen()
                    sys.exit(0)
                else:
                    clear_screen()
                    self.print_banner()
                    selected_entry = entries[selected]
                    command = selected_entry['command']
                    self.console.print(f"\n[green]Executing command:[/green] {command}")
                    # Don't add to history again since it's already there
                    subprocess.run(command, shell=True)
                    break

            elif c == 'q':  # Quick exit
                clear_screen()
                sys.exit(0)

    def display_help(self):
        """Display help information"""
        clear_screen()
        self.print_banner()

        help_text = """[bold white]Usage:[/bold white]
        qq "your question here"    Ask for command suggestions
        qq --history              Show command history
        qq --settings            Configure application settings
        qq --debug               Enable debug mode

    [bold white]Examples:[/bold white]
        qq "how to find files containing text"
        qq "show running processes"
        qq "check disk space"

    [bold white]Navigation:[/bold white]
        ↑/↓ arrows               Select options
        Enter                    Execute/Select
        q                        Quit/Cancel

    [bold white]Current Configuration:[/bold white]
        Provider: [green]{provider}[/green]
        Action: [green]{action}[/green]
        Model: [green]{model}[/green]

    For more information, visit: [blue]https://southbrucke.com[/blue]
    """.format(
            provider=self.get_provider_name(),
            action=self.settings.get('command_action', 'Run Command'),
            model=self.provider.get_model_info() or 'Not Set'
        )

        self.console.print(Panel(
            help_text,
            title="Quick Question Help",
            border_style="blue",
            expand=False
        ))

    def generate_prompt(self, question: str) -> str:
        os_type = "Windows" if sys.platform == "win32" else "macOS"
        return f"""You are a helpful command-line expert. Provide exactly 3 different command-line solutions for the following question: {question}

    CRITICAL REQUIREMENTS:
    1. You MUST respond with ONLY a JSON array containing exactly 3 strings
    2. Each string must be a complete, executable command
    3. Do NOT include any explanations, reasoning, or text outside the JSON array
    4. Do NOT include line numbers or bullet points
    5. Focus on {os_type} terminal commands
    6. Keep commands concise and practical

    REQUIRED FORMAT - Your ENTIRE response must be:
    ["complete command 1", "complete command 2", "complete command 3"]
    
    Nothing else. Just the JSON array."""

    def get_command_suggestions_simple(self, question: str) -> List[str]:
        """Get command suggestions without UI elements for simple mode"""
        # Initialize providers if not already done
        if not self.providers:
            self._initialize_providers(skip_status_if_cached=True)
            
        try:
            prompt = self.generate_prompt(question)
            self.debug_print("Generated prompt:", prompt)

            # Simple status message instead of spinner
            self.console.print("[dim]Thinking...[/dim]", end="\r")
            
            raw_response = self.provider.generate_response_with_debug(prompt) if self.debug else self.provider.generate_response(prompt)
            
            # Clear the thinking message
            self.console.print(" " * 20, end="\r")
            
            if self.debug:
                self.debug_print("Raw LLM response:", raw_response)

            return raw_response

        except Exception as e:
            if self.debug:
                import traceback
                traceback.print_exc()
            self.console.print(f"[red]Error: {str(e)}[/red]")
            return ["echo 'Error occurred while generating suggestions'"]

    def get_command_suggestions(self, question: str) -> List[str]:
        clear_screen()
        self.print_banner()

        current_model = self.provider.get_model_info()
        if current_model:
            self.console.print(f"[green]Using model: {current_model}")

        try:
            prompt = self.generate_prompt(question)
            self.debug_print("Generated prompt:", prompt)

            # Create and start the spinner
            with self.console.status(
                "[bold blue]Thinking...[/bold blue]",
                spinner="dots",
                spinner_style="blue"
            ):
                raw_response = self.provider.generate_response_with_debug(prompt) if self.debug else self.provider.generate_response(prompt)

                if self.debug:
                    self.debug_print("Raw LLM response:", raw_response)

                return raw_response

        except Exception as e:
            self.console.print(f"[red]Error: {str(e)}")
            if self.debug:
                import traceback
                self.debug_print("Full traceback:", traceback.format_exc())
            self.console.print("[yellow]Please make sure your LLM provider is running and configured correctly.")
            sys.exit(1)

    def getch(self):
        return getch(debug=self.debug)

    async def _check_providers_async(self) -> List[LLMProvider]:
        """Async provider checking with enhanced debugging"""
        available_providers = []
        default_model = self.settings.get('default_model')

        if self.debug:
            print("\nDEBUG: Starting async provider checks")
            print(f"DEBUG: Default model from settings: {default_model}")

        # Create all provider instances
        providers = [
            LMStudioProvider(debug=self.debug),
            OllamaProvider(debug=self.debug),
            OpenAIProvider(debug=self.debug),
            AnthropicProvider(debug=self.debug),
            GroqProvider(debug=self.debug),
            GrokProvider(debug=self.debug)
        ]

        if self.debug:
            print("\nDEBUG: Created provider instances")
            for p in providers:
                print(f"DEBUG: Initialized {p.__class__.__name__}")

        # Check all providers concurrently
        async def check_provider(provider):
            if self.debug:
                print(f"\nDEBUG: Checking {provider.__class__.__name__}")

            # Set model BEFORE checking status if this is the default provider
            if default_model and self.get_provider_name(provider) == self.settings['default_provider']:
                provider.current_model = default_model
                if self.debug:
                    print(f"DEBUG: Pre-setting default model to {default_model} for {self.get_provider_name(provider)}")

            if await provider.async_check_status(debug=self.debug):
                if self.debug:
                    print(f"DEBUG: {provider.__class__.__name__} is available")
                    if provider.current_model:
                        print(f"DEBUG: Current model: {provider.current_model}")
                return provider

            if self.debug:
                print(f"DEBUG: {provider.__class__.__name__} is not available")
            return None

        if self.debug:
            print("\nDEBUG: Starting concurrent provider checks")

        # Run all checks concurrently
        tasks = [check_provider(p) for p in providers]
        results = await asyncio.gather(*tasks)

        if self.debug:
            print("\nDEBUG: Completed concurrent provider checks")

        # Filter out None results
        available_providers = [p for p in results if p is not None]

        if self.debug:
            print(f"\nDEBUG: Found {len(available_providers)} available providers:")
            for p in available_providers:
                print(f"DEBUG: - {self.get_provider_name(p)}")
            if not available_providers:
                print("\nDEBUG: No providers available")
                print("DEBUG: Please ensure either LM Studio or Ollama is running")
                print("DEBUG: LM Studio should be running on http://localhost:1234")
                print("DEBUG: Ollama should be running on http://localhost:11434")

        return available_providers

    def _get_available_providers(self) -> List[LLMProvider]:
        """Get available providers with enhanced caching"""
        if self.debug:
            print("\nDEBUG: Starting provider initialization")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            providers = loop.run_until_complete(self._check_providers_async())
            loop.close()

            # Cache the results if we found any providers
            if providers:
                provider_cache.set('available_providers', providers)
                if self.debug:
                    print("\nDEBUG: Cached new provider configuration")
                    cache_info = provider_cache.get_cache_info()
                    print(f"DEBUG: Cache will expire in: {cache_info['available_providers']['expires_in_seconds']} seconds")

            return providers

        except Exception as e:
            if self.debug:
                print(f"\nDEBUG: Error checking providers: {str(e)}")
                import traceback
                print("DEBUG: Full traceback:")
                traceback.print_exc()
            return []

    def handle_simple_mode(self, suggestions: List[str], question: str):
        """Handle simple mode - copy or type first suggestion based on settings"""
        if not suggestions:
            self.console.print("[red]No suggestions available[/red]")
            sys.exit(1)
        
        # Get the first suggestion
        selected_command = suggestions[0]
        
        # Get the simple mode action from settings
        simple_mode_action = self.settings.get('simple_mode_action', 'Copy')
        
        try:
            if simple_mode_action == 'Type':
                # Type the command to terminal
                type_command_to_terminal(selected_command)
                self.console.print(f"[green]✓[/green] Command typed: [blue]{selected_command}[/blue]")
                self.console.print("[dim]Press Enter to execute[/dim]")
            else:
                # Copy to clipboard
                copy_to_clipboard(selected_command)
                self.console.print(f"[green]✓[/green] Command copied to clipboard: [blue]{selected_command}[/blue]")
            
            # Save to history
            self.save_to_history(selected_command, question)
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]Error in simple mode: {str(e)}[/red]")
            sys.exit(1)

    def display_suggestions(self, suggestions: List[str], question: str):
        """Display command suggestions using the enhanced UI library"""
        ui = UIOptionDisplay(self.console, debug=self.debug)

        # Format header panels with provider info
        provider_type = "Cloud Based Provider" if self.is_cloud_provider(self.provider) else "Local Provider"
        provider_info = self.get_provider_name()
        current_model = self.provider.get_model_info()
        
        header_panels = [
            {
                'title': 'Provider Info',
                'content':
                    f"Type: [{'red' if self.is_cloud_provider(self.provider) else 'green'}]{provider_type}[/]\n"
                    f"Provider: [yellow]{provider_info}[/yellow]\n"
                    f"Model: [blue]{current_model or 'Not Set'}[/blue]"
            },
            {
                'title': 'Question',
                'content': f"[italic]{question}[/italic]"
            }
        ]

        # Prepare options data
        options = [f"Option {i + 1}" for i in range(len(suggestions))]
        panel_titles = [f"Command {i + 1}" for i in range(len(suggestions))]
        
        # Format the command display with syntax highlighting
        def format_command(cmd: str) -> str:
            return f"[green]$ {cmd}[/green]"
        
        extra_content = [format_command(cmd) for cmd in suggestions]

        while True:
            selected, action = ui.display_options(
                options=options,
                panel_titles=panel_titles,
                extra_content=extra_content,
                header_panels=header_panels,
                show_cancel=True,
                formatter=lambda x: x  # Simple pass-through formatter
            )

            if action in ('quit', 'cancel'):
                clear_screen()
                sys.exit(0)

            if action == 'select':
                clear_screen()
                ui.display_banner("Quick Question",
                    ["Command execution"],
                    website="https://southbrucke.com")

                selected_command = suggestions[selected]

                # Check command action setting
                if self.settings.get('command_action') == 'Copy Command':
                    try:
                        copy_to_clipboard(selected_command)
                        ui.display_message(
                            f"Command copied to clipboard:\n[green]{selected_command}[/green]",
                            style="blue",
                            title="Success",
                            pause=True
                        )
                        # Save to history before exiting
                        self.save_to_history(selected_command, question)
                        sys.exit(0)
                    except Exception as e:
                        ui.display_message(
                            f"Error copying to clipboard: {str(e)}",
                            style="red",
                            title="Error",
                            pause=True
                        )
                        sys.exit(1)
                else:
                    self.console.print(f"\n[green]Executing command:[/green] {selected_command}")
                    # Save to history before executing
                    self.save_to_history(selected_command, question)
                    subprocess.run(selected_command, shell=True)
                    break


def copy_to_clipboard(text: str):
    """Cross-platform clipboard copy"""
    try:
        import pyperclip
        pyperclip.copy(text)
    except ImportError:
        if sys.platform == 'darwin':
            subprocess.run('pbcopy', input=text.encode(), env={'LANG': 'en_US.UTF-8'})
        elif sys.platform == 'win32':
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()


def type_command_to_terminal(command: str):
    """Type command to terminal input buffer"""
    if sys.platform == 'win32':
        # Windows implementation
        import msvcrt
        for char in command:
            msvcrt.putch(char.encode())
    else:
        # Unix/Linux/macOS implementation
        import fcntl
        import termios
        
        # Get the terminal file descriptor
        fd = sys.stdin.fileno()
        
        # Put each character into the input buffer
        for char in command:
            fcntl.ioctl(fd, termios.TIOCSTI, char.encode())


def main():
    """Entry point for Quick Question"""
    parser = argparse.ArgumentParser(description="Quick Question - Command Line Suggestions")
    parser.add_argument("question", nargs="*", help="Your command-line question")
    parser.add_argument("--settings", action="store_true", help="Open settings menu (Rich UI)")
    parser.add_argument("--config", action="store_true", help="Open advanced configuration (Textual UI)")
    parser.add_argument("--history", action="store_true", help="Show command history")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the provider cache")
    parser.add_argument("--dev", action="store_true", help="Enter developer mode")
    parser.add_argument("--simple", action="store_true", help="Simple mode - copy or type first suggestion based on settings")
    parser.add_argument("--simple-copy", action="store_true", help="Simple mode - copy first suggestion to clipboard")
    parser.add_argument("--simple-type", action="store_true", help="Simple mode - type first suggestion to terminal")

    args = parser.parse_args()

    if args.debug:
        enable_debug_printing()

    if args.clear_cache:
        provider_cache.clear()
        print("Cache cleared successfully")
        return

    if args.settings:
        SettingsManager(debug=args.debug, clear_cache=True).display_settings_ui()
        return
    
    if args.config:
        from quickquestion.config_app import run_config_app
        run_config_app()
        return
    
    if args.dev:
        from quickquestion.dev_mode import DevMode
        DevMode(debug=args.debug).display_menu()
        return

    # Pass clear_cache=False for normal operation
    settings_manager = SettingsManager(debug=args.debug, clear_cache=False)
    settings = settings_manager.load_settings()
    
    # Check if simple mode is enabled (either via args or settings)
    simple_mode = args.simple or args.simple_copy or args.simple_type or settings.get('simple_mode', False)
    
    # Determine simple mode action
    if args.simple_type:
        settings['simple_mode_action'] = 'Type'
    elif args.simple_copy:
        settings['simple_mode_action'] = 'Copy'
    # Otherwise use the setting value
    
    # Only show loading message if not in debug mode, not in dev mode, and not in simple mode
    if not args.debug and not args.dev and not simple_mode:
        print("Loading Quick Question...")

    # Use lazy initialization for simple mode to improve startup time
    qq = QuickQuestion(debug=args.debug, settings=settings, lazy_init=simple_mode)

    try:
        if args.history:
            qq.display_history()
            return

        if not args.question:
            # Show help if no arguments provided
            qq.display_help()
        else:
            question = " ".join(args.question)
            
            if simple_mode:
                # Suppress SSL warnings in simple mode for cleaner output
                warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)
                # In simple mode, don't clear screen or show banner
                suggestions = qq.get_command_suggestions_simple(question)
                qq.handle_simple_mode(suggestions, question)
            else:
                suggestions = qq.get_command_suggestions(question)
                qq.display_suggestions(suggestions, question)
    finally:
        if args.debug:
            disable_debug_printing()


if __name__ == "__main__":
    main()
