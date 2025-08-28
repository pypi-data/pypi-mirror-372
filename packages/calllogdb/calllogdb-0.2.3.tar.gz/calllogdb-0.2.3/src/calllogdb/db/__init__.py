"""
Файл для создания модуля программы
"""

from .async_database import AsyncCallRepository
from .database import CallRepository

__all__: list[str] = ["CallRepository", "AsyncCallRepository"]
