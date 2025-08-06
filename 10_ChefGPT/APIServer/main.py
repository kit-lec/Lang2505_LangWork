from fastapi import FastAPI

from pydantic import BaseModel, Field

class Quote(BaseModel):
    quote: str = Field(
        description="The quote that Drakos Ephesius said.",
    )
    year: int = Field(
        description="The year when Drakos Ephesius said the quote.",
    )



app = FastAPI(
    # ↓ 'Drakos Ephesius 명언 제공자'
    title="Drakos Ephesius Quote Giver",
    # ↓ Drakos Ephesius 의 실제 명언을 가져옵니다.
    description="Get a real quote said by Drakos Ephesius himself.",

    servers=[
        {"url": "https://judy-speed-joe-reliability.trycloudflare.com"},
    ],
)

# url 요청 --> 함수가 처리 <= Routing

# ↓ /quote 라는 URL endpoint 에 Get request 를 받으면, 아래 get_quote() 함수가 실행된다.
@app.get(
    path="/quote",
    # ↓ summary: "이 endpoint 는 Drakos Ephesius의 명언을 무작위로 리턴합니다"
    summary="Returns a random quote by Drakos Ephesius",
    # ↓ description: "이 GET 요청을 받으면 이 endpoint 는 Drakos Ephesius 가 말한 실제 명언을 return 합니다"
    description="Upon receiving a GET request this endpoint will return a real quiote said by Drakos Ephesius himself.",
    # ↓ resposne 도 우리가 무엇으로 답변할지 설명할 수 있다.
    #   "Quote object 는 Drakos Ephesius 가 말한 명언과 그 명언을 말한 날짜를 포합합니다"
    response_description="A Quote object that contains the quote said by Drakos Ephesius and the date when the quote was said.",

    response_model=Quote,
)
def get_quote():
    return {
        "quote": "Life is short so eat it all.",
        "year": 1950,
    }