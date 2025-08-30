r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import asyncio

from payloop._base import BaseClient
from payloop._constants import (
    ATHROPIC_CLIENT_TITLE,
    GOOGLE_CLIENT_TITLE,
    LANGCHAIN_CHATBEDROCK_CLIENT_TITLE,
    LANGCHAIN_CLIENT_PROVIDER,
    LANGCHAIN_OPENAI_CLIENT_TITLE,
    OPENAI_CLIENT_TITLE,
    PYDANTIC_AI_CLIENT_PROVIDER,
)
from payloop._invoke import (
    Invoke,
    InvokeAsync,
    InvokeAsyncIterator,
    InvokeAsyncStream,
    InvokeStream,
)


class Anthropic(BaseClient):
    def register(self, client):
        if not hasattr(client, "messages"):
            raise RuntimeError("client provided is not instance of Anthropic")

        if not hasattr(client, "_payloop_installed"):
            client.messages.actual_create = client.messages.create
            client.messages.create = (
                Invoke(self.config, client.messages.actual_create)
                .set_client(None, ATHROPIC_CLIENT_TITLE, client._version)
                .invoke
            )

            client._payloop_installed = True

        return self


class Google(BaseClient):
    def register(self, client):
        if not hasattr(client, "models"):
            raise RuntimeError("client provided is not instance of genai.Client")

        if not hasattr(client, "_payloop_installed"):
            client.models.actual_generate_content = client.models.generate_content
            client.models.generate_content = (
                Invoke(self.config, client.models.actual_generate_content)
                .set_client(None, GOOGLE_CLIENT_TITLE, client._version)
                .uses_protobuf()
                .invoke
            )

            client._payloop_installed = True

        return self


class LangChain(BaseClient):
    def register(
        self, chatbedrock=None, chatgooglegenai=None, chatopenai=None, chatvertexai=None
    ):
        if (
            chatbedrock is None
            and chatgooglegenai is None
            and chatopenai is None
            and chatvertexai is None
        ):
            raise RuntimeError("LangChain::register called without client")

        if chatbedrock is not None:
            if not hasattr(chatbedrock, "client"):
                raise RuntimeError("client provided is not instance of ChatBedrock")

            if not hasattr(chatbedrock.client, "_payloop_installed"):
                chatbedrock.client._invoke_model = chatbedrock.client.invoke_model
                chatbedrock.client.invoke_model = (
                    Invoke(self.config, chatbedrock.client._invoke_model)
                    .set_client(
                        LANGCHAIN_CLIENT_PROVIDER,
                        LANGCHAIN_CHATBEDROCK_CLIENT_TITLE,
                        None,
                    )
                    .invoke
                )

                chatbedrock.client._invoke_model_with_response_stream = (
                    chatbedrock.client.invoke_model_with_response_stream
                )
                chatbedrock.client.invoke_model_with_response_stream = (
                    Invoke(
                        self.config,
                        chatbedrock.client._invoke_model_with_response_stream,
                    )
                    .set_client(
                        LANGCHAIN_CLIENT_PROVIDER,
                        LANGCHAIN_CHATBEDROCK_CLIENT_TITLE,
                        None,
                    )
                    .invoke
                )

                chatbedrock.client._payloop_installed = True

        if chatgooglegenai is not None:
            if not hasattr(chatgooglegenai, "client"):
                raise RuntimeError(
                    "client provided is not instance of ChatGoogleGenerativeAI"
                )

            if not hasattr(chatgooglegenai.client, "_payloop_installed"):
                chatgooglegenai.client._generate_content = (
                    chatgooglegenai.client.generate_content
                )
                chatgooglegenai.client.generate_content = (
                    Invoke(self.config, chatgooglegenai.client._generate_content)
                    .set_client(LANGCHAIN_CLIENT_PROVIDER, "chatgooglegenai", None)
                    .uses_protobuf()
                    .invoke
                )

                if chatgooglegenai.async_client is not None:
                    chatgooglegenai.async_client._stream_generate_content = (
                        chatgooglegenai.async_client.stream_generate_content
                    )
                    chatgooglegenai.async_client.stream_generate_content = (
                        InvokeAsyncIterator(
                            self.config,
                            chatgooglegenai.async_client._stream_generate_content,
                        )
                        .set_client(LANGCHAIN_CLIENT_PROVIDER, "chatgooglegenai", None)
                        .uses_protobuf()
                        .invoke
                    )

                chatgooglegenai.client._payloop_installed = True

        if chatopenai is not None:
            if not hasattr(chatopenai, "client") or not hasattr(
                chatopenai, "async_client"
            ):
                raise RuntimeError("client provided is not instance of ChatOpenAI")

            for client in [chatopenai.root_client, chatopenai.client._client]:
                if not hasattr(client, "_payloop_installed"):
                    client.beta._chat_completions_parse = (
                        client.beta.chat.completions.parse
                    )
                    client.beta.chat.completions.parse = (
                        Invoke(self.config, client.beta._chat_completions_parse)
                        .set_client(
                            LANGCHAIN_CLIENT_PROVIDER,
                            LANGCHAIN_OPENAI_CLIENT_TITLE,
                            None,
                        )
                        .invoke
                    )

                    client._chat_completions_create = client.chat.completions.create
                    client.chat.completions.create = (
                        Invoke(self.config, client._chat_completions_create)
                        .set_client(
                            LANGCHAIN_CLIENT_PROVIDER,
                            LANGCHAIN_OPENAI_CLIENT_TITLE,
                            None,
                        )
                        .invoke
                    )

                    client._payloop_installed = True

            for client in [
                chatopenai.root_async_client,
                chatopenai.async_client._client,
            ]:
                if not hasattr(client, "_payloop_installed"):
                    client.beta._chat_completions_parse = (
                        client.beta.chat.completions.parse
                    )
                    client.beta.chat.completions.parse = (
                        InvokeAsyncIterator(
                            self.config, client.beta._chat_completions_parse
                        )
                        .set_client(
                            LANGCHAIN_CLIENT_PROVIDER,
                            LANGCHAIN_OPENAI_CLIENT_TITLE,
                            None,
                        )
                        .invoke
                    )

                    client._chat_completions_create = client.chat.completions.create
                    client.chat.completions.create = (
                        InvokeAsyncIterator(
                            self.config, client._chat_completions_create
                        )
                        .set_client(
                            LANGCHAIN_CLIENT_PROVIDER,
                            LANGCHAIN_OPENAI_CLIENT_TITLE,
                            None,
                        )
                        .invoke
                    )

                    client._payloop_installed = True

        if chatvertexai is not None:
            if not hasattr(chatvertexai, "prediction_client"):
                raise RuntimeError("client provided isnot instance of ChatVertexAI")

            if not hasattr(chatvertexai.prediction_client, "_payloop_installed"):
                chatvertexai.prediction_client.actual_generate_content = (
                    chatvertexai.prediction_client.generate_content
                )
                chatvertexai.prediction_client.generate_content = (
                    Invoke(
                        self.config,
                        chatvertexai.prediction_client.actual_generate_content,
                    )
                    .set_client(LANGCHAIN_CLIENT_PROVIDER, "chatvertexai", None)
                    .uses_protobuf()
                    .invoke
                )

                chatvertexai.prediction_client._payloop_installed = True

        return self


