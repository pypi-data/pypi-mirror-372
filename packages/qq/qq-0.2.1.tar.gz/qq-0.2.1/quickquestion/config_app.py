#!/usr/bin/env python3
"""
Textual-based configuration app for Quick Question.
Provides a rich TUI for managing providers and settings.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, Input, Label, DataTable, Tree, TabbedContent, TabPane, Checkbox, Select, LoadingIndicator, Markdown
from textual.reactive import var, reactive
from textual.binding import Binding
from textual.screen import Screen
from textual.message import Message
from textual.css.query import NoMatches
from textual import events, work
from pathlib import Path
import json
import asyncio
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .provider_registry import get_registry, ProviderInfo
from .settings_manager import SettingsManager
from .llm_lite_provider import LiteLLMProvider
from .cache import provider_cache


class ProviderStatus:
    """Provider availability status"""
    AVAILABLE = "✓ Available"
    CONFIGURED = "● Configured"
    NOT_CONFIGURED = "○ Not Configured"
    CHECKING = "⟳ Checking..."
    ERROR = "✗ Error"


class CategoryTree(Tree):
    """Tree widget for provider categories"""
    
    def __init__(self, *args, **kwargs):
        super().__init__("Provider Categories", *args, **kwargs)
        self.registry = get_registry()
        self.provider_status = {}
    
    def on_mount(self) -> None:
        """Build the category tree when mounted"""
        self.build_tree()
    
    def build_tree(self) -> None:
        """Build the provider category tree"""
        self.clear()
        root = self.root
        root.expand()
        
        for category in self.registry.get_all_categories():
            providers = self.registry.get_category_providers(category)
            configured_count = sum(1 for p in providers if self._is_configured(p))
            
            # Add category node with count
            category_label = f"{category} ({configured_count}/{len(providers)})"
            category_node = root.add(category_label, data={"type": "category", "name": category})
            
            # Add providers under category
            for provider in providers:
                status = self._get_provider_status(provider)
                provider_label = f"{provider.name} {status}"
                category_node.add_leaf(
                    provider_label,
                    data={"type": "provider", "info": provider}
                )
    
    def _is_configured(self, provider: ProviderInfo) -> bool:
        """Check if a provider is configured"""
        if not provider.requires_api_key:
            return True  # Local providers are always "configured"
        return bool(provider.api_key_env_var and os.environ.get(provider.api_key_env_var))
    
    def _get_provider_status(self, provider: ProviderInfo) -> str:
        """Get the status indicator for a provider"""
        if provider.name in self.provider_status:
            return self.provider_status[provider.name]
        
        if not provider.requires_api_key:
            # Will check availability later
            return ProviderStatus.NOT_CONFIGURED
        elif provider.api_key_env_var and os.environ.get(provider.api_key_env_var):
            return ProviderStatus.CONFIGURED
        else:
            return ProviderStatus.NOT_CONFIGURED
    
    @work(exclusive=True)
    async def check_provider_availability(self, provider: ProviderInfo) -> None:
        """Check if a provider is available (async)"""
        self.provider_status[provider.name] = ProviderStatus.CHECKING
        self.refresh()
        
        try:
            # Create provider instance and check
            llm_provider = LiteLLMProvider(provider_name=provider.name)
            available = await llm_provider.async_check_status()
            
            if available:
                self.provider_status[provider.name] = ProviderStatus.AVAILABLE
            else:
                self.provider_status[provider.name] = ProviderStatus.NOT_CONFIGURED
        except Exception:
            self.provider_status[provider.name] = ProviderStatus.ERROR
        
        self.refresh()


class ProviderConfigScreen(Screen):
    """Screen for configuring a specific provider"""
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("enter", "save", "Save"),
    ]
    
    def __init__(self, provider: ProviderInfo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = provider
        self.api_key_input = None
        self.model_select = None
        self.test_button = None
        self.status_label = None
    
    def compose(self) -> ComposeResult:
        """Create the configuration UI"""
        yield Header()
        
        with ScrollableContainer():
            yield Static(f"# Configure {self.provider.name}", classes="title")
            
            if self.provider.description:
                yield Static(self.provider.description, classes="description")
            
            if self.provider.requires_api_key:
                yield Label("API Key:")
                self.api_key_input = Input(
                    placeholder=f"Enter your {self.provider.name} API key",
                    password=True,
                    id="api_key_input"
                )
                # Load existing key if available
                if self.provider.api_key_env_var:
                    existing_key = os.environ.get(self.provider.api_key_env_var, "")
                    if existing_key:
                        self.api_key_input.value = existing_key
                yield self.api_key_input
            
            if self.provider.default_models:
                yield Label("Default Model:")
                self.model_select = Select(
                    [(model, model) for model in self.provider.default_models],
                    id="model_select"
                )
                yield self.model_select
            
            if self.provider.documentation_url:
                yield Static(f"📚 [Documentation]({self.provider.documentation_url})")
            
            with Horizontal():
                self.test_button = Button("Test Connection", variant="primary", id="test_button")
                yield self.test_button
                yield Button("Save", variant="success", id="save_button")
                yield Button("Cancel", variant="error", id="cancel_button")
            
            self.status_label = Static("", id="status_label")
            yield self.status_label
        
        yield Footer()
    
    @work(exclusive=True)
    async def test_connection(self) -> None:
        """Test the provider connection"""
        self.status_label.update("⟳ Testing connection...")
        
        try:
            # Save API key temporarily if provided
            if self.api_key_input and self.provider.api_key_env_var:
                os.environ[self.provider.api_key_env_var] = self.api_key_input.value
            
            # Test the provider
            provider = LiteLLMProvider(provider_name=self.provider.name)
            available = await provider.async_check_status()
            
            if available:
                models = provider.get_available_models()
                self.status_label.update(f"✓ Connection successful! Found {len(models)} models.")
                
                # Update model select if we got models
                if models and self.model_select:
                    self.model_select.set_options([(model, model) for model in models])
            else:
                self.status_label.update("✗ Connection failed. Please check your settings.")
        
        except Exception as e:
            self.status_label.update(f"✗ Error: {str(e)}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "test_button":
            self.test_connection()
        elif event.button.id == "save_button":
            self.save_configuration()
        elif event.button.id == "cancel_button":
            self.app.pop_screen()
    
    def save_configuration(self) -> None:
        """Save the provider configuration"""
        try:
            # Save API key if provided
            if self.api_key_input and self.provider.api_key_env_var:
                os.environ[self.provider.api_key_env_var] = self.api_key_input.value
            
            # Update settings file
            settings_manager = SettingsManager()
            settings = settings_manager.load_settings()
            
            # Add provider to options if not already there
            if self.provider.name not in settings["provider_options"]:
                settings["provider_options"].append(self.provider.name)
            
            # Set as default if it's the first configured provider
            configured_providers = [p for p in settings["provider_options"] 
                                   if self._is_provider_configured(p)]
            if len(configured_providers) == 1:
                settings["default_provider"] = self.provider.name
            
            # Save selected model
            if self.model_select and self.model_select.value:
                settings["default_model"] = self.model_select.value
            
            settings_manager.save_settings(settings)
            
            self.status_label.update("✓ Configuration saved successfully!")
            self.app.pop_screen()
            
        except Exception as e:
            self.status_label.update(f"✗ Error saving: {str(e)}")
    
    def _is_provider_configured(self, provider_name: str) -> bool:
        """Check if a provider is configured"""
        registry = get_registry()
        provider_info = registry.get_provider(provider_name)
        if not provider_info:
            return False
        if not provider_info.requires_api_key:
            return True
        return bool(provider_info.api_key_env_var and 
                   os.environ.get(provider_info.api_key_env_var))
    
    def action_go_back(self) -> None:
        """Go back to the main screen"""
        self.app.pop_screen()


class MainScreen(Screen):
    """Main configuration screen"""
    
    BINDINGS = [
        Binding("ctrl+s", "save_settings", "Save Settings", show=True),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the main UI"""
        yield Header()
        
        with TabbedContent():
            with TabPane("Quick Setup", id="quick_setup_tab"):
                with Vertical(classes="quick_container"):
                    # Top section with settings in columns
                    with Horizontal(classes="quick_settings_row"):
                        # Left column - Provider and Model
                        with Vertical(classes="quick_column"):
                            yield Label("Provider:", classes="compact_header")
                            yield Select(
                                [],  # Will be populated on mount
                                id="quick_provider_select",
                                classes="mini_select"
                            )
                            
                            yield Label("Model:", classes="compact_header")
                            yield Select(
                                [],  # Will be populated based on provider
                                id="quick_model_select",
                                disabled=True,
                                classes="mini_select"
                            )
                        
                        # Right column - Actions and Simple Mode
                        with Vertical(classes="quick_column"):
                            yield Label("Command:", classes="compact_header")
                            yield Select(
                                [("Run Command", "Run Command"), ("Copy Command", "Copy Command")],
                                id="quick_command_action",
                                classes="mini_select"
                            )
                            
                            with Horizontal(classes="mode_row"):
                                yield Checkbox("Simple Mode", id="quick_simple_mode", classes="mini_checkbox")
                                yield Select(
                                    [("Copy", "Copy"), ("Type", "Type")],
                                    id="quick_simple_action",
                                    classes="mini_mode_select"
                                )
                    
                    # Status line and instructions
                    yield Static("[dim]Press Ctrl+S to save settings[/dim]", id="quick_status_label", classes="status_line")
                    
                    # Test button only
                    yield Button("Test Provider", id="quick_test_button", disabled=True, classes="compact_button")
            
            with TabPane("Providers", id="providers_tab"):
                with Horizontal():
                    with Vertical(classes="sidebar"):
                        yield Label("Categories")
                        yield CategoryTree(id="category_tree")
                    
                    with Vertical(classes="main_content"):
                        yield Label("Provider Details", id="details_label")
                        yield Static("Select a provider from the list", id="provider_details")
                        with Horizontal(id="provider_actions"):
                            yield Button("Configure", variant="primary", id="configure_button", disabled=True)
                            yield Button("Test", id="test_button", disabled=True)
            
            
            with TabPane("About", id="about_tab"):
                yield Markdown("""
# Quick Question Configuration

Quick Question (qq) is a CLI tool for getting quick command-line suggestions using any LLM.

## Features
- 🚀 100+ LLM providers supported via LiteLLM
- 🏠 Local model support (Ollama, LM Studio)
- ☁️ Cloud provider support (OpenAI, Anthropic, etc.)
- ⚡ Fast inference providers (Groq, Together AI)
- 🔧 Easy configuration management

## Keyboard Shortcuts
- **Arrow Keys**: Navigate between items
- **Enter**: Select/Activate
- **Tab**: Switch between tabs
- **Escape**: Go back/Cancel
- **/**: Search providers

## Getting Help
Visit [https://southbrucke.com](https://southbrucke.com) for documentation.
                """)
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize when mounted"""
        self.selected_provider = None
        self.load_settings()
        self.load_quick_setup()
        # Schedule immediate settings load after mount
        self.set_timer(0.1, self.load_saved_settings)
    
    def action_save_settings(self) -> None:
        """Handle Ctrl+S to save settings"""
        self.save_quick_setup()
    
    def load_settings(self) -> None:
        """Load current settings"""
        # Settings are now loaded in load_quick_setup
        pass
    
    def load_saved_settings(self) -> None:
        """Load saved settings after widgets are ready"""
        try:
            settings_manager = SettingsManager()
            settings = settings_manager.load_settings()
            
            # Load Command Action
            command_action = self.query_one("#quick_command_action", Select)
            saved_value = settings.get("command_action", "Run Command")
            # Ensure the value matches one of the Select options
            if saved_value in ["Run Command", "Copy Command"]:
                command_action.value = saved_value
            
            # Load Simple Mode
            simple_mode = self.query_one("#quick_simple_mode", Checkbox)
            simple_mode.value = settings.get("simple_mode", False)
            
            # Load Simple Mode Action
            simple_action = self.query_one("#quick_simple_action", Select)
            simple_action.value = settings.get("simple_mode_action", "Copy")
        except Exception as e:
            # Widgets might not be ready yet
            self.app.notify(f"Note: Could not load all settings: {str(e)}", severity="warning")
    
    @work(exclusive=True)
    async def load_quick_setup(self) -> None:
        """Load available providers for quick setup"""
        try:
            settings_manager = SettingsManager()
            settings = settings_manager.load_settings()
            
            # Load all settings immediately, before checking providers
            try:
                # Load Command Action
                command_action = self.query_one("#quick_command_action", Select)
                command_action.value = settings.get("command_action", "Run Command")
                
                # Load Simple Mode
                simple_mode = self.query_one("#quick_simple_mode", Checkbox)
                simple_mode.value = settings.get("simple_mode", False)
                
                # Load Simple Mode Action
                simple_action = self.query_one("#quick_simple_action", Select)
                simple_action.value = settings.get("simple_mode_action", "Copy")
            except Exception:
                pass  # Widgets might not be ready yet
            
            # Get cached providers or check them
            cached_providers = provider_cache.get('available_providers')
            if cached_providers:
                providers = cached_providers
            else:
                # Check providers asynchronously
                status_label = self.query_one("#quick_status_label", Static)
                status_label.update("⟳ Checking available providers...")
                
                providers = []
                registry = get_registry()
                checked_providers = set()  # Avoid duplicates
                
                # First check local providers
                for provider_name in ["Ollama", "LM Studio"]:
                    try:
                        llm = LiteLLMProvider(provider_name=provider_name)
                        if await llm.async_check_status():
                            providers.append(llm)
                            checked_providers.add(provider_name)
                    except:
                        pass
                
                # Then check cloud providers with API keys
                for provider_name in ["OpenAI", "Anthropic", "Groq", "Grok"]:
                    if provider_name not in checked_providers:
                        try:
                            llm = LiteLLMProvider(provider_name=provider_name)
                            if await llm.async_check_status():
                                providers.append(llm)
                                checked_providers.add(provider_name)
                        except:
                            pass
                
                if providers:
                    provider_cache.set('available_providers', providers)
                
                status_label.update("")
            
            # Update provider select
            if providers:
                provider_names = []
                for p in providers:
                    if hasattr(p, 'provider_name'):
                        provider_names.append(p.provider_name)
                    elif hasattr(p, 'name'):
                        provider_names.append(p.name)
                    else:
                        provider_names.append(p.__class__.__name__.replace('Provider', ''))
                
                provider_select = self.query_one("#quick_provider_select", Select)
                provider_select.set_options([(name, name) for name in provider_names])
                
                # Set current default if it exists
                default_provider = settings.get("default_provider", "")
                if default_provider in provider_names:
                    provider_select.value = default_provider
                    # Load models for this provider
                    await self.load_models_for_provider(default_provider)
                
                # Enable test button
                test_button = self.query_one("#quick_test_button", Button)
                test_button.disabled = False
            
        except Exception as e:
            status_label = self.query_one("#quick_status_label", Static)
            status_label.update(f"✗ Error loading providers: {str(e)}")
    
    @work(exclusive=True)
    async def load_models_for_provider(self, provider_name: str) -> None:
        """Load models for selected provider"""
        try:
            model_select = self.query_one("#quick_model_select", Select)
            model_select.disabled = True
            model_select.set_options([])
            
            # Get provider and its models
            llm = LiteLLMProvider(provider_name=provider_name)
            if await llm.async_check_status():
                models = llm.get_available_models()
                if models:
                    model_select.set_options([(model, model) for model in models])
                    model_select.disabled = False
                    
                    # Set current default model if it exists
                    settings_manager = SettingsManager()
                    settings = settings_manager.load_settings()
                    default_model = settings.get("default_model", "")
                    if default_model in models:
                        model_select.value = default_model
                    elif llm.current_model in models:
                        model_select.value = llm.current_model
        except Exception as e:
            status_label = self.query_one("#quick_status_label", Static)
            status_label.update(f"✗ Error loading models: {str(e)}")
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle tree node selection"""
        node_data = event.node.data
        if node_data and node_data.get("type") == "provider":
            self.selected_provider = node_data["info"]
            self.update_provider_details()
    
    def update_provider_details(self) -> None:
        """Update the provider details panel"""
        if not self.selected_provider:
            return
        
        details = f"""
**{self.selected_provider.name}**

{self.selected_provider.description or "No description available"}

**Category:** {self.selected_provider.category}
**Requires API Key:** {"Yes" if self.selected_provider.requires_api_key else "No"}
**LiteLLM Prefix:** `{self.selected_provider.litellm_prefix}`
"""
        
        if self.selected_provider.default_models:
            details += f"\n**Default Models:**\n"
            for model in self.selected_provider.default_models[:3]:
                details += f"- {model}\n"
        
        if self.selected_provider.documentation_url:
            details += f"\n📚 [Documentation]({self.selected_provider.documentation_url})"
        
        # Update the details panel
        details_panel = self.query_one("#provider_details", Static)
        details_panel.update(details)
        
        # Enable action buttons
        configure_button = self.query_one("#configure_button", Button)
        configure_button.disabled = False
        
        test_button = self.query_one("#test_button", Button)
        test_button.disabled = False
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "configure_button" and self.selected_provider:
            self.app.push_screen(ProviderConfigScreen(self.selected_provider))
        elif event.button.id == "test_button" and self.selected_provider:
            self.test_provider()
        elif event.button.id == "quick_test_button":
            self.test_quick_setup_provider()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select widget changes"""
        if event.select.id == "quick_provider_select":
            # Load models when provider changes
            if event.value:
                self.load_models_for_provider(event.value)
                # Enable test button
                test_button = self.query_one("#quick_test_button", Button)
                test_button.disabled = False
    
    @work(exclusive=True)
    async def test_quick_setup_provider(self) -> None:
        """Test the provider selected in quick setup"""
        try:
            provider_select = self.query_one("#quick_provider_select", Select)
            model_select = self.query_one("#quick_model_select", Select)
            status_label = self.query_one("#quick_status_label", Static)
            
            if not provider_select.value:
                status_label.update("✗ Please select a provider")
                return
            
            status_label.update("⟳ Testing provider...")
            
            llm = LiteLLMProvider(provider_name=provider_select.value)
            if model_select.value:
                llm.current_model = model_select.value
            
            if await llm.async_check_status():
                status_label.update(f"✓ Provider is working! Model: {llm.current_model}")
            else:
                status_label.update("✗ Provider test failed")
        
        except Exception as e:
            status_label = self.query_one("#quick_status_label", Static)
            status_label.update(f"✗ Error: {str(e)}")
    
    def save_quick_setup(self) -> None:
        """Save quick setup settings"""
        try:
            provider_select = self.query_one("#quick_provider_select", Select)
            model_select = self.query_one("#quick_model_select", Select)
            command_action = self.query_one("#quick_command_action", Select)
            simple_mode = self.query_one("#quick_simple_mode", Checkbox)
            simple_action = self.query_one("#quick_simple_action", Select)
            status_label = self.query_one("#quick_status_label", Static)
            
            if not provider_select.value:
                status_label.update("✗ Please select a provider")
                return
            
            settings_manager = SettingsManager()
            settings = settings_manager.load_settings()
            
            # Update settings
            settings["default_provider"] = provider_select.value
            if model_select.value:
                settings["default_model"] = model_select.value
            settings["command_action"] = command_action.value
            settings["simple_mode"] = simple_mode.value
            settings["simple_mode_action"] = simple_action.value
            
            # Clear cache to force refresh
            provider_cache.clear('available_providers')
            
            settings_manager.save_settings(settings)
            
            status_label.update("[green]✓ Settings saved successfully![/green] [dim]Press Ctrl+S to save[/dim]")
            # Clear success message after 3 seconds
            self.set_timer(3, lambda: status_label.update("[dim]Press Ctrl+S to save settings[/dim]"))
            
        except Exception as e:
            status_label = self.query_one("#quick_status_label", Static)
            status_label.update(f"✗ Error saving: {str(e)}")
            self.app.notify(f"Error saving settings: {str(e)}", severity="error")
    
    @work(exclusive=True)
    async def test_provider(self) -> None:
        """Test the selected provider"""
        if not self.selected_provider:
            return
        
        details_panel = self.query_one("#provider_details", Static)
        details_panel.update("⟳ Testing provider...")
        
        try:
            provider = LiteLLMProvider(provider_name=self.selected_provider.name)
            available = await provider.async_check_status()
            
            if available:
                models = provider.get_available_models()
                details_panel.update(
                    f"✓ Provider is available!\n"
                    f"Found {len(models)} models.\n"
                    f"Current model: {provider.current_model}"
                )
            else:
                details_panel.update("✗ Provider is not available.\nPlease check configuration.")
        except Exception as e:
            details_panel.update(f"✗ Error testing provider:\n{str(e)}")
    


class ConfigApp(App):
    """Main Textual application for configuration"""
    
    CSS = """
    .sidebar {
        width: 40;
        border-right: solid green;
        padding: 1;
    }
    
    .main_content {
        padding: 1;
    }
    
    .quick_container {
        padding: 1;
    }
    
    .quick_settings_row {
        height: auto;
        padding: 0;
    }
    
    .quick_column {
        width: 50%;
        padding: 0 1;
    }
    
    .compact_header {
        height: 1;
        margin: 0;
        padding: 0;
    }
    
    .mini_select {
        height: 3;
        margin-bottom: 1;
    }
    
    .mode_row {
        height: 3;
        align: left middle;
    }
    
    .mini_checkbox {
        width: auto;
        margin-right: 1;
    }
    
    .mini_mode_select {
        width: 15;
        height: 3;
    }
    
    .compact_button {
        margin-top: 1;
        width: 100%;
    }
    
    .status_line {
        height: 2;
        text-align: center;
        margin: 0;
    }
    
    #quick_status_label {
        margin-top: 2;
        padding: 1;
        color: #00ff00;
    }
    
    #provider_details {
        height: 100%;
        padding: 1;
        border: solid green;
    }
    
    #provider_actions {
        margin-top: 1;
        height: 3;
    }
    
    .title {
        text-style: bold;
        color: purple;
        margin-bottom: 1;
    }
    
    .description {
        color: #888888;
        margin-bottom: 1;
    }
    
    Tree {
        height: 100%;
    }
    
    Button {
        margin: 0 1;
    }
    
    #status_label {
        margin-top: 1;
        padding: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("tab", "next_tab", "Next Tab", show=False),
        Binding("shift+tab", "previous_tab", "Previous Tab", show=False),
        Binding("/", "search", "Search"),
        Binding("?", "help", "Help"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Quick Question Configuration"
        self.sub_title = "Manage LLM Providers and Settings"
    
    def on_mount(self) -> None:
        """Set up the app when mounted"""
        self.push_screen(MainScreen())
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()
    
    def action_search(self) -> None:
        """Open search dialog"""
        # TODO: Implement provider search
        self.notify("Search coming soon!", severity="information")
    
    def action_help(self) -> None:
        """Show help"""
        self.notify(
            "Use arrow keys to navigate, Enter to select, Tab to switch tabs, Q to quit",
            severity="information"
        )


def run_config_app():
    """Run the configuration app"""
    app = ConfigApp()
    app.run()


if __name__ == "__main__":
    run_config_app()