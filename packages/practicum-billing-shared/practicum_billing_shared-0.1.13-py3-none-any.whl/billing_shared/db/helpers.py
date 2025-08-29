import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, List, Type, TypeVar, Union

import aio_pika
from pydantic import AnyUrl
from sqlalchemy import BooleanClauseList, Column, ColumnElement, Select, delete, select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.interfaces import ORMOption

from .models import Base
from .schemas import PaymentTaskData, RefundTaskData


class DbAgent:
    def __init__(
        self, url: AnyUrl, echo: bool = False, echo_pool: bool = False, pool_size: int = 5, max_overflow: int = 10
    ) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=str(url),
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self._session_factory = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            yield session

    async def create_db_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_db_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class DbRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _compose_select_stmt(
        self,
        model: Type[ModelT],
        filters: List[Union[ColumnElement[bool], BooleanClauseList]] = [],
        options: List[ORMOption] = [],
        joins: List[InstrumentedAttribute] = [],
        join_filters: List[Union[ColumnElement[bool], BooleanClauseList]] = [],
    ) -> Select:
        stmt = select(model)
        for filter_condition in filters:
            stmt = stmt.where(filter_condition)
        for join_target in joins:
            stmt = stmt.join(join_target)
        for j_filter_condition in join_filters:
            stmt = stmt.where(j_filter_condition)

        stmt = stmt.options(*options)
        return stmt

    async def get(
        self,
        model: Type[ModelT],
        filters: List[Union[ColumnElement[bool], BooleanClauseList]] = [],
        options: List[ORMOption] = [],
        joins: List[InstrumentedAttribute] = [],
        join_filters: List[Union[ColumnElement[bool], BooleanClauseList]] = [],
    ) -> ModelT | None:
        stmt = self._compose_select_stmt(model, filters, options, joins, join_filters)
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list(
        self,
        model: Type[ModelT],
        filters: List[Union[ColumnElement[bool], BooleanClauseList]] = [],
        options: List[ORMOption] = [],
        joins: List[InstrumentedAttribute] = [],
        join_filters: List[Union[ColumnElement[bool], BooleanClauseList]] = [],
    ) -> List[ModelT]:
        stmt = self._compose_select_stmt(model, filters, options, joins, join_filters)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add(self, model_obj: ModelT) -> None:
        self._session.add(model_obj)
        await self._session.commit()

    async def update(
        self,
        model: Type[ModelT],
        filters: List[Union[ColumnElement[bool], BooleanClauseList]],
        update_kws: dict[str, Any],
    ) -> None:
        stmt = update(model)

        for filter_condition in filters:
            stmt = stmt.where(filter_condition)

        stmt = stmt.values(**update_kws)
        await self._session.execute(stmt)
        await self._session.commit()

    async def delete(self, model: Type[ModelT], col: Column, values: List[Any]) -> None:
        stmt = delete(model).where(col.in_(values))
        await self._session.execute(stmt)
        await self._session.commit()

    async def refresh(self, model_obj: ModelT) -> ModelT:
        await self._session.refresh(model_obj)


class RabbitAdapter:
    connection: aio_pika.RobustConnection
    channel: aio_pika.RobustChannel
    queues: dict[str, aio_pika.RobustQueue]

    def __init__(
        self,
        url: str,
        exchange_name: str = "billing",
        payments_wait_qname: str = "payments.wait",
        payments_check_qname: str = "payments.check",
        refunds_wait_qname: str = "refunds.wait",
        refunds_check_qname: str = "refunds.check",
    ):
        self.url = url
        self.exchange_name = exchange_name
        self.payments_wait_qname = payments_wait_qname
        self.payments_check_qname = payments_check_qname
        self.refunds_wait_qname = refunds_wait_qname
        self.refunds_check_qname = refunds_check_qname

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(self.exchange_name)

        pwq = await self.channel.declare_queue(
            self.payments_wait_qname,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self.exchange_name,
                "x-dead-letter-routing-key": self.payments_check_qname,
                "x-message-ttl": 30000,
            },
        )
        await pwq.bind(self.exchange, routing_key=self.payments_wait_qname)
        pcq = await self.channel.declare_queue(self.payments_check_qname, durable=True)
        await pcq.bind(self.exchange, routing_key=self.payments_check_qname)

        rwq = await self.channel.declare_queue(
            self.refunds_wait_qname,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self.exchange_name,
                "x-dead-letter-routing-key": self.refunds_check_qname,
                "x-message-ttl": 30000,
            },
        )
        await rwq.bind(self.exchange, routing_key=self.refunds_wait_qname)
        rcq = await self.channel.declare_queue(self.refunds_check_qname, durable=True)
        await rcq.bind(self.exchange, routing_key=self.refunds_check_qname)

        self.queues = {
            self.payments_wait_qname: pwq,
            self.payments_check_qname: pcq,
            self.refunds_wait_qname: rwq,
            self.refunds_check_qname: rcq,
        }

    async def publish(self, data: Union[PaymentTaskData, RefundTaskData]) -> None:
        message = aio_pika.Message(
            body=data.model_dump_json().encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        match type(data):
            case t if t is PaymentTaskData:
                routing_key = self.payments_wait_qname
            case t if t is RefundTaskData:
                routing_key = self.refunds_wait_qname
            case _:
                raise TypeError("RMQ task data of uknown type")

        await self.exchange.publish(message, routing_key=routing_key)

    async def subscribe(self, qname: str, handler: Callable) -> None:
        q = self.queues.get(qname)
        if not q:
            raise Exception("Wrong q name")
        await q.consume(handler)

    async def stop(self) -> None:
        if self.channel is not None:
            await self.channel.close()
        if self.connection is not None:
            await self.connection.close()
