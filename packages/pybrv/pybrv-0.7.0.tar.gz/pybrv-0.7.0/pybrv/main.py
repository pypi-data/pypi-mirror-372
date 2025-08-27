"""
pybrv - Python Business Rule Validator
Main module that provides the core functionality and interface.
"""
from .rule_manager import RuleManager
from .create_pybrvmeta import DatabricksPybrvmeta
from .recommendation import PybrvRecommendation

# Singleton instance of the rule manager

def main():
    """Entry point for the pybrv CLI"""
    help()


def help():
    """Display help information about pybrv."""
    print("pybrv is the Python-based business rule validator.")
