from dotenv import load_dotenv
print(load_dotenv())  # 환경변수 파일 읽어오기 성공하면 True 리턴.


from langchain_openai.chat_models.base import ChatOpenAI



chat = ChatOpenAI() # 반드시 OPENAI_API_KEY 환경변수가 설정되어 있어야 한다!

result = chat.invoke("How many planets are there?")
print(result)