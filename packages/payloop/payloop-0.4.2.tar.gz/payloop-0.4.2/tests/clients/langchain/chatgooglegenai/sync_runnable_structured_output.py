#!/usr/bin/env python3

import os
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None) is None:
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set")


class Output(BaseModel):
    allergens: List[str]


prompt = ChatPromptTemplate(
    [
        ("system", "You are an expert in identifying allergens in food products."),
        ("user", "What are the allergens in the following product: {product_name}"),
    ]
)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).langchain.register(chatgooglegenai=llm)

# Make sure registering the same client again does not cause an issue.
payloop.langchain.register(chatgooglegenai=llm)

# Test setting attribution.
payloop.attribution(
    parent_id=123,
    parent_name="Abc",
    parent_uuid="95473da0-5d7a-435d-babf-d64c5dabe971",
    subsidiary_id=456,
    subsidiary_name="Def",
    subsidiary_uuid="b789eaf4-c925-4a79-85b1-34d270342353",
)

chain = prompt | llm.with_structured_output(Output)

print(chain.invoke({"product_name": "Lamen"}))
