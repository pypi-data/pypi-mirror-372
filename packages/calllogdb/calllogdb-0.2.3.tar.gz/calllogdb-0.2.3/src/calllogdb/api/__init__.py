"""
Файл для создания модуля программы
"""

from .api_client import APIClient
from .async_api_client import AsyncAPIClient

__all__: list[str] = ["APIClient", "AsyncAPIClient"]
