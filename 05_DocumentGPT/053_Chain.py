import os
import time
from dotenv import load_dotenv

load_dotenv()

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')  # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.runnables.base import RunnableLambda
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain.storage.file_system import LocalFileStore
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────
llm = ChatOpenAI(
    temperature=0.1,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
        Answer the question using ONLY the following context. 
        If you don't know the answer just say you don't know. DON'T make anything up.            

        Context: {context}
    """),
    ("human", "{question}"),
])


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

def invoke_chain(message):
    chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
    )
    response = chain.invoke(message)
    return response.content

# ────────────────────────────────────────
# 🍇 file load & cache
# ────────────────────────────────────────

# 업로드할 파일, 임베딩 벡터를 저장할 경로. 미리 생성해두기
upload_dir = r'./.cache/files'
embedding_dir = r'./.cache/embeddings'
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
if not os.path.exists(embedding_dir):
    os.makedirs(embedding_dir)    

# ------------------------------------------------------------------------
@st.cache_resource(show_spinner="Embedding file...")
def embed_file(file):
    file_content = file.read()
    file_path = os.path.join(upload_dir, file.name)

    # 업로드한 파일 저장
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 업로드된 '각각의 파일' 별로 embedding cache 디렉토리 지정하여 준비 
    cache_dir = LocalFileStore(os.path.join(embedding_dir, file.name))

    # 업로드된 파일을 load & split
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )

    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)

    # embeddings 생성하기 + cache 하기 
    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

    # 위 embeddings 을 vectorstore 에 넣기
    vectorstore = FAISS.from_documents(docs, cached_embeddings)

    # retriever 얻기
    retriever = vectorstore.as_retriever()
    return retriever    


# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────
st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
)

st.title("Document GPT")
st.markdown(
    """
안녕하세요!

이 챗봇을 사용해서 여러분의 파일들에 대해 AI에게 물어보세요!            
"""
)

with st.sidebar:
    file = st.file_uploader(
        label="Upload a .txt .pdf or .docs file",
        type=['pdf', 'txt', 'docx']
    )


# 일전에 만들어 봤던것과 같은 메세지 보내는 함수 작성
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})


# 메세지 히스토리 그리는 함수 
def paint_history():
    for message in st.session_state["messages"]:
        send_message(
            message["message"],
            message["role"],
            save=False,
        )

if file:
    
    retriever = embed_file(file)

    send_message("준비되었습니다. 질문하세요!", 'ai', save=False)
    paint_history()

    message = st.chat_input('업로드한 file 에 대해 질문을 남겨보세요')
    if message:
        send_message(message, 'human')
        result = invoke_chain(message)
        send_message(result, 'ai')

else:
    st.session_state['messages'] = []  # chat history 초깃값.  file 이 없거나 삭제되면 초기화

    