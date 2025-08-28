# calllog_async.py
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Literal, Union

from dateutil.relativedelta import relativedelta
from loguru import logger

from calllogdb.api import AsyncAPIClient
from calllogdb.core import Config
from calllogdb.db import AsyncCallRepository
from calllogdb.db.database import CallMapper
from calllogdb.db.models import Call
from calllogdb.types import Calls


# ───────── вспомогательные датаклассы ─────────
@dataclass(kw_only=True)
class DateParams:
    year: int = field(default_factory=lambda: datetime.now().year)
    month: int = field(default_factory=lambda: datetime.now().month)
    day: int = field(default_factory=lambda: datetime.now().day)
    hour: int = field(default_factory=lambda: datetime.now().hour)
    minute: int = 0

    date: datetime = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.date = datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
        )

    def adjust_date(self, delta: int, field: Literal["year", "month", "day", "hour", "minute"]) -> datetime:
        delta_map: dict[str, Union[timedelta, relativedelta]] = {
            "day": timedelta(days=delta),
            "hour": timedelta(hours=delta),
            "minute": timedelta(minutes=delta),
            "month": relativedelta(months=delta),
            "year": relativedelta(years=delta),
        }
        return self.date + delta_map[field]


@dataclass(kw_only=True)
class RequestParams:
    date_from: datetime = field(default_factory=lambda: DateParams().date)
    date_to: datetime = field(default_factory=lambda: DateParams().date)
    request_detailed: int = 1
    limit: int = 2000
    offset: int = 0

    def increase(self) -> None:
        self.offset += self.limit
        logger.debug(f"Параметры запроса увеличены: offset -> {self.offset}")


# ───────── главный класс ─────────
@dataclass
class AsyncCallLog:
    """Асинхронная обёртка для загрузки call-log’ов и записи их в БД."""

    config: Config = field(default_factory=Config)

    # ---------- низкоуровневый цикл запросов ----------
    async def _fetch_and_save(self, params: RequestParams) -> None:
        logger.info(f"Запрос данных: {asdict(params)}")

        # HTTP-клиент и репозиторий
        repo = AsyncCallRepository(self.config)
        async with AsyncAPIClient(self.config) as api:
            response_items: list[dict[str, Any]] = []

            while True:
                logger.debug(f"HTTP call offset={params.offset} limit={params.limit}")
                resp: dict[str, Any] = await api.get(params=asdict(params))
                items = resp.get("items", [])
                response_items.extend(items)

                if len(items) < params.limit:
                    break
                params.increase()

        logger.info(f"Всего получено {len(response_items)} записей")

        # преобразование и сохранение
        calls_model: Calls = Calls.from_dict(response_items)
        for c in calls_model.calls:
            c.ls_number = self.config.ls_number

        mapper = CallMapper()
        mapped: list[Call] = [mapper.map(c) for c in calls_model.calls]
        await repo.save_many(mapped)
        logger.info("Сохранение завершено")

    # ---------- публичные методы ----------
    async def get_month(self, month: int, *, year: int | None = None) -> None:
        year = year or DateParams().year
        await self._fetch_and_save(
            RequestParams(
                date_from=DateParams(year=year, month=month, day=1, hour=0).date,
                date_to=DateParams(year=year, month=month, day=1, hour=0).adjust_date(1, "month"),
            )
        )

    async def get_day(self, day: int, *, month: int | None = None, year: int | None = None) -> None:
        now = DateParams()
        year = year or now.year
        month = month or now.month
        await self._fetch_and_save(
            RequestParams(
                date_from=DateParams(year=year, month=month, day=day, hour=0).date,
                date_to=DateParams(year=year, month=month, day=day, hour=0).adjust_date(1, "day"),
            )
        )

    async def get_hours(self, hours: int = 1) -> None:
        now = DateParams()
        await self._fetch_and_save(
            RequestParams(
                date_from=now.adjust_date(-hours, "hour"),
                date_to=now.date,
            )
        )

    async def get_interval(self, *, date_from: datetime, date_to: datetime) -> None:
        await self._fetch_and_save(RequestParams(date_from=date_from, date_to=date_to))
