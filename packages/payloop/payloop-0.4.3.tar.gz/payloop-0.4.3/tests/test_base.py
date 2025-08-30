from unit_test_objects import UnitTestX, UnitTestY

from payloop._base import BaseInvoke
from payloop._config import Config
from payloop._constants import (
    ATHROPIC_CLIENT_TITLE,
    GOOGLE_CLIENT_TITLE,
    LANGCHAIN_CHATBEDROCK_CLIENT_TITLE,
    LANGCHAIN_CLIENT_PROVIDER,
    LANGCHAIN_OPENAI_CLIENT_TITLE,
    OPENAI_CLIENT_TITLE,
    PYDANTIC_AI_CLIENT_PROVIDER,
)


def test_list_to_json_native_types():
    assert BaseInvoke(Config(), "abc").list_to_json([1, 2, 3]) == [1, 2, 3]

    assert BaseInvoke(Config(), "abc").list_to_json([{"a": "b"}, {"c": "d"}]) == [
        {"a": "b"},
        {"c": "d"},
    ]

    assert BaseInvoke(Config(), "abc").list_to_json([[1, 2], [3, 4], [{"a", "b"}]]) == [
        [1, 2],
        [3, 4],
        [{"a", "b"}],
    ]

    assert BaseInvoke(Config(), "abc").list_to_json(
        [[1, {"a": "b"}], [{"c": "d"}, 2]]
    ) == [
        [1, {"a": "b"}],
        [{"c": "d"}, 2],
    ]


def test_list_to_json_object_simple():
    assert BaseInvoke(Config(), "abc").list_to_json([1, UnitTestX()]) == [
        1,
        {"a": 1, "b": 2},
    ]


def test_list_to_json_object_complex():
    assert BaseInvoke(Config(), "abc").list_to_json([1, UnitTestY()]) == [
        1,
        {"c": 3, "d": {"a": 1, "b": 2}},
    ]


def test_list_to_json_list_list_list():
    assert BaseInvoke(Config(), "abc").list_to_json([1, [2, [3, [4]]]]) == [
        1,
        [2, [3, [4]]],
    ]


def test_list_to_dict_to_list():
    assert BaseInvoke(Config(), "abc").list_to_json([{"a": 1, "b": [1, [2]]}]) == [
        {"a": 1, "b": [1, [2]]}
    ]


def test_dict_to_json_dict():
    assert BaseInvoke(Config(), "abc").dict_to_json({"a": "b", "c": "d"}) == {
        "a": "b",
        "c": "d",
    }


def test_dist_to_json_dict_has_dict():
    assert BaseInvoke(Config(), "abc").dict_to_json(
        {"a": {"b": {"c": "d"}, "e": 123}}
    ) == {"a": {"b": {"c": "d"}, "e": 123}}


def test_configure_for_streaming_usage_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_title = OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def", "stream": True}) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {"include_usage": False}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}


def test_configure_for_streaming_usage_streaming_options_is_not_dict_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_title = OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": 123}
    ) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }


def test_configure_for_streaming_usage_only_if_stream_is_true_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_title = OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def"}) == {"abc": "def"}


def test_configure_for_streaming_usage_langchain_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def", "stream": True}) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": {"include_usage": False}}
    ) == {"abc": "def", "stream": True, "stream_options": {"include_usage": True}}


def test_configure_for_streaming_usage_streaming_opts_is_not_dict_langchain_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage(
        {"abc": "def", "stream": True, "stream_options": 123}
    ) == {
        "abc": "def",
        "stream": True,
        "stream_options": {"include_usage": True},
    }


def test_configure_for_streaming_usage_only_if_stream_is_true_langchain_openai():
    invoke = BaseInvoke(Config(), "abc")
    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE

    assert invoke.configure_for_streaming_usage({"abc": "def"}) == {"abc": "def"}


def test_llm_is_openai():
    invoke = BaseInvoke(Config(), "abc")
    assert invoke.llm_is_openai() is False

    invoke._client_title = ATHROPIC_CLIENT_TITLE
    assert invoke.llm_is_openai() is False

    invoke._client_title = GOOGLE_CLIENT_TITLE
    assert invoke.llm_is_openai() is False

    invoke._client_title = OPENAI_CLIENT_TITLE
    assert invoke.llm_is_openai() is True

    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE
    assert invoke.llm_is_openai() is True

    invoke._client_provider = "abc"
    invoke._client_title = LANGCHAIN_OPENAI_CLIENT_TITLE
    assert invoke.llm_is_openai() is False

    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    invoke._client_title = "abc"
    assert invoke.llm_is_openai() is False


def test_provider_is_langchain():
    invoke = BaseInvoke(Config(), "abc")
    assert invoke.provider_is_langchain() is False

    invoke._client_provider = PYDANTIC_AI_CLIENT_PROVIDER
    assert invoke.provider_is_langchain() is False

    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    assert invoke.provider_is_langchain() is True


def test_client_is_bedrock():
    invoke = BaseInvoke(Config(), "abc")
    assert invoke.client_is_bedrock() is False

    invoke._client_provider = LANGCHAIN_CLIENT_PROVIDER
    assert invoke.client_is_bedrock() is False

    invoke._client_title = LANGCHAIN_CHATBEDROCK_CLIENT_TITLE
    assert invoke.client_is_bedrock() is True
