"""
API routes module
"""
from .auth_routes import router as auth_router
from .bot_routes import router as bot_router

__all__ = ['auth_router', 'bot_router']
