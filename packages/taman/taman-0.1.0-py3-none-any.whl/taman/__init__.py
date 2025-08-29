"""
Taman - System Monitoring API

A FastAPI-based system monitoring tool that provides real-time process tracking
and resource usage information through RESTful endpoints and Server-Sent Events.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .api import app

__all__ = ["app"]