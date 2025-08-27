# settings_manager.py

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from rich.console import Console
from quickquestion.ui_library import UIOptionDisplay
from quickquestion.llm_lite_provider import (
    LLMProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GroqProvider,
    GrokProvider
)
from quickquestion.utils import clear_screen
from quickquestion.cache import get_provider_cache


class SettingsManager:
    def __init__(self, debug=False, clear_cache=False):
        self.console = Console()
        self.settings_file = Path.home() / '.qq_settings.json'
        self.debug = debug
        self.ui = UIOptionDisplay(self.console, debug=debug)

        # Define default settings
        self.default_settings = {
            "default_provider": "LM Studio",
            "provider_options": ["LM Studio", "Ollama", "OpenAI", "Anthropic", "Groq", "Grok"],
            "command_action": "Run Command",
            "command_action_options": ["Run Command", "Copy Command"],
            "simple_mode": False,
            "simple_mode_action": "Copy",
            "simple_mode_action_options": ["Copy", "Type"],
            "default_model": None,
            "available_models": []
        }

        # Get cache with debug mode
        self.provider_cache = get_provider_cache(debug=debug)

        # Only clear cache if explicitly requested
        if clear_cache:
            if self.debug:
                print("DEBUG Settings: Clearing provider cache")
            self.provider_cache.clear('available_providers')

    def debug_print(self, message: str, data: Any = None):
        """Print debug information if debug mode is enabled"""
        if self.debug:
            print(f"DEBUG Settings: {message}")
            if data is not None:
                if isinstance(data, (dict, list)):
                    print(f"DEBUG Settings: Data = {json.dumps(data, indent=2)}")
                else:
                    print(f"DEBUG Settings: Data = {str(data)}")

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults if no file exists"""
        settings = self.default_settings.copy()
        self.debug_print("Loading settings")

        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)

                # Check if there are new provider options to add
                if "provider_options" in saved_settings:
                    new_providers = [p for p in self.default_settings["provider_options"]
                                   if p not in saved_settings["provider_options"]]
                    if new_providers:
                        self.debug_print(f"Adding new providers: {new_providers}")
                        saved_settings["provider_options"].extend(new_providers)
                        # Save the updated settings back to file
                        with open(self.settings_file, 'w') as f:
                            json.dump(saved_settings, f, indent=2)

                settings.update(saved_settings)
                self.debug_print("Loaded settings", settings)

            except json.JSONDecodeError as e:
                self.debug_print(f"Error loading settings: {str(e)}")
                return self.default_settings

        return settings

    def get_provider_instance(self, provider_name: str) -> Optional[LLMProvider]:
        """Create a provider instance based on name"""
        self.debug_print(f"Creating provider instance for {provider_name}")
        provider_map = {
            "LM Studio": LMStudioProvider,
            "Ollama": OllamaProvider,
            "OpenAI": OpenAIProvider,
            "Anthropic": AnthropicProvider,
            "Groq": GroqProvider,
            "Grok": GrokProvider
        }
        provider_class = provider_map.get(provider_name)
        if provider_class:
            return provider_class(debug=self.debug)
        return None

    def update_available_models(self, settings: dict, provider_name: str):
        """Update available models list for the selected provider"""
        self.debug_print(f"Updating available models for {provider_name}")
        
        with self.ui.display_loading(f"Checking available models for {provider_name}..."):
            provider = self.get_provider_instance(provider_name)
            if provider and provider.check_status():
                models = provider.get_available_models()
                self.debug_print("Found models", models)
                settings["available_models"] = models
                if not settings["default_model"] or settings["default_model"] not in models:
                    settings["default_model"] = provider.select_best_model(models)
                    self.debug_print(f"Selected default model: {settings['default_model']}")
            else:
                self.debug_print("No models available")
                settings["available_models"] = []
                settings["default_model"] = None

    def display_settings_ui(self):
        """Display interactive settings UI using the enhanced UI library"""
        settings = self.load_settings()
        editing_mode = False
        
        self.debug_print("Starting settings UI display")
        
        # Display banner
        self.ui.display_banner(
            "Quick Question Settings",
            ["Configure your Quick Question preferences"],
            website="https://southbrucke.com"
        )

        while True:
            # Prepare settings data for display
            settings_data = [
                {
                    'title': "Default LLM Provider",
                    'content': {
                        'current': settings['default_provider'],
                        'options': settings['provider_options'],
                        'selected_index': settings['provider_options'].index(settings['default_provider'])
                    }
                },
                {
                    'title': "Default Model",
                    'content': {
                        'current': settings.get('default_model', 'Not Set'),
                        'options': settings['available_models'],
                        'selected_index': (
                            settings['available_models'].index(settings['default_model'])
                            if settings.get('default_model') in settings.get('available_models', [])
                            else 0
                        ),
                        'error': 'No models available for selected provider' if not settings['available_models'] else None
                    }
                },
                {
                    'title': "Command Action",
                    'content': {
                        'current': settings['command_action'],
                        'options': settings['command_action_options'],
                        'selected_index': settings['command_action_options'].index(settings['command_action'])
                    }
                },
                {
                    'title': "Simple Mode",
                    'content': {
                        'current': "Enabled" if settings.get('simple_mode', False) else "Disabled",
                        'options': ["Disabled", "Enabled"],
                        'selected_index': 1 if settings.get('simple_mode', False) else 0
                    }
                },
                {
                    'title': "Simple Mode Action",
                    'content': {
                        'current': settings.get('simple_mode_action', 'Copy'),
                        'options': settings.get('simple_mode_action_options', ['Copy', 'Type']),
                        'selected_index': settings.get('simple_mode_action_options', ['Copy', 'Type']).index(settings.get('simple_mode_action', 'Copy'))
                    }
                }
            ]

            # Prepare UI elements
            options = ['Edit Provider', 'Edit Model', 'Edit Action', 'Edit Simple Mode', 'Edit Simple Mode Action', 'Save Changes', 'Cancel']
            panel_titles = ["Provider Settings", "Model Settings", "Action Settings", "Simple Mode", "Simple Mode Action", "Save", "Cancel"]
            
            # Format panel content
            extra_content = []
            current_editing = self.ui.state.selected_index if editing_mode else None
            
            for i, setting in enumerate(settings_data[:5]):
                is_editing = editing_mode and current_editing == i
                if self.debug:
                    self.debug_print(f"Formatting panel {i}", {
                        "setting": setting['title'],
                        "editing": is_editing,
                        "current_editing": current_editing
                    })
                
                content = self.ui.format_panel_content(
                    content=setting['content'],
                    editing_mode=is_editing,
                    error=setting['content'].get('error')
                )
                
                if i == current_editing:
                    # When editing, show the available options
                    options_list = setting['content']['options']
                    selected_idx = self.ui.state.selected_value_index
                    content = self.ui.format_panel_content(
                        content=f"Edit {setting['title']}",
                        options=options_list,
                        selected_index=selected_idx,
                        current_value=setting['content']['current'],
                        editing_mode=True,
                        error=setting['content'].get('error')
                    )
                extra_content.append(content)
            
            # Add content for Save and Cancel options
            extra_content.extend([
                "Save and apply all changes",
                "Exit without saving"
            ])

            # Display options
            selected, action = self.ui.display_options(
                options=options,
                panel_titles=panel_titles,
                extra_content=extra_content,
                show_cancel=False,
                editing_mode=editing_mode
            )

            self.debug_print("UI action", {"selected": selected, "action": action})

            if action == 'quit':
                if editing_mode:
                    self.debug_print("Exiting edit mode")
                    editing_mode = False
                    continue
                self.debug_print("Exiting settings")
                clear_screen()
                return

            if editing_mode:
                current_setting = settings_data[selected]
                options_list = current_setting['content']['options']
                
                if action == 'left' and self.ui.state.selected_value_index > 0:
                    self.ui.state.set_value_selection(self.ui.state.selected_value_index - 1)
                elif action == 'right' and self.ui.state.selected_value_index < len(options_list) - 1:
                    self.ui.state.set_value_selection(self.ui.state.selected_value_index + 1)
                elif action == 'select':
                    self.debug_print("Applying setting change", {
                        "setting": current_setting['title'],
                        "value_index": self.ui.state.selected_value_index
                    })
                    
                    if selected == 0:  # Provider
                        new_provider = settings['provider_options'][self.ui.state.selected_value_index]
                        if new_provider != settings['default_provider']:
                            settings['default_provider'] = new_provider
                            self.update_available_models(settings, new_provider)
                    elif selected == 1 and settings['available_models']:  # Model
                        settings['default_model'] = settings['available_models'][self.ui.state.selected_value_index]
                    elif selected == 2:  # Action
                        settings['command_action'] = settings['command_action_options'][self.ui.state.selected_value_index]
                    elif selected == 3:  # Simple Mode
                        settings['simple_mode'] = self.ui.state.selected_value_index == 1
                    elif selected == 4:  # Simple Mode Action
                        settings['simple_mode_action'] = settings['simple_mode_action_options'][self.ui.state.selected_value_index]
                    
                    editing_mode = False
                    self.ui.state.reset()

            else:  # Not editing
                if action == 'select':
                    if selected < 5:  # Editable options
                        self.debug_print(f"Entering edit mode for option {selected}")
                        editing_mode = True
                        current_setting = settings_data[selected]
                        self.ui.state.set_selection(selected)
                        self.ui.state.set_value_selection(current_setting['content']['selected_index'])
                    elif selected == 5:  # Save
                        self.debug_print("Saving settings")
                        self.save_settings(settings)
                        clear_screen()
                        self.ui.display_message(
                            "Settings saved successfully!",
                            style="green",
                            title="Success"
                        )
                        return
                    else:  # Cancel
                        self.debug_print("Canceling settings")
                        clear_screen()
                        return

    def save_settings(self, settings: Dict[str, Any]):
        """Save settings and update cache"""
        self.debug_print("Starting settings save")
        
        try:
            with self.ui.display_loading("Saving settings..."):
                # Save settings to file
                with open(self.settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                self.debug_print("Saved settings to file", settings)

                # Initialize provider with new settings
                provider = self.get_provider_instance(settings["default_provider"])
                if provider and provider.check_status():
                    self.debug_print(f"Initializing new provider: {settings['default_provider']}")

                    # Update available models
                    models = provider.get_available_models()
                    if models:
                        settings["available_models"] = models
                        if not settings["default_model"] or settings["default_model"] not in models:
                            settings["default_model"] = provider.select_best_model(models)
                            provider.current_model = settings["default_model"]
                        
                        self.debug_print("Updated models", {
                            "provider": settings['default_provider'],
                            "model": settings['default_model'],
                            "available_models": models
                        })

                    # Clear existing cache before updating
                    self.debug_print("Clearing provider cache before update")
                    self.provider_cache.clear('available_providers')
                    
                    # Update provider cache
                    providers = []
                    for provider_name in settings["provider_options"]:
                        try:
                            provider_instance = self.get_provider_instance(provider_name)
                            if provider_instance and provider_instance.check_status():
                                if provider_name == settings["default_provider"]:
                                    provider_instance.current_model = settings["default_model"]
                                providers.append(provider_instance)
                                self.debug_print(f"Added provider {provider_name} to cache")
                        except Exception as e:
                            self.debug_print(f"Error initializing provider {provider_name}: {str(e)}")

                    if providers:
                        self.debug_print(f"Caching {len(providers)} providers")
                        self.provider_cache.set('available_providers', providers)

        except Exception as e:
            self.debug_print(f"Error in save_settings: {str(e)}")
            self.ui.display_message(
                f"Error saving settings: {str(e)}",
                style="red",
                title="Error"
            )
            if self.debug:
                import traceback
                traceback.print_exc()


def get_settings(debug=False):
    """Helper function to get current settings"""
    return SettingsManager(debug=debug).load_settings()
