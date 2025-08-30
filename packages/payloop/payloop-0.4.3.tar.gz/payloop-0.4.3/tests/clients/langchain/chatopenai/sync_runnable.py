#!/usr/bin/env python3

import os
from typing import TypedDict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI

from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

if os.environ.get("OPENAI_API_KEY", None) is None:
    raise RuntimeError("OPENAI_API_KEY is not set")


# Define the input/output schema
class MyInput(TypedDict):
    question: str


def build_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            ("human", "{question}"),
        ]
    )

    llm = ChatOpenAI(model="gpt-4o", streaming=True)

    payloop = Payloop(
        api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
    ).langchain.register(chatopenai=llm)

    # Make sure registering the same client again does not cause an issue.
    payloop.langchain.register(chatopenai=llm)

    # Test setting attribution.
    payloop.attribution(
        parent_id=123,
        parent_name="Abc",
        parent_uuid="95473da0-5d7a-435d-babf-d64c5dabe971",
        subsidiary_id=456,
        subsidiary_name="Def",
        subsidiary_uuid="b789eaf4-c925-4a79-85b1-34d270342353",
    )

    chain = prompt | llm | StrOutputParser()

    return chain


chain = build_chain()

input_data = {"question": "What is the capital of France?"}

print("Streaming response:\n")
for chunk in chain.stream(input_data):
    print(chunk, end="", flush=True)