class OpenAi(BaseClient):
    def register(self, client, _provider=None, stream=False):
        if not hasattr(client, "chat"):
            raise RuntimeError("client provided is not instance of OpenAI")

        if not hasattr(client, "_payloop_installed"):
            client.beta._chat_completions_parse = client.beta.chat.completions.parse
            client.chat._completions_create = client.chat.completions.create

            try:
                asyncio.get_running_loop()

                if stream is True:
                    client.beta.chat.completions.parse = (
                        InvokeAsyncStream(
                            self.config, client.beta._chat_completions_parse
                        )
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
                    client.chat.completions.create = (
                        InvokeAsyncStream(
                            self.config,
                            client.chat._completions_create,
                        )
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
                else:
                    client.beta.chat.completions.parse = (
                        InvokeAsync(self.config, client.beta._chat_completions_parse)
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
                    client.chat.completions.create = (
                        InvokeAsync(
                            self.config,
                            client.chat._completions_create,
                        )
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
            except RuntimeError:
                if stream is True:
                    client.beta.chat.completions.parse = (
                        InvokeStream(self.config, client.beta._chat_completions_parse)
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
                    client.chat.completions.create = (
                        InvokeStream(
                            self.config,
                            client.chat._completions_create,
                        )
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
                else:
                    client.beta.chat.completions.parse = (
                        Invoke(self.config, client.beta._chat_completions_parse)
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )
                    client.chat.completions.create = (
                        Invoke(
                            self.config,
                            client.chat._completions_create,
                        )
                        .set_client(_provider, OPENAI_CLIENT_TITLE, client._version)
                        .invoke
                    )

            client._payloop_installed = True

        return self


class PydanticAi(BaseClient):
    def register(self, client):
        if not hasattr(client, "chat"):
            raise RuntimeError("client provided was not instantiated using PydanticAi")

        if not hasattr(client, "_payloop_installed"):
            client.chat.completions.actual_chat_completions_create = (
                client.chat.completions.create
            )

            client.chat.completions.create = (
                InvokeAsyncIterator(
                    self.config,
                    client.chat.completions.actual_chat_completions_create,
                )
                .set_client(PYDANTIC_AI_CLIENT_PROVIDER, "openai", client._version)
                .invoke
            )

            client._payloop_installed = True

        return self
