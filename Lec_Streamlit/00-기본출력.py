import streamlit as st
import numpy as np
import pandas as pd

import os
import time

print(f'✅ {os.path.basename(__file__)} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...')

# 서버 실행
# > streamlit run ******.py
#    ※ 초반에 email 물어보면 걍 엔터 치세요.

# 서버 종료
# 터미널창에서 user break (CTRL + C) 연타
# user break 되지 않으면 terminal 종료(kill) 하세요

# 기본적인 widget(ui)
st.title('Widget, UI')

# 특수 이모티콘 삽입 예시
# emoji: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.title('스마일 :sunglasses:')

# Header
st.header('헤더를 입력할수 있습니다! :sparkles:')

# subheader
st.subheader('이것은 subheader 입니다')

# 캡션
st.caption('캡셥을 넣어봅니다')

# 코드 표시
sample_code = '''
def function():
    print('hello, streamlit')
'''
st.code(sample_code, language='python')

# 일반 텍스트
st.text('일반적인 텍스트 입니다')

# 마크다운 
st.markdown('streamlit 은 **마크다운 문법을 지원** 합니다')

# 컬러코드: blue, green, orange, red, violet
st.markdown("텍스트의 색상을 :green[초록색]으로, 그리고 **:blue[파란색]** 볼트체로 설정할 수 있습니다.")
st.markdown(r":green[$\sqrt{x^2+y^2}=1$] 와 같이 latex 문법의 수식 표현도 가능합니다 :pencil:")

# LaTex 지원
st.latex(r'\sqrt{x^2+y^2}=1')

# <hr> 가로선 
st.markdown("---")

st.title("DataFrame, Metric")

# DataFrame 생성
df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

# DataFrame
st.dataframe(df, use_container_width=True)

# 테이블
# DataFrame 과는 다르게 interactive 한 UI 제공 안함.
st.table(df)

# 메트릭
st.metric(label='온도', value="10°C", delta="1.2°C")
st.metric(label='삼성전자', value="61,000 원", delta="-1,200원")

st.markdown('---')

#--------------------------------------------------------
st.title("write()")

st.write('hello')
st.write([1, 2, 3, 4])
st.write({"x":100, "y":200})

# 클래스도 출력
import re

st.write(re.Pattern)

# Streamlit 의 magic
re.Match

a = [1, 2, 3, 4]
d = {'x': 1}

a
d

# Chart elements
#  그래프, 차트 그리기
#  https://docs.streamlit.io/develop/api-reference/charts

st.markdown('---')

import matplotlib.pyplot as plt
import seaborn as sns

# 한글폰트 설정
from matplotlib import font_manager, rc
import platform
try : 
    if platform.system() == 'Windows':
    # 윈도우인 경우
        font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
        rc('font', family=font_name)
    else:    
    # Mac 인 경우
        rc('font', family='AppleGothic')
except : 
    pass
plt.rcParams['axes.unicode_minus'] = False   



st.title('Chart 그리기')

data = pd.DataFrame({
    '이름': ['영식', '철수', '영희'],
    '나이': [22, 31, 25],
    '몸무게': [75.5, 80.2, 55.1]
})

st.dataframe(data, use_container_width=True)


fig, ax = plt.subplots()
ax.bar(data['이름'], data['나이'])
st.pyplot(fig)

barplot = sns.barplot(x='이름', y='나이', hue='이름', data=data, 
                      ax=ax, palette='Set2', legend=False)
fig = barplot.get_figure()

st.pyplot(fig)


























