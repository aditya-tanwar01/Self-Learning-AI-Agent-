from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor

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


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a research assistant.

Research the user's query using the search tool when necessary.

Use the search tool only when you need additional information.
Do not repeatedly search for the same information.

After gathering enough information, stop using tools and produce the final answer.

Return ONLY valid JSON.

The response must contain exactly these four fields:

topic
summary
sources
tools_used

The topic field must be a string.

The summary field must be a string.

The sources field must be an array of objects.
Each source object must contain:
title
url

The tools_used field must be an array of strings.

Do not add extra fields.
Do not return markdown.
Do not return a code block.
""",
        ),

        ("human", "{query}"),

        ("placeholder", "{agent_scratchpad}"),
    ]
)


tools = [
    search_tool
]


agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)


agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True
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

        raw_response = agent_executor.invoke(
            {
                "query": request.query,
                "chat_history": []
            }
        )

        output = raw_response.get("output")

        print("AI OUTPUT:", output)

        structured_response = parser.parse(output)

        print("PARSED RESPONSE:", structured_response)

        return structured_response.model_dump()

    except Exception as e:

        print("RESEARCH ERROR:", str(e))

        return {
            "topic": request.query,
            "summary": f"AI response could not be parsed: {str(e)}",
            "sources": [],
            "tools_used": []
        }