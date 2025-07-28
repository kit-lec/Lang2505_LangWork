import os
from dotenv import load_dotenv

print(f'✅ {os.path.basename( __file__ )} 실행됨')
load_dotenv()  #
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}')
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st
from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_core.runnables.base import RunnableLambda
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────
llm = ChatOpenAI(
    temperature=0.1,
)

answers_prompt = ChatPromptTemplate.from_template("""
    Using ONLY the following context answer the user's question. If you can't just say you don't know, don't make anything up.
                                                 
    Then, give a score to the answer between 0 and 5.

    If the answer answers the user question the score should be high, else it should be low.

    Make sure to always include the answer's score even if it's 0.

    Context: {context}
                                                 
    Examples:
                                                 
    Question: How far away is the moon?
    Answer: The moon is 384,400 km away.
    Score: 5
                                                 
    Question: How far away is the sun?
    Answer: I don't know
    Score: 0
                                                 
    Your turn!

    Question: {question}
""")



def get_answers(inputs):
    docs = inputs['docs']
    question = inputs['question']

    # 각 Document 를 처리해줄 chain 
    answers_chain = answers_prompt | llm

    return {
        "question": question,
        "answers":     [
                # 각각의 Document 마다 Dict 생성
                {
                    "answer": answers_chain.invoke(
                                {"question": question, "context": doc.page_content}
                            ).content,
                    "source": doc.metadata['source'],
                    'date': doc.metadata['lastmod'],
                }
                for doc in docs
            ]
    }


choose_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Use ONLY the following pre-existing answers to answer the user's question.

            Use the answers that have the highest score (more helpful) and favor the most recent ones.

            Cite sources and return the sources as it is.

            Answers: {answers}
            """,
        ),
        ("human", "{question}"),
    ]
)


# 입력은 '모든 answer' 와  '사용자 question'
# 출력은 선택된 최종 answer.
def choose_answer(inputs):
    answers = inputs['answers']
    question = inputs['question']
    choose_chain = choose_prompt | llm

    condensed = "\n\n".join(
        f"Answer:{answer['answer']}\nSource:{answer['source']}\nDate:{answer['date']}\n"
        for answer in answers
    )

    return choose_chain.invoke({
        "question": question,
        "answers": condensed,
    })



# ────────────────────────────────────────
# 🍇 file load & cache
# ────────────────────────────────────────


def parse_page(soup):
    header = soup.find("header")
    footer = soup.find('footer')

    if header:
        header.decompose()

    if footer:
        footer.decompose()
    
    return (str(soup.get_text())
            .replace(r"\n", " ")
            .replace(r"\xa0", " "))
    
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1000,
    chunk_overlap=200,
)


@st.cache_resource(show_spinner="Fetching URL...")
def load_website(url):
    loader = SitemapLoader(
        url,
        # filter_urls=[
        #     r"^(.*\/news\/).*",  
        # ],

        parsing_function=parse_page,
    )
    loader.max_depth = 3
    loader.requests_per_second = 1
    loader.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}

    docs = loader.load_and_split(text_splitter=splitter) 

# BadRequestError: Error code: 400 - {'error': {'message': 'Requested 630770 tokens, max
# 300000 tokens per request', 'type': 'max_tokens_per_request', 'param': None, 'code':
# 'max_tokens_per_request'}}    

    batch_size = 100  # 한번에 모델에 건네줄 Document 개수 (적절한 값 설정)

    substores = []
    for i in range(0, len(docs), batch_size):
        chunk = docs[i: i + batch_size]
        vector_store = FAISS.from_documents(chunk, OpenAIEmbeddings())
        substores.append(vector_store)

    # 여러 vector store 병합
    vector_store = substores[0]
    for store in substores[1:]:
        vector_store.merge_from(store)

    return vector_store.as_retriever()



# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────
st.set_page_config(
    page_title="SiteGPT",
    page_icon="🖥️",
)

with st.sidebar:
    url = st.text_input(
        "Write down a URL",
        placeholder="https://example.com",
    )

st.markdown(
"""
    # SiteGPT
           
    Ask questions about the content of a website.
           
    Start by writing the URL of the website on the sidebar.
"""
)

if url:

    # 사용자가 URL 을 입력하면, 거기에 XML sitemap 이 포함되는지 확인할거다.
    # 포함되지 않다면 error 를 보여줘서 application 의 출돌을 미리 방지하자.
    if ".xml" not in url:
        with st.sidebar:
            st.error("Plaease write down a Sitemap URL")
    else:
        retriever = load_website(url)
        query = st.text_input("Ask a question to the website")

        # docs = retriever.invoke("What is the price of Claude3")
        # st.write(docs) # 확인용

        # Map Re-Rank Chain 만들기. 두개의 chain 이 필요하다
        # 1.첫번째 chain
        #   모든 개별 Document 에 대한 답변 생성 및 채점 담당
        # 2.두번째 chain
        #   모든 답변을 가진 마지막 시점에 실행된다
        #   점수가 제일 높고 + 가장 최신 정보를 담고 있는 답변들 고른다        

        # ----------
        # 🟡 첫번째 chain
        #    retreiver 에 의해 리턴된 List[Document] 와 사용자가 입력한 question 필요
        #    이는 chain 의 입력값들이다.
        if query:
            chain = {
                "docs": retriever,
                "question": RunnablePassthrough(),
            } | RunnableLambda(get_answers) | RunnableLambda(choose_answer)

            # 이 질문이 retriever 에게 전달될거다. => retriever.invoke('..')
            result = chain.invoke(query)
            st.markdown(result.content.replace("$", "\$"))
