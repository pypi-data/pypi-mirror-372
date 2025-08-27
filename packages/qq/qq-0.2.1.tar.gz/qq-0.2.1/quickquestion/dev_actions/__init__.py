# dev_actions/__init__.py
from .base import DevAction
from .git_push import GitPushAction

# Register all available actions
available_actions = [
    GitPushAction
]
