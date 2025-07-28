import os
from dotenv import load_dotenv

print(f'✅ {os.path.basename( __file__ )} 실행됨')
load_dotenv()  #
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}')
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st
from langchain_community.document_loaders.sitemap import SitemapLoader


@st.cache_resource(show_spinner="Fetching URL...")
def load_website(url):
    loader = SitemapLoader(url)
    loader.max_depth = 1  # 수업시간 한계상 depth=1  (기본값 10)
    loader.requests_per_second = 1
    loader.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36'}

    docs = loader.load()    
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