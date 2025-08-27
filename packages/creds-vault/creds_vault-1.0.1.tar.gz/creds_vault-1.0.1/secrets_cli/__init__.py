"""
Creds Vault - Secure environment variable synchronization tool.

A command-line utility for securely sharing .env files across development teams
using GitHub Gists with client-side AES-256 encryption.
"""

__version__ = "1.0.1"
__author__ = "Mudassir Mirza"
__email__ = "hello.mudassirmirza@gmail.com"

from .cli import main

__all__ = ["main"]