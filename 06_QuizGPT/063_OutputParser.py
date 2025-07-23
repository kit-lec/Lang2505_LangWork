import os
import time
from dotenv import load_dotenv

load_dotenv()

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')  # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!
#─────────────────────────────────────────────────────────────────────────────────────────

import streamlit as st

from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain_text_splitters.character import CharacterTextSplitter

from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain_community.retrievers.wikipedia import WikipediaRetriever

import json
from langchain_core.output_parsers.base import BaseOutputParser


# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────

class JsonOutputParser(BaseOutputParser):

    # OutputParser 는 parse(text) 가 구현되어야 한다.
    # text 에는 LLM 에 의해 생성된 결과가 전달될거다.
    def parse(self, text):
        # 응답의 앞뒤 문자열 제거
        text = text.replace("```", "").replace("json", "")
        # 파이썬 객체 <- JSON text
        return json.loads(text)
        
    
output_parser = JsonOutputParser()

llm = ChatOpenAI(
    temperature=0.1,
    model='gpt-3.5-turbo-1106',
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

question_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a helpful assistant that is role playing as a teacher.
         
    Based ONLY on the following context make 10 questions to test the user's knowledge about the text.
   
    Each question should have 4 answers, three of them must be incorrect and one should be correct.
         
    Use (o) to signal the correct answer.
         
    Question examples:
         
    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
         
    Your turn!
         
    Context: {context}
    """),
])

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

question_chain = {"context": format_docs} | question_prompt | llm

# 위 question_chain 으로 만들어진 퀴즈를 입력받아 json 처럼 format 해줄 prompt
formatting_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a powerful formatting algorithm.
     
    You format exam questions into JSON format.
    Answers with (o) are the correct ones.
     
    Example Input:

    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
   
     
    Example Output:
     
    ```json
    {{ "questions": [
            {{
                "question": "What is the color of the ocean?",
                "answers": [
                        {{
                            "answer": "Red",
                            "correct": false
                        }},
                        {{
                            "answer": "Yellow",
                            "correct": false
                        }},
                        {{
                            "answer": "Green",
                            "correct": false
                        }},
                        {{
                            "answer": "Blue",
                            "correct": true
                        }},
                ]
            }},
                        {{
                "question": "What is the capital or Georgia?",
                "answers": [
                        {{
                            "answer": "Baku",
                            "correct": false
                        }},
                        {{
                            "answer": "Tbilisi",
                            "correct": true
                        }},
                        {{
                            "answer": "Manila",
                            "correct": false
                        }},
                        {{
                            "answer": "Beirut",
                            "correct": false
                        }},
                ]
            }},
                        {{
                "question": "When was Avatar released?",
                "answers": [
                        {{
                            "answer": "2007",
                            "correct": false
                        }},
                        {{
                            "answer": "2001",
                            "correct": false
                        }},
                        {{
                            "answer": "2009",
                            "correct": true
                        }},
                        {{
                            "answer": "1998",
                            "correct": false
                        }},
                ]
            }},
            {{
                "question": "Who was Julius Caesar?",
                "answers": [
                        {{
                            "answer": "A Roman Emperor",
                            "correct": true
                        }},
                        {{
                            "answer": "Painter",
                            "correct": false
                        }},
                        {{
                            "answer": "Actor",
                            "correct": false
                        }},
                        {{
                            "answer": "Model",
                            "correct": false
                        }},
                ]
            }}
        ]
     }}
    ```
    Your turn!

    Questions: {context}


    """),
])

formmatting_chain = formatting_prompt | llm




# ────────────────────────────────────────
# 🍇 file load & cache
# ────────────────────────────────────────

file_dir = os.path.dirname(os.path.realpath(__file__)) # *.py 파일의 '경로'만
upload_dir = os.path.join(file_dir, '.cache/quiz_files')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# 이번예제에선 embed, vector store 필요없이 오로지 '문서' 만 필요
#  문서 업로드 와 split 까지만 해두자.
@st.cache_resource(show_spinner="Loading file...")
def split_file(file):
    file_content = file.read()
    file_path = os.path.join(upload_dir, file.name)
   
    with open(file_path, "wb") as f:
        f.write(file_content)

    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )

    loader = UnstructuredFileLoader(file_path)

    docs = loader.load_and_split(text_splitter=splitter)

    return docs



# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────
st.set_page_config(
    page_title="QuizGPT",
    page_icon="👩‍🚒",
)

st.title("QuizGPT")

with st.sidebar:
    docs = []

    choice = st.selectbox(
        label="Choose what you want to use.",
        options=(
            "File",
            "Wikipedia Article",
        ),
    )

    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx , .txt or .pdf file",
            type=["pdf", "txt", "docx"],
        )
        if file:
            docs = split_file(file)

    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            retriever = WikipediaRetriever(top_k_results=5)

            with st.status("Searching Wikipedia..."):
                docs = retriever.invoke(topic)


if not docs:
    # 사용자 welcome 메세지 출력
    st.markdown(
        """
    Welcome to QuizGPT.
               
    I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
               
    Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    start = st.button("Generate Quiz")
    if start:
        # questions_response = question_chain.invoke(docs)   
        # formatting_response = formmatting_chain.invoke({
        #     "context": questions_response.content,
        # })

        # 위 두번의 chain  호출을 아래와 같이 간단하게(?) 만들수 있다.
        chain = {"context": question_chain} | formmatting_chain | output_parser
        response = chain.invoke(docs)
        st.write(response) # 확인용

        



























