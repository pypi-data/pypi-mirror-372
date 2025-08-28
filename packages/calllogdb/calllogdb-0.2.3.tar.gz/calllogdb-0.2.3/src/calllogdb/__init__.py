"""
CallLogDB – библиотека для работы с call_log.

Публичный API:
    CallLog – основной класс для работы с call_log.
"""

from typing import Any, Literal

from calllogdb.core import Config

from .api import APIClient, AsyncAPIClient
from .async_calllog import AsyncCallLog
from .calllog import CallLog as calllogdb  # noqa: N813
from .core import Config, setup_logging  # noqa: F811
from .db import AsyncCallRepository, CallRepository
from .types import Call, Calls, EventBase

setup_logging("WARNING")

__all__: list[str] = [
    "calllogdb",
    "APIClient",
    "AsyncAPIClient",
    "Call",
    "Calls",
    "EventBase",
    "CallRepository",
    "AsyncCallRepository",
    "setup_logging",
    "Config",
]


class CallLogFacade:
    def __init__(self, config: Config) -> None:
        self._calllog = AsyncCallLog(config)

    def run(self, mode: Literal["hours", "day", "month", "interval"] = "hours", **kwargs: Any) -> None:
        """
        Точка входа для запуска загрузки данных звонков по выбранному режиму.

        Параметры:
            mode (Literal["hours", "day", "month", "interval"], optional):
                Режим запроса данных. Выбирай любой, но без паники, если забудешь — будет по умолчанию "hours".
                - "hours": последние N часов (по умолчанию 1 час).
                - "day": данные за конкретный день.
                - "month": данные за конкретный месяц.
                - "interval": данные за произвольный интервал времени.

            **kwargs: дополнительные параметры, которые зависят от выбранного режима:
                • Для mode="hours":
                    - hour (int, optional): Количество последних часов. Если не указал — считает за 1.
                • Для mode="day":
                    - day (int): День месяца. Обязательно.
                    - month (int, optional): Месяц (1–12). По умолчанию — текущий.
                    - year (int, optional): Год. По умолчанию — текущий.
                • Для mode="month":
                    - month (int): Месяц (1–12). Обязательно.
                    - year (int, optional): Год. По умолчанию — текущий.
                • Для mode="interval":
                    - date_from (datetime): Начало интервала. Без этого никак.
                    - date_to (datetime): Конец интервала. Без этого никак.

        Исключения:
            ValueError:
                - Если передан неизвестный mode (например, "вчера" или "когда-нибудь").
                - Если выбрал mode="interval", но забыл date_from или date_to.

        Примеры использования:
            >>> self.run("hours", hour=3)
        >>> self.run("day", day=4, month=6, year=2025)
        >>> self.run("month", month=5)
        >>> self.run("interval", date_from=datetime(2025, 5, 1), date_to=datetime(2025, 5, 2))
        """
        import asyncio

        async def wrapper() -> None:
            match mode:
                case "hours":
                    await self._calllog.get_hours(**kwargs)
                case "day":
                    await self._calllog.get_day(**kwargs)
                case "month":
                    await self._calllog.get_month(**kwargs)
                case "interval":
                    await self._calllog.get_interval(**kwargs)
                case _:
                    raise ValueError(f"Неизвестный режим: {mode}")

        asyncio.run(wrapper())


# удобный вход
def calllogdb_async(config: Config) -> CallLogFacade:
    return CallLogFacade(config)
