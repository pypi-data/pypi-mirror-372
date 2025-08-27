# -*- coding: UTF-8 -*-
import asyncio
import typing

import dmPython

from dmasyncwrapper.abstract import AbstractConnection, AbstractCursor
from dmasyncwrapper.logger import logger


class Cursor(AbstractCursor):

    def __init__(
            self, *, sync_cursor: dmPython.Cursor,
            connection: AbstractConnection,
    ):
        self._sync_cursor: dmPython.Cursor = sync_cursor
        self._connection: AbstractConnection = connection

    @property
    def description(self):
        return self._sync_cursor.description

    @property
    def rowcount(self):
        return self._sync_cursor.rowcount

    async def callproc(self, procname, *args, **kwargs):
        return await asyncio.to_thread(
            self._sync_cursor.callproc, procname, *args, **kwargs)

    async def close(self):
        return await asyncio.to_thread(self._sync_cursor.close)

    async def execute(
            self, operation: str, parameters: typing.Sequence = None,
            *args, **kwargs,
    ):
        return await asyncio.to_thread(
            self._sync_cursor.execute, operation, parameters,
            *args, **kwargs)

    async def executemany(
            self, operation: str,
            seq_of_parameters: typing.Sequence[typing.Sequence] = None,
            max_batch: int = 1000,
            *args, **kwargs,
    ):
        # FIXME:
        #  dmPython驱动致命bug，executemany方法单次参数组数量超过某个值后，
        #  写入不会报任何错而是返回成功但数据库中产生大量异常数据。
        #  震惊，震撼，震碎三观。
        if len(seq_of_parameters) < max_batch:
            await asyncio.to_thread(
                self._sync_cursor.executemany, operation,
                seq_of_parameters, *args, **kwargs)
        else:
            logger.info(
                'seq_of_parameters length is %d, splitting into batches of %d',
                len(seq_of_parameters), max_batch)
            for i in range(0, len(seq_of_parameters), max_batch):
                each_batch = seq_of_parameters[i:i + max_batch]
                await asyncio.to_thread(
                    self._sync_cursor.executemany, operation,
                    each_batch, *args, **kwargs)

    async def fetchone(self) -> tuple | None:
        return await asyncio.to_thread(self._sync_cursor.fetchone)

    async def fetchmany(self, size=None):
        if size is None:
            size = self._sync_cursor.arraysize
        return await asyncio.to_thread(self._sync_cursor.fetchmany, size)

    async def fetchall(self) -> list[tuple]:
        return await asyncio.to_thread(self._sync_cursor.fetchall)

    async def nextset(self):
        return await asyncio.to_thread(self._sync_cursor.nextset)

    @property
    def arraysize(self):
        return self._sync_cursor.arraysize

    async def setinputsizes(self, *args, **kwargs):
        return await asyncio.to_thread(
            self._sync_cursor.setinputsizes, *args, **kwargs)

    async def setoutputsize(self, *args, **kwargs):
        return await asyncio.to_thread(
            self._sync_cursor.setoutputsize, *args, **kwargs)

    async def __aenter__(self) -> typing.Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return await self.close()
