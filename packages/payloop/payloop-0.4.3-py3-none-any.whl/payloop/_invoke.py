r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import time
from collections.abc import AsyncIterator, Iterator

from botocore.eventstream import EventStream
from grpc.experimental.aio import UnaryStreamCall

from payloop._base import BaseInvoke
from payloop._iterable import Iterable as PayloopIterable
from payloop._iterator import AsyncIterator as PayloopAsyncIterator
from payloop._iterator import Iterator as PayloopIterator
from payloop._network import Collector
from payloop._streaming import StreamingBody as PayloopStreamingBody
from payloop._utils import merge_chunk


class Invoke(BaseInvoke):
    def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = self._method(**kwargs)

        if isinstance(raw_response, Iterator):
            return (
                PayloopIterator(self.config, raw_response)
                .configure_invoke(self)
                .configure_request(kwargs, start)
            )
        elif self.client_is_bedrock():
            if isinstance(raw_response["body"], EventStream):
                raw_response["body"] = (
                    PayloopIterable(self.config, raw_response["body"])
                    .configure_invoke(self)
                    .configure_request(kwargs, start)
                )
            else:
                raw_response["body"] = (
                    PayloopStreamingBody(self.config, raw_response["body"])
                    .configure_invoke(self)
                    .configure_request(kwargs, start)
                )

            return raw_response
        else:
            Collector(self.config).fire_and_forget(
                self._format_payload(
                    self._client_provider,
                    self._client_title,
                    self._client_version,
                    start,
                    time.time(),
                    self._format_kwargs(kwargs),
                    self._format_response(raw_response),
                )
            )

            return raw_response


class InvokeAsync(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = await self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )

        return raw_response


class InvokeAsyncIterator(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = await self._method(**kwargs)
        if isinstance(raw_response, AsyncIterator) or isinstance(
            raw_response, UnaryStreamCall
        ):
            return (
                PayloopAsyncIterator(self.config, raw_response)
                .configure_invoke(self)
                .configure_request(kwargs, start)
            )
        else:
            Collector(self.config).fire_and_forget(
                self._format_payload(
                    self._client_provider,
                    self._client_title,
                    self._client_version,
                    start,
                    time.time(),
                    self._format_kwargs(kwargs),
                    self._format_response(raw_response),
                )
            )

            return raw_response


class InvokeAsyncStream(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        stream = await self._method(**kwargs)

        raw_response = {}
        async for chunk in stream:
            raw_response = merge_chunk(raw_response, chunk.__dict__)
            yield chunk

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )


class InvokeStream(BaseInvoke):
    async def invoke(self, **kwargs):
        start = time.time()

        kwargs = self.configure_for_streaming_usage(kwargs)

        raw_response = await self._method(**kwargs)

        Collector(self.config).fire_and_forget(
            self._format_payload(
                self._client_provider,
                self._client_title,
                self._client_version,
                start,
                time.time(),
                self._format_kwargs(kwargs),
                self._format_response(raw_response),
            )
        )

        return raw_response
