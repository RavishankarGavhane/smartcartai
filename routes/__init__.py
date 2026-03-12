# C:\Users\Sonam Gavhane\OneDrive\Desktop\SmartCartAI\routes\__init__.py

from .web import router as web_router
from .auth import router as auth_router
from .products import router as products_router
from .orders import router as orders_router
from .stats import router as stats_router
from .addresses import router as addresses_router

__all__ = [
    'web_router',
    'auth_router',
    'products_router',
    'orders_router',
    'stats_router',
    'addresses_router'
]