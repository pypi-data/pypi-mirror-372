#!/usr/bin/env python3

import os

from langchain_aws import ChatBedrock
from langchain_core.tools import tool

from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")


@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b


llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",  # or another Claude model
    region_name="us-east-1",  # use your active Bedrock region
)

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).langchain.register(chatbedrock=llm)

# Make sure registering the same client again does not cause an issue.
payloop.langchain.register(chatbedrock=llm)

# Test setting attribution.
payloop.attribution(
    parent_id=123,
    parent_name="Abc",
    parent_uuid="95473da0-5d7a-435d-babf-d64c5dabe971",
    subsidiary_id=456,
    subsidiary_name="Def",
    subsidiary_uuid="b789eaf4-c925-4a79-85b1-34d270342353",
)

llm_with_tools = llm.bind_tools([multiply])
print(llm_with_tools.invoke("What is 10 * 10?"))
