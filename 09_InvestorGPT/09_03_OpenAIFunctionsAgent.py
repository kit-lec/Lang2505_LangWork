from dotenv import load_dotenv
load_dotenv()

import warnings
warnings.filterwarnings('ignore')

from langchain_openai.chat_models.base import ChatOpenAI
from langchain.agents.initialize import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_core.tools.simple import Tool
from langchain_core.tools.base import BaseTool

from pydantic import BaseModel, Field
from typing import Any, Type  # typing 은 Python 의 기본 내장모듈

# pydantic 의 BaseModel 구현. => 사용자 정의 데이터 모델 정의
#   - 입력데이터의 타입검증, 자동변환, 직렬화/역직렬화 등의 처리기능 제공됨.
class CalculatorToolArgsSchema(BaseModel):    
    a: float = Field(description="The first number")
    b: float = Field(description="The second number")


# BaseTool 을 구현하여 커스텀 Tool 클래스 생성
class CalculatorTool(BaseTool):
    name: Type[str] = "CalculatorTool"  # tool 의 이름에 공백 있으면 안됨!
    description: Type[str] = """
    Use this to perform sums of two numbers.
    The first and second arguments should be numbers.
    Only receives two arguments.
    """
    # argument 의 스키마 정의
    # argument 들이 이 스키마를 따르도록 지정
    # a 는 실수형, b 도 실수형.
    args_schema: Type[CalculatorToolArgsSchema] = CalculatorToolArgsSchema

    # 이 툴이 사용되었을때 실행할 코드
    # def _run(self, *args: Any, **kwargs: Any) -> Any:
    def _run(self, a, b):    
        return a + b


llm = ChatOpenAI(
    temperature=0.1,
    model_name="gpt-4o-mini",
)

# def plus(inputs):
#     a, b = inputs.split(",")
#     return float(a) + float(b)

agent = initialize_agent(
    llm=llm,
    verbose=True,
    agent=AgentType.OPENAI_FUNCTIONS,
    tools=[
        CalculatorTool(),
    ],
)

prompt = "Cost of $355.39 + $924.87 + $721.2 + $1940.29 + $573.63 + $65.72 + $35.00 + $552.00 + $76.16 + $29.12"

agent.invoke(prompt)

