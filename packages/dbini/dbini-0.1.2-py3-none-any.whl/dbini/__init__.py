"""
dbini - Zero-config NoSQL backend database for Python

This package provides a lightweight, zero-configuration, NoSQL-style database 
that automatically stores data locally inside the project directory. It is 
designed to be developer-friendly, secure, and easily usable across different 
programming environments.

Main Components:
----------------
- DBini   : Core database handler (create projects, collections, docs, files)
- Server  : Lightweight server to expose REST API for frontend or external clients
"""

from .core import DBini
from .server import serve, create_app  # fixed: import functions instead of non-existent Server

__version__ = "0.1.2"
__author__ = "Binidu01"
__license__ = "MIT"

__all__ = [
    "DBini",
    "serve",
    "create_app",
]
