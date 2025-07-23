import os
from dotenv import load_dotenv

print(f'✅ {os.path.basename( __file__ )} 실행됨')
load_dotenv()  #
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}')
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st

# Chromium 의 headless instance 를 사용하여 HTML 페이지를 스크레이핑
from langchain_community.document_loaders.chromium import AsyncChromiumLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer

import asyncio

# Windows 환경에서의 event loop policy 설정
if hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

html2text_transformer = Html2TextTransformer()

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
    loader = AsyncChromiumLoader(
        urls=[url],
        user_agent='Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    )

    # TODO
