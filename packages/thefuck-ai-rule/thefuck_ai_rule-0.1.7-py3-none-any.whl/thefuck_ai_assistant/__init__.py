"""
TheFuck AI Assistant - 智能命令修正助手
"""
from .installer import install
from .rule import AI_API_URL, AI_API_KEY, AI_MODEL
from .rule import query_ai_for_correction
from .rule import ask_ai_if_command_failed
from .rule import get_new_command
from .rule import match

__version__ = "0.1.7"
__all__ = [
    "install",
    "AI_API_URL",
    "AI_API_KEY",
    "AI_MODEL",
    "query_ai_for_correction",
    "ask_ai_if_command_failed",
    "get_new_command",
    "match",
]
