from dotenv import load_dotenv
load_dotenv()

import warnings
warnings.filterwarnings('ignore')

from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.initialize import initialize_agent
from langchain.agents.agent_types import AgentType
# from langchain_core.tools.structured import StructuredTool
from langchain_core.tools.simple import Tool  # <- Tool


llm = ChatOpenAI(
    temperature=0.1,
    model_name="gpt-4o-mini",
)

def plus(inputs):  # inputs <-  "10,20" 과 같은 형태의 str 로 전달 받는다.
    a, b = inputs.split(",")
    return float(a) + float(b)

agent = initialize_agent(
    llm=llm,
    verbose=True,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    tools=[
        Tool.from_function(
            func=plus,
            name="Sum Calculator",
            description="Use this to perform sums of two numbers. Use this tool by sending a pair of numbers separated by a comma.\nExample:1,2",
        ),
    ],
)

prompt = "Cost of $355.39 + $924.87 + $721.2 + $1940.29 + $573.63 + $65.72 + $35.00 + $552.00 + $76.16 + $29.12"

agent.invoke(prompt)

