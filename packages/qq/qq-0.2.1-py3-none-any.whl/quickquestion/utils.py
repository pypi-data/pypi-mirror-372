import sys
import os
import inspect
import builtins
import datetime
from typing import Any
if sys.platform != 'win32':
    import termios
    import tty


def getch(debug=False):
    """Cross-platform character input with cleaner debug output"""
    if sys.platform == 'win32':
        import msvcrt
        first = msvcrt.getch()
        if debug:
            print("\nDEBUG getch() - First byte:", first)

        if first in [b'\xe0', b'\x00']:  # Special keys
            second = msvcrt.getch()
            if debug:
                print("DEBUG getch() - Second byte:", second)

            # Windows arrow keys mapping
            if second == b'H':    # Up arrow
                result = '\x1b[A'
            elif second == b'P':  # Down arrow
                result = '\x1b[B'
            elif second == b'K':  # Left arrow
                result = '\x1b[D'
            elif second == b'M':  # Right arrow
                result = '\x1b[C'
            else:
                result = 'x'  # Default for unmapped special keys

            if debug:
                print(f"DEBUG getch() - Mapped to: {repr(result)}")

            return result

        return first.decode('utf-8', errors='replace')
    else:
        # Unix systems (macOS, Linux)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            first = sys.stdin.read(1)
            if debug:
                print(f"\nDEBUG getch() - First byte: {repr(first)}")

            if first == '\x1b':  # Escape sequence
                # Read potential escape sequence
                second = sys.stdin.read(1)
                if debug:
                    print(f"DEBUG getch() - Second byte: {repr(second)}")

                if second == '[':
                    third = sys.stdin.read(1)
                    if debug:
                        print(f"DEBUG getch() - Third byte: {repr(third)}")

                    # Map arrow keys
                    result = '\x1b[' + third

                    if debug:
                        print(f"DEBUG getch() - Mapped to: {repr(result)}")

                    return result

                # Handle non-arrow escape sequences
                return first + second

            return first

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def clear_screen(caller: str = None):
    """Fast cross-platform screen clearing with caller tracking

    Args:
        caller: Optional string to identify the caller. If not provided,
               will attempt to automatically detect the caller.
    """
    # Get caller info if not provided
    if caller is None:
        # Get the caller's frame
        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        
        if caller_frame:
            # Get the module name and calling function name
            module_name = caller_frame.f_globals.get('__name__', '')
            function_name = caller_frame.f_code.co_name
            
            # Format caller string
            caller = f"{module_name}.{function_name}"
        else:
            caller = "unknown"
            
    debug_str = f"Clearing screen (called from: {caller})"
    
    # If debug mode is enabled (checking if print has been replaced with debug_print)
    if hasattr(print, '__wrapped__'):
        print(debug_str)
    
    # Perform the actual screen clearing
    if sys.platform == 'win32':
        # Use ANSI escape sequences if available, fallback to cls
        try:
            import colorama
            colorama.init()
            print('\033[2J\033[H', end='')
        except ImportError:
            os.system('cls')
    else:
        print('\033[2J\033[H', end='')


original_print = builtins.print


def debug_print(*args: Any, **kwargs: Any):
    """Enhanced print function that adds timestamps to debug messages"""
    if args and isinstance(args[0], str) and args[0].strip().startswith("DEBUG"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        new_args = (f"[{timestamp}] {args[0]}",) + args[1:]
        original_print(*new_args, **kwargs)
    else:
        original_print(*args, **kwargs)


def enable_debug_printing():
    """Enable timestamped debug printing"""
    builtins.print = debug_print


def disable_debug_printing():
    """Restore original print function"""
    builtins.print = original_print
