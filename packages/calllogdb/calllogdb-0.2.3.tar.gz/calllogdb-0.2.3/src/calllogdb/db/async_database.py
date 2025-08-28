# async_call_repository.py
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncIterator, Literal

from loguru import logger
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.dialects.postgresql.dml import Insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from calllogdb.core import Config
from calllogdb.types import Call as CallData

from .models import ApiVars, Base, Call, Date, Event

# ─────────────────── настройки логирования ────────────────────
logging.getLogger("psycopg").setLevel(logging.CRITICAL)


def call_to_dict(call: Call) -> dict[str, Any]:
    """Преобразует модель Call в словарь по её колонкам."""
    return {col.name: getattr(call, col.name) for col in Call.__table__.columns}


# ─────────────────────── CallMapper (synс) ─────────────────────
class CallMapper:
    def map(self, call_data: CallData) -> Call:
        logger.debug(f"Маппинг call_id={getattr(call_data, 'call_id', 'нет')}")
        new_call = Call(**call_data.del_events())

        if call_data.call_date:
            d: datetime = call_data.call_date
            new_call.date = Date(
                call_id=new_call.call_id,
                year=d.year,
                month=d.month,
                day=d.day,
                hours=d.hour,
                minutes=d.minute,
                seconds=d.second,
            )

        new_call.events = []
        for idx, event in enumerate(call_data.events):
            new_event = Event(**event.del_api_vars(), id=idx, call_id=new_call.call_id)
            new_call.events.append(new_event)

            if api_vars := getattr(event, "api_vars", None):
                new_event.api_vars = [
                    ApiVars(
                        id=new_event.id,
                        event_id=new_call.call_id,
                        account_id=api_vars.get("account_id"),
                        num_a=api_vars.get("num_a"),
                        num_b=api_vars.get("num_b"),
                        num_c=api_vars.get("num_c"),
                        scenario_id=api_vars.get("scenario_id"),
                        scenario_counter=api_vars.get("scenario_counter"),
                        dest_link_name=api_vars.get("dest_link_name"),
                        dtmf=api_vars.get("dtmf"),
                        ivr_object_id=api_vars.get("ivr_object_id"),
                        ivr_schema_id=api_vars.get("ivr_schema_id"),
                        stt_answer=api_vars.get("stt_answer"),
                        stt_question=api_vars.get("stt_question"),
                        intent=api_vars.get("intent"),
                        # other=json.dumps(api_vars, separators=(",", ":")),
                    )
                ]
                logger.debug(f"ApiVars установлены для события {idx}: {new_event.api_vars}")

        logger.debug(f"Маппинг завершен для call_id: {new_call.call_id} с {len(new_call.events)} событиями")
        return new_call


# ──────────────────── AsyncCallRepository ──────────────────────
class AsyncCallRepository:
    """Асинхронное сохранение объектов Call в PostgreSQL (asyncpg)."""

    def __init__(self, config: Config) -> None:
        self.config: Config = config
        # ---------- движок ----------
        self._engine: AsyncEngine = create_async_engine(
            config.db_url_async,
            echo=False,
        )

        # ---------- фабрика сессий ----------
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
            autoflush=False,
        )

        self._initialized: bool = False
        logger.debug("AsyncCallRepository инициализирован")

    # ---------- создание схемы (один раз) ----------
    async def _init_db(self) -> None:
        if self._initialized:
            return
        async with self._engine.begin() as conn:
            await conn.execute(text(f"SET search_path TO {self.config.schema}"))
            await conn.run_sync(Base.metadata.create_all)
        self._initialized = True
        logger.info(f"Схема БД создана в search_path «{self.config.schema}»")

    # ---------- контекст сессии ----------
    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as sess:
            try:
                yield sess
            except Exception:
                await sess.rollback()
                raise
            finally:
                await sess.close()

    # ---------- helper ----------
    @staticmethod
    def _is_duplicate(err: IntegrityError) -> bool:
        return "duplicate key" in str(err.orig).lower()

    # ---------- API ----------
    async def save_many(self, calls: list[Call], *, batch_size: int = 500) -> None:
        if not calls:
            return
        await self._init_db()

        mode: Literal["insert_only", "upsert", "merge"] = self.config.insert_mode

        if mode == "upsert":
            await self._save_upsert(calls, batch_size)
        elif mode == "insert_only":
            await self._save_insert_only(calls, batch_size)
        elif mode == "merge":
            await self._save_merge(calls, batch_size)
        else:
            raise ValueError(f"Неподдерживаемый режим вставки: {mode}")

    async def _save_upsert(self, calls: list[Call], batch_size: int) -> None:
        for i in range(0, len(calls), batch_size):
            batch: list[Call] = calls[i : i + batch_size]
            stmt: Insert = insert(Call).values([call_to_dict(c) for c in batch])
            stmt = stmt.on_conflict_do_update(
                index_elements=["call_id"],
                set_={
                    col.name: getattr(stmt.excluded, col.name)
                    for col in Call.__table__.columns
                    if col.name != "call_id"
                },
            )
            async with self.session() as s:
                try:
                    await s.execute(stmt)
                    await s.commit()
                    logger.info("UPSERT выполнен: {}–{}", i, i + len(batch))
                except Exception as e:
                    await s.rollback()
                    logger.error("Ошибка UPSERT {}–{}: {}", i, i + len(batch), e)
                    raise

    async def _save_insert_only(self, calls: list[Call], batch_size: int) -> None:
        for i in range(0, len(calls), batch_size):
            batch: list[Call] = calls[i : i + batch_size]
            stmt: Insert = insert(Call).values([call_to_dict(c) for c in batch])
            stmt = stmt.on_conflict_do_nothing(index_elements=["call_id"])
            async with self.session() as s:
                try:
                    await s.execute(stmt)
                    await s.commit()
                    logger.info("INSERT ONLY выполнен: {}–{}", i, i + len(batch))
                except Exception as e:
                    await s.rollback()
                    logger.error("Ошибка INSERT ONLY {}–{}: {}", i, i + len(batch), e)
                    raise

    async def _save_merge(self, calls: list[Call], batch_size: int) -> None:
        async with self.session() as s:
            for i in range(0, len(calls), batch_size):
                batch: list[Call] = calls[i : i + batch_size]
                try:
                    s.add_all(batch)
                    await s.commit()
                    logger.info("MERGE: пакет {}–{} добавлен", i, i + len(batch))
                except IntegrityError as e:
                    await s.rollback()
                    if self._is_duplicate(e):
                        logger.warning("MERGE: дубликаты в пакете {}–{}, обрабатываем поштучно", i, i + len(batch))
                        for call in batch:
                            try:
                                await s.merge(call)
                            except Exception as inner:
                                logger.error("MERGE: ошибка по call_id {}: {}", call.call_id, inner)
                        await s.commit()
                    else:
                        logger.error("MERGE: критическая ошибка вставки {}–{}: {}", i, i + len(batch), e)
                        raise
