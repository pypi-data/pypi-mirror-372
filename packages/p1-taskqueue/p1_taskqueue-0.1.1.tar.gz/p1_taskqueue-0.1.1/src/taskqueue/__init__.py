"""
TaskQueue - A Task Queue Wrapper for Dekoruma Backend.
"""

__version__ = "0.1.0"
__author__ = "Chalvin"
__email__ = "engineering@dekoruma.com"

from .cmanager import cm
from .celery_app import celery_app

__all__ = ["cm", "celery_app"]
