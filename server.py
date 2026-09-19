from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from tools import search_tool

import os


load_dotenv()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://self-learning-ai-agent-1.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Source(BaseModel):
    title: str
    url: str


class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[Source]
    tools_used: list[str]


class ResearchRequest(BaseModel):
    query: str


llm = ChatOpenAI(
    model="Atria-Dawn-Preview",
    api_key=os.getenv("ATRIA_API_KEY"),
    base_url="https://api.atria-asi.ai/v1"
)


parser = PydanticOutputParser(
    pydantic_object=ResearchResponse
)


@app.get("/")
def home():
    return {
        "message": "Self Learning AI backend is running"
    }


@app.post("/research")
def research(request: ResearchRequest):

    try:

        print("USER QUERY:", request.query)

        # Search the web
        search_results = search_tool.run(request.query)

        print("SEARCH RESULTS:", search_results)

        # Ask AI to analyze the search results
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an AI research assistant.

Use the provided web search results to answer the user's research question.

Return ONLY valid JSON.

The JSON must contain exactly these fields:

topic
summary
sources
tools_used

topic must be a string.

summary must be a clear and useful explanation.

sources must be an array of objects.
Each object must contain:
title
url

tools_used must be an array of strings.

Do not use markdown.
Do not use code blocks.
Do not add extra fields.

{format_instructions}
"""
                ),
                (
                    "human",
                    """
User question:
{query}

Web search results:
{search_results}
"""
                )
            ]
        ).partial(
            format_instructions=parser.get_format_instructions()
        )

        messages = prompt.format_messages(
            query=request.query,
            search_results=search_results
        )

        response = llm.invoke(messages)

        print("AI RAW RESPONSE:", response.content)

        structured_response = parser.parse(response.content)

        print("PARSED RESPONSE:", structured_response)

        return structured_response.model_dump()

    except Exception as e:

        print("RESEARCH ERROR:", str(e))

        return {
            "topic": request.query,
            "summary": f"Research failed: {str(e)}",
            "sources": [],
            "tools_used": []
        }