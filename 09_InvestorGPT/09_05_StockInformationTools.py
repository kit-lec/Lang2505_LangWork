import os
import requests
from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.initialize import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_core.tools.base import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper

from dotenv import load_dotenv
load_dotenv()
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
print(f'\tALPHA_VANTAGE_API_KEY={alpha_vantage_api_key[:5]}...')

llm = ChatOpenAI(temperature=0.1)

# tool 정의

# 회사 심볼 tool
class StockMarketSymbolSearchToolArgsSchema(BaseModel):
    query: str = Field(
        description="The query you will search for.Example query: Stock Market Symbol for Apple Company"        
    )

class StockMarketSymbolSearchTool(BaseTool):
    name: Type[str] = "StockMarketSymbolSearchTool"
    description: Type[str] = """
    Use this tool to find the stock market symbol for a company.
    It takes a query as an argument.   
    """
    args_schema: Type[StockMarketSymbolSearchToolArgsSchema] = StockMarketSymbolSearchToolArgsSchema

    def _run(self, query):
        ddg = DuckDuckGoSearchAPIWrapper()
        return ddg.run(query)



agent = initialize_agent(
    llm=llm,
    verbose=True,
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=[
        StockMarketSymbolSearchTool(),
    ],
)

prompt = "Give me financial information on Cloudflare's stock and help me analyze if it's a potential good investment."

agent.invoke(prompt)

