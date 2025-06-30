import streamlit as st
import os
import time

print(f'✅ {os.path.basename(__file__)} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...')

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="👀",
)

st.title("Document GPT1")

with st.chat_message(name='human'):
    st.write('Helloo!')

with st.chat_message(name='ai'):
    st.write('How are you!')

st.chat_input(placeholder="Send a message to AI")

with st.status("Embedding file...", expanded=True) as status:
    time.sleep(3)
    st.write("Getting the file")
    time.sleep(3)
    st.write("Embedding the file")
    time.sleep(3)
    st.write("Caching the file")
    # update
    status.update(label='Error', state='error')