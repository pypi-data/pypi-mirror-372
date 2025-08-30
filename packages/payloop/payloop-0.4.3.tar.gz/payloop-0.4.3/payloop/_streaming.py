r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import json
import time

from payloop._base import BaseInvoke
from payloop._config import Config
from payloop._network import Collector
from payloop._utils import bytes_to_json


class StreamingBody:
    def __init__(self, config: Config, source_streaming_body):
        self.config = config
        self.source_streaming_body = source_streaming_body
        self.raw_response = None

    def __getattr__(self, name):
        return getattr(self.source_streaming_body, name)

    def configure_invoke(self, invoke: BaseInvoke):
        self.invoke = invoke
        return self

    def configure_request(self, kwargs, time_start):
        self._kwargs = kwargs
        self._time_start = time_start

        if self.invoke.client_is_bedrock():
            self._kwargs = bytes_to_json(self._kwargs)

        return self

    def read(self, *args, **kwargs):
        data = self.source_streaming_body.read(*args, **kwargs)

        Collector(self.config).fire_and_forget(
            self.invoke._format_payload(
                self.invoke._client_provider,
                self.invoke._client_title,
                self.invoke._client_version,
                self._time_start,
                time.time(),
                self.invoke._format_kwargs(self._kwargs),
                self.invoke._format_response(json.loads(data.decode())),
            )
        )

        return data
