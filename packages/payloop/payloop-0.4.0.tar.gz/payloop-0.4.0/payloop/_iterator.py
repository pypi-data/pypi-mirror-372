r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import time

from payloop._base import BaseInvoke
from payloop._config import Config
from payloop._network import Collector
from payloop._utils import merge_chunk


class AsyncIterator:
    def __init__(self, config: Config, source_iterator):
        self.config = config
        self.source_iterator = source_iterator
        self.iterator = None
        self.raw_response = {}

    def __aiter__(self):
        self.iterator = self.source_iterator.__aiter__()
        return self

    async def __anext__(self):
        try:
            chunk = await self.iterator.__anext__()

            self.raw_response = merge_chunk(self.raw_response, chunk.__dict__)

            return chunk
        except StopAsyncIteration:
            raise

    async def __aenter__(self):
        await self.source_iterator.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        Collector(self.config).fire_and_forget(
            self.invoke._format_payload(
                self.invoke._client_provider,
                self.invoke._client_title,
                self.invoke._client_version,
                self.__time_start,
                time.time(),
                self.invoke._format_kwargs(self.__kwargs),
                self.invoke._format_response(self.raw_response),
            )
        )

        return await self.source_iterator.__aexit__(exc_type, exc, tb)

    def configure_invoke(self, invoke: BaseInvoke):
        self.invoke = invoke
        self._uses_protobuf = invoke._uses_protobuf
        return self

    def configure_request(self, kwargs, time_start):
        self.__kwargs = kwargs
        self.__time_start = time_start
        return self


class Iterator:
    def __init__(self, config: Config, source_iterator):
        self.config = config
        self.source_iterator = source_iterator
        self.raw_response = {}

    def __iter__(self):
        return self

    def __next__(self):
        try:
            chunk = next(self.source_iterator)

            self.raw_response = merge_chunk(self.raw_response, chunk.__dict__)

            return chunk
        except StopIteration:
            raise

    def __enter__(self):
        self.source_iterator.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        Collector(self.config).fire_and_forget(
            self.invoke._format_payload(
                self.invoke._client_provider,
                self.invoke._client_title,
                self.invoke._client_version,
                self.__time_start,
                time.time(),
                self.invoke._format_kwargs(self.__kwargs),
                self.invoke._format_response(self.raw_response),
            )
        )

        return self.source_iterator.__exit__(exc_type, exc, tb)

    def configure_invoke(self, invoke: BaseInvoke):
        self.invoke = invoke
        self._uses_protobuf = invoke._uses_protobuf
        return self

    def configure_request(self, kwargs, time_start):
        self.__kwargs = kwargs
        self.__time_start = time_start
        return self
