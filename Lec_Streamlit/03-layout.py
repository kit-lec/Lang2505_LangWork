import streamlit as st
import os
import time

print(f'✅ {os.path.basename(__file__)} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...')

# layout
#  streamlit 에서 제공하는 다양한 레이아웃 
#  공식: https://docs.streamlit.io/develop/api-reference/layout  (◀ 함 보자!)

st.title('sidebar')

# 레이아웃 구성하는 두가지 방법

# 첫번째 방법
sbar = st.sidebar

sbar.title('sidebar title1')
sbar.text('hello')
sbar.text_input('이름입력')

st.sidebar.slider('나이')

# 두번째 방법 <- with 사용. 추천
with st.sidebar:
    st.title('sidebar title2')
    st.text_input('BBB')
    "HELLO EVERYONE"

# ---------------------------------------
# tab

tab_one, tab_two, tab_three = st.tabs(['One', 'Two', 'Three'])

with tab_one:
    st.write('Alpha')

with tab_two:
    st.write('Bravo')

with tab_three:
    st.write('Charlie')

st.markdown('---')
# ----------------------------------------------

st.title('columns')
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="달러USD", value="1,228 원", delta="-12.00 원")
with col2:
    st.metric(label="일본JPY(100엔)", value="958.63 원", delta="-7.44 원")
with col3: # 이방법 추천.
    st.metric(label="유럽연합EUR", value="1,335.82 원", delta="11.44 원")















