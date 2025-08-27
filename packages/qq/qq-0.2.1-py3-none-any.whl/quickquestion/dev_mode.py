# dev_mode.py

import os
import sys
import json
import inspect
import importlib.util
from pathlib import Path
from typing import Optional, List, Type, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import threading

from quickquestion.llm_lite_provider import LLMProvider
from quickquestion.utils import clear_screen, getch
from quickquestion.settings_manager import get_settings
from quickquestion.dev_actions import available_actions, DevAction
from quickquestion.ui_library import UIOptionDisplay


class DevMode:
    def __init__(self, debug: bool = False):
        self.console = Console()
        self.debug = debug
        self.settings = get_settings(debug=debug)
        self.ui = UIOptionDisplay(self.console, debug=debug)
        
        # Show loading if not in debug mode
        if not debug:
            with self.ui.display_loading("Initializing dev mode..."):
                self.provider = self._initialize_provider()
                self.custom_actions_dir = Path.home() / "QuickQuestion" / "CustomDevActions"
                self.actions = self._initialize_actions()
        else:
            self.provider = self._initialize_provider()
            self.custom_actions_dir = Path.home() / "QuickQuestion" / "CustomDevActions"
            self.actions = self._initialize_actions()
            
        self._execution_lock = threading.Lock()
        self._is_executing = False
        
    def debug_print(self, message: str, data: Any = None):
        """Print debug information if debug mode is enabled"""
        if self.debug:
            # Add timestamp to debug messages
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            msg = f"[{timestamp}] DEBUG DevMode: {message}"
            self.console.print(msg)
            
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

    def _ensure_custom_actions_dir(self):
        """Ensure custom actions directory exists and contains required files"""
        if not self.custom_actions_dir.exists():
            self.debug_print(f"Creating custom actions directory: {self.custom_actions_dir}")
            self.custom_actions_dir.mkdir(parents=True)
            
            # Create __init__.py file
            init_file = self.custom_actions_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")
                self.debug_print("Created __init__.py file")
            
            # Create sample action file
            sample_path = self.custom_actions_dir / "sample_action.py"
            if not sample_path.exists():
                self.debug_print("Creating sample action file")
                sample_content = '''"""Sample Developer Action for Quick Question"""
import time
from rich.progress import Progress, SpinnerColumn, TextColumn
from quickquestion.dev_actions.base import DevAction

class SampleStepAction(DevAction):
    @property
    def name(self) -> str:
        return "Sample Two-Step Action"
        
    @property
    def description(self) -> str:
        return "Demonstrates a two-step process with progress indicators"

    def show_countdown(self, seconds: int, message: str):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(message, total=seconds)
            for remaining in range(seconds, 0, -1):
                progress.update(task, description=f"{message} ({remaining}s)")
                time.sleep(1)
        
    def execute(self) -> bool:
        self.console.print("[bold blue]Starting sample two-step process...[/bold blue]")
        
        self.console.print("[green]Step 1:[/green] First waiting period")
        self.show_countdown(3, "Processing step 1")
        
        if not self.confirm_action("Continue to step 2?"):
            self.console.print("[yellow]Process cancelled[/yellow]")
            return False
            
        self.console.print("[green]Step 2:[/green] Second waiting period")
        self.show_countdown(3, "Processing step 2")
        
        self.console.print("[bold green]Process completed successfully![/bold green]")
        return True
    '''
                sample_path.write_text(sample_content)
                self.debug_print("Created sample action file")

    def _load_custom_actions(self) -> List[Type[DevAction]]:
        """Load custom actions from the CustomDevActions directory"""
        custom_actions = []
        
        self._ensure_custom_actions_dir()
        
        if not self.custom_actions_dir.exists():
            self.debug_print(f"Custom actions directory not found: {self.custom_actions_dir}")
            return []

        sys.path.append(str(self.custom_actions_dir.parent.parent))
        
        # Scan for .py files
        for file_path in self.custom_actions_dir.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
                
            try:
                module_name = f"QuickQuestion.CustomDevActions.{file_path.stem}"
                self.debug_print(f"Loading module: {module_name}")
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None or spec.loader is None:
                    self.debug_print(f"Could not create spec for {file_path}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)
                
                # Find DevAction subclasses
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and issubclass(obj, DevAction) and obj != DevAction):
                        self.debug_print(f"Found custom action: {name}")
                        custom_actions.append(obj)
                        
            except Exception as e:
                self.debug_print(f"Error loading {file_path}: {str(e)}")
                if self.debug:
                    import traceback
                    traceback.print_exc()
                continue
        
        return custom_actions

    def _initialize_actions(self) -> List[DevAction]:
        """Initialize both built-in and custom actions"""
        # Get built-in actions
        actions = [action(self.provider, self.debug) for action in available_actions]
        self.debug_print(f"Initialized {len(actions)} built-in actions")
        
        # Load custom actions
        custom_actions = self._load_custom_actions()
        actions.extend(action(self.provider, self.debug) for action in custom_actions)
        self.debug_print(f"Added {len(custom_actions)} custom actions")
        
        return actions

    def _initialize_provider(self) -> Optional[LLMProvider]:
        """Initialize the LLM provider based on current settings"""
        self.debug_print("Initializing provider")
        from quickquestion.qq import QuickQuestion
        qq = QuickQuestion(debug=self.debug, settings=self.settings)
        return qq.provider

    def display_menu(self):
        """Display the developer mode menu using the enhanced UI library"""
        try:
            self.debug_print("Starting dev mode display")
            
            # Display banner
            if not self.debug:
                clear_screen()
            
            # Prepare menu data
            options = self.actions + ["Exit"]
            panel_titles = []
            extra_content = []
            
            # Format action options
            for action in self.actions:
                panel_titles.append(action.name)
                extra_content.append(f"[dim]{action.description}[/dim]")
                
            # Add exit option
            panel_titles.append("Exit")
            extra_content.append("Exit developer mode")

            while True:
                try:
                    # Display menu and get selection
                    selected, action = self.ui.display_options(
                        options=[opt.name if isinstance(opt, DevAction) else opt for opt in options],
                        panel_titles=panel_titles,
                        extra_content=extra_content,
                        show_cancel=False,
                        banner_params={
                            'title': "Quick Question",
                            'subtitle': ["Select an action"],
                            'website': "https://southbrucke.com"
                        }
                    )
                    
                    # Log selection in debug mode
                    if self.debug:
                        self.debug_print("Menu selection", {
                            "selected": selected,
                            "action": action,
                            "selected_name": (options[selected].name
                                if selected < len(self.actions)
                                else "Exit")
                        })

                    # Handle selection
                    if action in ('quit', 'cancel') or selected == len(options) - 1:  # Exit
                        self.debug_print("Exiting dev mode")
                        clear_screen()
                        return
                        
                    elif action == 'select':
                        selected_action = self.actions[selected]
                        self.debug_print(f"Executing action: {selected_action.name}")
                        
                        # Execute selected action
                        self._execute_action(selected_action)
                        
                        # Refresh display after action completes
                        if not self.debug:
                            clear_screen()
                        self.ui.display_banner(
                            "Quick Question - Developer Mode - Line 259",
                            subtitle=["Select an action to execute"],
                            website="https://southbrucke.com"
                        )
                        
                except KeyboardInterrupt:
                    self.debug_print("Keyboard interrupt received")
                    clear_screen()
                    return
                    
                except Exception as e:
                    self.debug_print(f"Error in menu handling: {str(e)}")
                    if self.debug:
                        import traceback
                        self.debug_print("Full traceback", traceback.format_exc())
                    return
                    
        except Exception as e:
            self.debug_print(f"Fatal error in display_menu: {str(e)}")
            if self.debug:
                import traceback
                self.debug_print("Full traceback", traceback.format_exc())
            raise

    def _execute_action(self, action: DevAction):
        """Execute an action with proper locking and error handling"""
        if self._is_executing:
            self.ui.display_message(
                "An action is already running, please wait...",
                style="yellow",
                title="Warning"
            )
            return

        try:
            with self._execution_lock:
                if self._is_executing:
                    return
                
                self._is_executing = True
                self.debug_print(f"Executing action: {action.name}")
                
                # Execute without a persistent loading indicator
                success = action.execute()

                if not success:
                    self.debug_print("Action completed with errors")
                    self.ui.display_message(
                        "Action completed with errors. Check the output above.",
                        style="yellow",
                        title="Warning",
                        pause=True
                    )

        except Exception as e:
            self.debug_print(f"Error executing action: {str(e)}")
            self.ui.display_message(
                f"Error executing action: {str(e)}",
                style="red",
                title="Error",
                pause=True
            )
            if self.debug:
                import traceback
                traceback.print_exc()

        finally:
            with self._execution_lock:
                self._is_executing = False


def main():
    """Entry point for developer mode"""
    import argparse
    parser = argparse.ArgumentParser(description="Quick Question - Developer Mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    dev_mode = DevMode(debug=args.debug)
    dev_mode.display_menu()


if __name__ == "__main__":
    main()
