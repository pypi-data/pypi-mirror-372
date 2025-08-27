# dev_actions/base.py
from abc import ABC, abstractmethod
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from functools import wraps
from contextlib import contextmanager
from quickquestion.utils import clear_screen, getch
import threading


class DevAction(ABC):
    """Base class for developer actions with execution lock prevention"""
    
    def __init__(self, provider, debug: bool = False):
        self.provider = provider
        self.debug = debug
        self.console = Console()
        self._execution_lock = threading.Lock()
        self._is_executing = False
        
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the action shown in the menu"""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """The description shown in the menu"""
        pass

    @contextmanager
    def show_loading(self, message: str = None):
        """Context manager for showing loading state"""
        default_message = f"Executing {self.name}..."
        with self.console.status(
            f"[bold blue]{message or default_message}[/bold blue]",
            spinner="dots",
            spinner_style="blue"
        ):
            yield

    def execute_with_loading(self, func):
        """Decorator to add loading message to any method"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.show_loading():
                return func(*args, **kwargs)
        return wrapper
        
    @abstractmethod
    def execute(self) -> bool:
        """Execute the action. Return True if successful."""
        pass

    def _wrapped_execute(self) -> bool:
        """Internal wrapper to add loading state and prevent multiple executions"""
        # Check if we're already executing
        if self._is_executing:
            if self.debug:
                self.console.print("[red]Action already executing, ignoring request[/red]")
            return False

        try:
            # Set executing flag
            with self._execution_lock:
                if self._is_executing:
                    return False
                self._is_executing = True

            # Execute with loading status
            with self.show_loading():
                return self.execute()

        finally:
            # Always reset the executing flag
            with self._execution_lock:
                self._is_executing = False

    def __call__(self) -> bool:
        """Make the action callable with default loading behavior and execution lock"""
        return self._wrapped_execute()

    def display_options(self, options: List[str], title: str = "Options") -> Optional[int]:
        """Display a list of options with consistent UI"""
        selected = 0

        # Show options
        for i, option in enumerate(options):
            style = "bold white on blue" if i == selected else "blue"
            self.console.print(Panel(str(option), border_style=style))

        while True:
            c = getch(debug=self.debug)
            
            if c == '\x1b[A':  # Up arrow
                if selected > 0:
                    selected -= 1
                    return self.display_options(options)  # Recursively redraw
            elif c == '\x1b[B':  # Down arrow
                if selected < len(options) - 1:
                    selected += 1
                    return self.display_options(options)  # Recursively redraw
            elif c == '\r':  # Enter
                return selected
            elif c == 'q':  # Quick exit
                return None

    def confirm_action(self, message: str) -> bool:
        """Display a confirmation dialog with consistent UI
        
        Args:
            message: Message to display
            
        Returns:
            True if confirmed, False if cancelled
        """
        options = ["Confirm", "Cancel"]
        selected = self.display_options(options, "Confirmation")
        return selected == 0
