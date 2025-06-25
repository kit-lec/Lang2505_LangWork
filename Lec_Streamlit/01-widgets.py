import streamlit as st
import numpy as np
import pandas as pd

import os
import time

print(f'✅ {os.path.basename(__file__)} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...')

# Streamlit 의 data flow 와 data 가 처리되는 방식

# Streamlit 에선 'data 가 변경'될때 마다 python 파일 '전체'가 다시 실행된다. (py 파일 위에서부터 아래까지 전부 다시 실행)
# 가령 사용자가 무언가를 입력하거나 slider 를 드래그 해서 data 가 변경될때마다 ..

st.title(time.strftime('%Y-%m-%d %H:%M:%S'))

# 다양한 입력 widgets 들
#    https://docs.streamlit.io/develop/api-reference/widgets


model = st.selectbox("Choose Your model", ("GPT-3", "GPT-4"))
st.markdown(f'model: :green[{model}]')

name = st.text_input("What is your name?")
st.markdown(f'name: :green[{name}]')

# 입력할때마다 화면이 rerun 된다.
#  이는 reload 와는 다르다!

value = st.slider(label='temperature', min_value=0.1, max_value=1.0)
st.markdown(f'value: :green[{value}]')


# 특정 입력값에 따라 '보여지거나/보여지지 않거나' 를 지정해줄수 있다
if model == 'GPT-3':
    st.write('cheap')
else:
    st.write('expensive')

if model == 'GPT-3':
    st.write('값싼 모델')
else:
    st.write('비싼 모델')
    country = st.text_input("What is your country?")
    st.write(country)

# 버튼
button = st.button("버튼을 눌러보세요") # -> bool 리턴ㄴ

if button:
    st.write(':blue[버튼]이 눌렸습니다. :sparkle:')


df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

st.download_button(
    label="CSV로 다운로드",
    data=df.to_csv(),
    file_name='sample.csv',
    mime='text/csv',
)

agree = st.checkbox('동의 하십니까?') # -> bool 리턴
if agree:
    st.write('동의 해주셔서 감사합니다 :100:')

mbti = st.radio(
    label="당신의 MBTI 는 무엇입니까?",
    options=('ISTJ', 'ENFP', '선택지 없슴')
)

st.write({
    'ISTJ': '당신은 :blue[현실주의자] 입니다',
    'ENFP': '당신은 :green[활동가] 입니다',
    '선택지 없슴': '당신에 대해 :red[알고 싶어요]:grey_exclamation:'
}[mbti])


mbti = st.selectbox(
    label="당신의 MBTI 는 무엇입니까?",
    options=('ISTJ', 'ENFP', '선택지 없슴'),
    index=1 
)

st.write({
    'ISTJ': '당신은 :blue[현실주의자] 입니다',
    'ENFP': '당신은 :green[활동가] 입니다',
    '선택지 없슴': '당신에 대해 :red[알고 싶어요]:grey_exclamation:'
}[mbti])


