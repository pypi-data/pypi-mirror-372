"""
LIMMA - Language Interface Model for Machine Automation
A Python package for controlling ESP8266/ESP32 devices using natural language.
GET API KEY - https://limma.live
"""

__version__ = "0.1.1"
__author__ = "Yash Kumar Firoziya"
__email__ = "ykfiroziya@gmail.com"

from .core import Limma, LimmaConfig, ContextManager, ESPManager, NetworkUtils

__all__ = [
    "Limma",
    "LimmaConfig", 
    "ContextManager",
    "ESPManager",
    "NetworkUtils"
]