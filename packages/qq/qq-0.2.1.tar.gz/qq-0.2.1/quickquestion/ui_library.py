# ui_library.py

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import List, Optional, Tuple, Any, Dict, Union
import json
from .utils import getch, clear_screen


class UIStateManager:
    """Manages UI state and transitions"""
    def __init__(self):
        self.editing_mode = False
        self.selected_index = 0
        self.selected_value_index = 0
        
    def reset(self):
        self.editing_mode = False
        self.selected_index = 0
        self.selected_value_index = 0
        
    @property
    def is_editing(self) -> bool:
        return self.editing_mode
        
    def toggle_editing(self):
        self.editing_mode = not self.editing_mode
        
    def set_selection(self, index: int):
        self.selected_index = index
        
    def set_value_selection(self, index: int):
        self.selected_value_index = index


class UIOptionDisplay:
    """Enhanced UI component for displaying and managing interactive menus"""
    
    def __init__(self, console: Console, debug: bool = False):
        self.console = console
        self.debug = debug
        self.state = UIStateManager()
        
    def debug_print(self, message: str, data: Any = None):
        """Print debug information if debug mode is enabled"""
        if self.debug:
            if data is not None:
                if isinstance(data, (dict, list)):
                    print(f"DEBUG UI: {message}")
                    print(f"DEBUG UI: Data = {json.dumps(data, indent=2)}")
                else:
                    print(f"DEBUG UI: {message} - {str(data)}")
            else:
                print(f"DEBUG UI: {message}")

    def display_banner(self,
        title: str,
        subtitle: List[str] = None,
        website: str = None
    ):
        """Display a consistent banner across UI components"""
        self.debug_print("Displaying banner", {
            'title': title,
            'subtitle': subtitle,
            'website': website
        })
        
        website_text = Text.assemble(
            "",
            (f"({website})", "dim")
        ) if website else ""
        
        title_text = f"[purple]{title}[/purple]"
        if subtitle:
            title_text += "\n" + "\n".join(subtitle)
        if website:
            title_text += f"\n{website_text}"
            
        self.console.print(Panel(
            title_text,
            box=box.ROUNDED,
            style="white",
            expand=False
        ), end="")

    def display_loading(self, message: str = "Loading..."):
        """Display a loading spinner with message"""
        self.debug_print(f"Displaying loading spinner: {message}")
        return self.console.status(
            f"[bold blue]{message}[/bold blue]",
            spinner="dots",
            spinner_style="blue"
        )

    def format_panel_content(
        self,
        content: Union[str, Dict[str, Any]],
        current_value: Optional[str] = None,
        options: Optional[List[str]] = None,
        selected_index: Optional[int] = None,
        editing_mode: bool = False,
        error: Optional[str] = None
    ) -> str:
        """Format content for display in a panel"""
        self.debug_print("Formatting panel content", {
            'content_type': type(content).__name__,
            'editing_mode': editing_mode,
            'has_error': error is not None
        })
        
        formatted = []
        
        # Handle dictionary-style content
        if isinstance(content, dict):
            current = content.get('current', 'Not Set')
            current_options = content.get('options', [])
            current_index = content.get('selected_index', 0)
            
            formatted.append(f"Current: [green]{current}[/green]")
            
            if current_options and editing_mode:
                options_str = ", ".join(
                    f"[{'white on cyan' if i == current_index else 'white'}]{opt}[/]"
                    for i, opt in enumerate(current_options)
                )
                formatted.append(f"Available: {options_str}")
                
        # Handle direct content
        else:
            if current_value:
                formatted.append(f"Current: [green]{current_value}[/green]")
            
            formatted.append(str(content))
            
            if options and editing_mode:
                options_str = ", ".join(
                    f"[{'white on cyan' if i == selected_index else 'white'}]{opt}[/]"
                    for i, opt in enumerate(options)
                )
                formatted.append(f"Available: {options_str}")
        
        # Add error message if present
        if error:
            formatted.append(f"[red]{error}[/red]")
            
        return "\n".join(formatted)

    def display_message(
        self,
        message: str,
        style: str = "green",
        title: str = None,
        pause: bool = True
    ):
        """Display a message with optional pause"""
        self.debug_print("Displaying message", {
            'message': message,
            'style': style,
            'title': title,
            'pause': pause
        })
        
        self.console.print(Panel(
            message,
            title=title,
            border_style=style
        ))
        
        if pause:
            self.console.print("\nPress Enter to continue...")
            while True:
                c = getch(debug=self.debug)
                if c == '\r':
                    break

    def display_header_panels(
        self,
        panels: List[Dict[str, str]],
        title: str = "Summary",
        style: str = "blue"
    ):
        """Display header panels with structured content"""
        self.debug_print("Displaying header panels", {
            'num_panels': len(panels),
            'title': title
        })
        
        if not panels:
            return
            
        content = []
        for panel in panels:
            panel_title = panel.get('title', '')
            panel_content = panel.get('content', '')
            content.append(f"[bold]{panel_title}[/bold]\n{panel_content}")
            
        self.console.print(Panel(
            "\n\n".join(content),
            title=title,
            border_style=style,
            box=box.ROUNDED
        ))

    def display_options(
        self,
        options: List[Any],
        title: str = "Options",
        panel_titles: Optional[List[str]] = None,
        extra_content: Optional[List[str]] = None,
        header_panels: Optional[List[Dict[str, str]]] = None,
        show_cancel: bool = True,
        editing_mode: bool = False,
        selected: Optional[int] = None,
        formatter: Optional[callable] = None,
        banner_params: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, str]:
        """Display an interactive option menu with optional banner"""
        self.debug_print("Starting display_options", {
            'num_options': len(options),
            'editing_mode': editing_mode,
            'selected': selected,
            'has_banner': banner_params is not None
        })
        
        if selected is not None:
            self.state.set_selection(selected)
        
        def render_screen():
            # Always clear screen before rendering
            clear_screen(caller="UIOptionDisplay.display_options")
            
            # Display banner if parameters provided
            if banner_params:
                self.debug_print("Rendering banner", banner_params)
                self.display_banner(
                    title=banner_params.get('title', ''),
                    subtitle=banner_params.get('subtitle', []),
                    website=banner_params.get('website')
                )
                
            if header_panels:
                self.debug_print("Rendering header panels", {
                    'num_panels': len(header_panels)
                })
                self.display_header_panels(header_panels)
            
            # Show appropriate navigation instructions
            instructions = (
                "[dim]←/→ to select, Enter to confirm, q to cancel[/dim]"
                if editing_mode else
                "[dim]↑/↓ to select, Enter to edit, q to exit[/dim]"
            )
            self.console.print(instructions)
            
            # Display options
            self.debug_print("Rendering options", {
                'current_selection': self.state.selected_index,
                'editing_mode': editing_mode
            })
            
            for i, option in enumerate(options):
                style = "bold white on blue" if i == self.state.selected_index else "blue"
                content = formatter(option) if formatter else str(option)
                
                panel_content = content
                if extra_content and i < len(extra_content):
                    panel_content = f"{content}\n{extra_content[i]}"
                
                panel_title = (
                    panel_titles[i] if panel_titles and i < len(panel_titles)
                    else f"Option {i + 1}"
                )
                
                self.console.print(Panel(
                    panel_content,
                    title=panel_title,
                    border_style=style
                ))
            
            if show_cancel:
                cancel_style = "bold white on red" if self.state.selected_index == len(options) else "red"
                self.console.print(Panel(
                    "Cancel",
                    title="Exit",
                    border_style=cancel_style
                ))

        while True:
            render_screen()
            c = getch(debug=self.debug)
            
            self.debug_print("Key pressed", repr(c))
            
            if not editing_mode:
                if c == '\x1b[A':  # Up arrow
                    self.debug_print("Up arrow pressed", {
                        'current_index': self.state.selected_index
                    })
                    if self.state.selected_index > 0:
                        self.state.set_selection(self.state.selected_index - 1)
                        continue
                        
                elif c == '\x1b[B':  # Down arrow
                    self.debug_print("Down arrow pressed", {
                        'current_index': self.state.selected_index
                    })
                    max_index = len(options) - 1 if not show_cancel else len(options)
                    if self.state.selected_index < max_index:
                        self.state.set_selection(self.state.selected_index + 1)
                        continue
                        
            else:  # Editing mode
                if c == '\x1b[D':  # Left arrow
                    self.debug_print("Left arrow pressed (editing mode)")
                    return self.state.selected_index, 'left'
                    
                elif c == '\x1b[C':  # Right arrow
                    self.debug_print("Right arrow pressed (editing mode)")
                    return self.state.selected_index, 'right'
            
            if c == '\r':  # Enter
                self.debug_print("Enter pressed", {
                    'selected_index': self.state.selected_index,
                    'is_cancel': show_cancel and self.state.selected_index == len(options)
                })
                if show_cancel and self.state.selected_index == len(options):
                    return self.state.selected_index, 'cancel'
                return self.state.selected_index, 'select'
                
            elif c == 'q':  # Quick exit
                self.debug_print("Quick exit requested")
                return self.state.selected_index, 'quit'
