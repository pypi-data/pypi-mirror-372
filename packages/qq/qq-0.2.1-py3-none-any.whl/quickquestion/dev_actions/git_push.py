# dev_actions/git_push.py

import subprocess
import os
from typing import List, Optional, Tuple
from rich.panel import Panel
from pathlib import Path
from quickquestion.ui_library import UIOptionDisplay
from quickquestion.utils import clear_screen
from contextlib import contextmanager
from .base import DevAction


class GitPushAction(DevAction):
    """Git push action with AI-generated commit messages"""
    
    def __init__(self, provider, debug: bool = False):
        super().__init__(provider, debug)
        self._is_loading = False

    @property
    def name(self) -> str:
        return "Push Code"
        
    @property
    def description(self) -> str:
        return "Stage, commit, and push changes with AI-generated commit message"

    def _is_git_repository(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            if self.debug:
                self.console.print(f"[blue]DEBUG: Git repository check result: {result.returncode}[/blue]")
                if result.stderr:
                    self.console.print(f"[blue]DEBUG: Git stderr: {result.stderr}[/blue]")
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            if self.debug:
                self.console.print(f"[red]DEBUG: Git repository check error: {str(e)}[/red]")
            return False

    def _get_git_changes(self) -> Tuple[str, List[str]]:
        """Get the diff of changes and list of modified files"""
        if self.debug:
            self.console.print("[blue]DEBUG: Getting git changes[/blue]")
            
        # Get both staged and unstaged changes
        diff_process = subprocess.run(
            ["git", "diff", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        # Get both modified and untracked files
        status_process = subprocess.run(
            ["git", "status", "--porcelain"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd()
        )
        
        modified_files = [
            line[3:] for line in status_process.stdout.split('\n')
            if line.strip() and line[0] in ['M', 'A', 'D', '?', ' ']
        ]
        
        if self.debug:
            self.console.print(f"[blue]DEBUG: Found {len(modified_files)} modified files[/blue]")
            for file in modified_files:
                self.console.print(f"[blue]DEBUG: Modified file: {file}[/blue]")
        
        return diff_process.stdout, modified_files

    def _stage_changes(self) -> bool:
        """Stage all changes"""
        try:
            if self.debug:
                self.console.print("[blue]DEBUG: Staging changes[/blue]")
            result = subprocess.run(
                ["git", "add", "-A"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode != 0:
                if self.debug:
                    self.console.print(f"[red]DEBUG: Git add error: {result.stderr}[/red]")
                return False
            return True
        except subprocess.CalledProcessError as e:
            if self.debug:
                self.console.print(f"[red]DEBUG: Error staging changes: {str(e)}[/red]")
            return False

    def _commit_changes(self, message: str) -> bool:
        """Commit staged changes with the given message"""
        try:
            if self.debug:
                self.console.print("[blue]DEBUG: Committing changes[/blue]")
            result = subprocess.run(
                ["git", "commit", "-m", message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )
            if result.returncode != 0:
                if self.debug:
                    self.console.print(f"[red]DEBUG: Git commit error: {result.stderr}[/red]")
                return False
            if self.debug and result.stdout:
                self.console.print(f"[blue]DEBUG: Git commit output: {result.stdout}[/blue]")
            return True
        except subprocess.CalledProcessError as e:
            if self.debug:
                self.console.print(f"[red]DEBUG: Error committing changes: {str(e)}[/red]")
            return False

    def _generate_commit_message(self, diff: str, files: List[str]) -> str:
        """Generate a commit message using the LLM"""
        prompt = f"""As a developer, analyze these git changes and generate a clear, concise commit message.
Modified files: {', '.join(files)}

Changes:
{diff}

Rules for the commit message:
1. Use present tense (e.g., "Add feature" not "Added feature")
2. Keep it under 50 characters
3. Be specific but concise
4. Focus on the "what" and "why", not the "how"
5. Don't include file names unless crucial

Return ONLY the commit message with no additional text or formatting."""

        try:
            if self.debug:
                self.console.print("[blue]DEBUG: Generating commit message using LLM[/blue]")
            response = self.provider.generate_response(prompt)
            return response[0].strip('"\'')
        except Exception as e:
            if self.debug:
                self.console.print(f"[red]Error generating commit message: {str(e)}[/red]")
            return ""

    def _display_commit_options(self, commit_message: str, modified_files: List[str]) -> Optional[str]:
        """Display commit options without additional status messages"""
        ui = UIOptionDisplay(self.console, debug=self.debug)
        
        # Prepare options data
        options = ["Commit", "Regenerate", "Cancel"]
        panel_titles = ["Commit Changes", "Generate New Message", "Exit"]
        
        # Prepare header panels
        header_panels = [
            {
                'title': 'Git Status',
                'content': f"[yellow]Modified Files:[/yellow]\n{', '.join(modified_files)}"
            },
            {
                'title': 'Current Commit Message',
                'content': f"[green]{commit_message}[/green]"
            }
        ]

        while True:
            selected, action = ui.display_options(
                options=options,
                panel_titles=panel_titles,
                extra_content=[
                    "Apply the selected commit message",
                    "Generate a new message",
                    "Cancel the operation"
                ],
                header_panels=header_panels,
                show_cancel=False,  # We have our own cancel option
                banner_params={
                    'title': "Git Commit Review",
                    'subtitle': ["Review and confirm commit message"],
                    'website': "https://southbrucke.com"
                }
            )

            if action in ('quit', 'cancel') or selected == 2:  # Exit
                return None
                
            if action == 'select':
                if selected == 0:  # Commit
                    return commit_message
                elif selected == 1:  # Regenerate
                    # Show loading only while generating
                    with self.show_loading("Generating new commit message..."):
                        diff, _ = self._get_git_changes()
                        new_message = self._generate_commit_message(diff, modified_files)
                    
                    if new_message:
                        commit_message = new_message
                        # Update the header panel with new message
                        header_panels[1]['content'] = f"[green]{commit_message}[/green]"
                    else:
                        ui.display_message(
                            "Failed to generate new commit message",
                            style="red",
                            title="Error",
                            pause=True
                        )
                    continue

        return None

    def execute(self) -> bool:
        """Execute the git push action with clean UI flow"""
        ui = UIOptionDisplay(self.console, debug=self.debug)
        
        if self.debug:
            self.console.print("[blue]DEBUG: Starting git push action[/blue]")
            
        if not self._is_git_repository():
            ui.display_message(
                "Not a git repository",
                style="red",
                title="Error"
            )
            return False

        # Get git changes silently
        diff, modified_files = self._get_git_changes()
        
        if not modified_files:
            ui.display_message(
                "No changes to commit",
                style="yellow",
                title="Status"
            )
            return False

        # Generate initial commit message with loading indicator
        with self.show_loading("Analyzing changes..."):
            commit_message = self._generate_commit_message(diff, modified_files)
        
        if not commit_message:
            ui.display_message(
                "Could not generate commit message",
                style="red",
                title="Error"
            )
            return False

        # Display options and get selected message
        # Note: No status message here as the UI is interactive
        selected_message = self._display_commit_options(commit_message, modified_files)
        
        if selected_message is None:
            ui.display_message(
                "Operation cancelled",
                style="yellow",
                title="Status"
            )
            return False
            
        # Show loading only during actual commit
        with self.show_loading("Committing changes..."):
            success = self._stage_changes() and self._commit_changes(selected_message)
        
        if success:
            ui.display_message(
                "Successfully committed changes!",
                style="green",
                title="Success"
            )
            return True
        
        ui.display_message(
            "Failed to commit changes",
            style="red",
            title="Error"
        )
        return False
