"""
Configuration module for RXNRECer.
"""

from .config import *

# Create a config object that contains all configuration variables
class Config:
    def __init__(self):
        # Import all variables from config module
        import sys
        current_module = sys.modules[__name__]
        
        # Get all variables that don't start with underscore
        for name in dir(current_module):
            if not name.startswith('_') and not callable(getattr(current_module, name)):
                setattr(self, name, getattr(current_module, name))

# Create a global config instance
config = Config()

__all__ = ["config"]
