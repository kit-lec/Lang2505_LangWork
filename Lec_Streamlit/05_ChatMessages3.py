import streamlit as st
import os
import time

print(f'✅ {os.path.basename(__file__)} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...')

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="👀",
)

st.title("ChatMessages 3")

# session_state 는 여러번 재실행해도 data 가 보존될수 있도록 해준다.
#   보존되는 데이터는 key-value 형태로 session에 저장됨

# 'messages' 라는 key 에 담아볼거다.


if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# st.write(st.session_state['messages']) # 확인용

message = st.chat_input(placeholder="Send a message to AI")

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    if save:    
        st.session_state['messages'].append({'message': message, 'role': role})
        

# 세션에 있는 chat 내용들 그리기 (chat 생성이 아니다.)
for msg in st.session_state['messages']:
    send_message(msg['message'], msg['role'], save=False)


if message:
    send_message(message, 'human') # chat 생성
    time.sleep(2)
    send_message(f'You said: {message}', 'ai') # chat 생성


















