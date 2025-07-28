import os
from dotenv import load_dotenv

print(f'✅ {os.path.basename( __file__ )} 실행됨')
load_dotenv()  #
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}')
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st
from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

# document 전체 HTML 을 가진 Beautiful soup object 값이 전달된다
# 여기서 검색(search) 하거나, HTML element 들을 제거할수 있다.
def parse_page(soup):
    header = soup.find("header")  # <header> 요소 리턴
    footer = soup.find('footer')  # <footer> 요소 리턴

    if header:
        header.decompose()  # header 를 HTML 에서 제거

    if footer:
        footer.decompose()  # footer 를 HTML 에서 제거
    
    # header 와 footer 가 제거된 나머지 text 만 리턴
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
        # data 를 load 하고 싶은 url 들을 담을 list. url 은 정규표현식으로 인식된다.        
        filter_urls=[
            # "https://www.anthropic.com/news/anthropic-raises-series-e-at-usd61-5b-post-money-valuation",

            # 정규표현식 사용
            # .*  ← 전 후에 다른 문자들이 올수는 있지만
            #  /news/ 를 포함하는 url 만 볼수 있다.
            r"^(.*\/news\/).*",  
            
            # ?! ← negative lookahead   /news/ 롤 포함하지 않은 url만 통과
            # r"^(?!.*\/news\/).*",              
        ],

        parsing_function=parse_page,
    )
    loader.max_depth = 1  # 수업시간 한계상 depth=1  (기본값 10)
    loader.requests_per_second = 1
    loader.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}

    docs = loader.load_and_split(text_splitter=splitter) 
    return docs

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
        docs = load_website(url)
        st.write(docs) # 확인용