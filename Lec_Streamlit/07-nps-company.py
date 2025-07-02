# 회사명을 입력하면 회사의 기초정보와 
# 회사 직원들의 월 평균급여, 추정연봉, 
# 동일 업종내 비교, 연봉의 차이

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import platform
import seaborn as sns
import re
import streamlit as st

# 한글폰트 설정
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
matplotlib.rcParams['axes.unicode_minus'] = False 

class PensionData():
    # 생성자: 데이터파일 읽어온후 전처리 수행
    def __init__(self, filepath):
        warnings.simplefilter(action='ignore', category=pd.errors.DtypeWarning)
        self.df = pd.read_csv(os.path.join(filepath), encoding='cp949')
        self.pattern1 = r'(\([^)]+\))'
        self.pattern2 = r'(\[[^)]+\])'
        self.pattern3 = r'[^A-Za-z0-9가-힣]'
        self.preprocess()  
          
    # 전처리   
    def preprocess(self):

        # '사업장업종코드' 컬럼값이 빈 문자열인것들은 제거한다.
        mask = self.df['사업장업종코드'].replace({r'^\s+$': pd.NA}, regex=True).isna()
        self.df = self.df[~mask]
        self.df['사업장업종코드'] = self.df['사업장업종코드'].astype('int32')

        # 컬럼명들을 재정의
        self.df.columns = [
            '자료생성년월', '사업장명', '사업자등록번호', '가입상태', '우편번호',
            '사업장지번상세주소', '주소', '고객법정동주소코드', '고객행정동주소코드', 
            '시도코드', '시군구코드', '읍면동코드', 
            '사업장형태구분코드 1 법인 2 개인', '업종코드', '업종코드명', 
            '적용일자', '재등록일자', '탈퇴일자',
            '가입자수', '금액', '신규', '상실'
        ]
        # 불필요한 컬럼 제거
        df = self.df.drop(['자료생성년월', '우편번호', '사업장지번상세주소', '고객법정동주소코드', '고객행정동주소코드', '사업장형태구분코드 1 법인 2 개인', '적용일자', '재등록일자'], axis=1)
        # 사업장명 cleasing
        df['사업장명'] = df['사업장명'].apply(self.preprocessing)
        # '탈퇴일자_연도', '탈퇴일자_월' 컬럼 추가
        df['탈퇴일자_연도'] =  pd.to_datetime(df['탈퇴일자']).dt.year
        df['탈퇴일자_월'] =  pd.to_datetime(df['탈퇴일자']).dt.month
        # '주소' 컬럼에서 '시도' 부분만 새 컬럼으로 추가
        df['시도'] = df['주소'].str.split(' ').str[0]

        # 탈퇴한 기업들은 drop
        df = df.loc[df['가입상태'] == 1].drop(['가입상태', '탈퇴일자'], axis=1).reset_index(drop=True)

        # 분석하고자 하는 컬럼들 추가
        df['인당금액'] = df['금액'] / df['가입자수']
        df['월급여추정'] =  df['인당금액'] / 9 * 100
        df['연간급여추정'] = df['월급여추정'] * 12
        
        self.df = df  # 원본 변경하기

        
    # 사업장명 정제를 위한 함수    
    def preprocessing(self, x):
        # 특수 문자들 제거.   "(주)", "[주]" ...
        x = re.sub(self.pattern1, '', x)
        x = re.sub(self.pattern2, '', x)
        x = re.sub(self.pattern3, ' ', x)
        x = re.sub(' +', ' ', x)
        return x
    
    # 주어진 'company_name' 으로 기업 검색
    def find_company(self, company_name):
        # 가입자수가 많은 순으로 정렬하여 리턴
        return self.df.loc[self.df['사업장명'].str.contains(company_name), ['사업장명', '월급여추정', '연간급여추정', '업종코드', '가입자수']]\
                  .sort_values('가입자수', ascending=False)
    
    # 주어진 'company_name' 으로 
    # 동종업계 정보 (월급여 추정액, 연간급여추정액 ) 비교 
    def compare_company(self, company_name):
        company = self.find_company(company_name)
        code = company['업종코드'].iloc[0]
        df1 = self.df.loc[self.df['업종코드'] == code, ['월급여추정', '연간급여추정']].agg(['mean', 'count', 'min', 'max'])
        df1.columns = ['업종_월급여추정', '업종_연간급여추정']
        df1 = df1.T
        df1.columns = ['평균', '개수', '최소', '최대']
        df1.loc['업종_월급여추정', company_name] = company['월급여추정'].values[0]
        df1.loc['업종_연간급여추정', company_name] = company['연간급여추정'].values[0]
        return df1

    # 검색 기업 정보 출력 
    def company_info(self, company_name):
        company = self.find_company(company_name)
        return self.df.loc[company.iloc[0].name]
                
    def get_data(self):
        return self.df    
    

file_path = r'https://www.dropbox.com/scl/fi/2v4676nsnjf3tx0jrkq26/nlp_company_20250123.csv?rlkey=m78skae6r03yd4g6xu1lopdo6&st=o3jmgbqj&dl=1'    


@st.cache_resource
def read_pensiondata():
    data = PensionData(file_path)
    return data

data = read_pensiondata() # 처음 실행할때는 호출되겠지만,  두번째부터는 cache 된 결과로 리턴된다.
                            # 단 호출시 매개변수가 다르면 호출된다. 

company_name = st.text_input('회사명을 입력해 주세요', placeholder='검색할 회사명 입력')


if data and company_name:
    output = data.find_company(company_name=company_name)

    if len(output) > 0:
        st.subheader(output.iloc[0]['사업장명'])

        # 사업장 정보 출력
        info = data.company_info(company_name=company_name)
        st.markdown(
            f"""
            - `{info['주소']}`
            - 업종코드명 `{info['업종코드명']}`
            - 총 근무자 `{int(info['가입자수']):,}` 명
            - 신규 입사자 `{info['신규']:,}` 명
            - 퇴사자 `{info['상실']:,}` 명
            """
        )        
        col1, col2, col3 = st.columns(3)
        col1.text('월급여 추정')
        col1.markdown(f"`{int(output.iloc[0]['월급여추정']):,}` 원")

        col2.text('연봉 추정')
        col2.markdown(f"`{int(output.iloc[0]['연간급여추정']):,}` 원")

        col3.text('가입자수 추정')
        col3.markdown(f"`{int(output.iloc[0]['가입자수']):,}` 명")  

        # 🟥find_company() 로 사용자가 입력한 검색어로 검색한 결과들을 전부 출력.
        st.dataframe(output.round(0), use_container_width=True)

        # compare_company()
        #  업종평균 vs. 검색기업 
        #  비교 결과 출력 
        comp_output = data.compare_company(company_name=company_name)
        st.dataframe(comp_output.round(0), use_container_width=True)

        st.markdown(f'### 업종 평균 VS {company_name} 비교')
        # 검색은 회사의 '월급여추정'액과 업종평균을 비교
        percent_value = info['월급여추정'] / comp_output.iloc[0, 0] * 100 - 100
        diff_month = abs(comp_output.iloc[0, 0] - info['월급여추정'])  # 월급여추정 액의 차이
        diff_year = abs(comp_output.iloc[1, 0] - info['연간급여추정'])  # 연간급여추정 액의 차이
        upordown = '높은' if percent_value > 0 else '낮은'  # %값이 높은지 낮은지에 따른 문구 선택 
        # 위 결과로 아래에 markdown 으로 출력
        st.markdown(f"""
        - 업종 **평균 월급여**는 `{int(comp_output.iloc[0, 0]):,}` 원, **평균 연봉**은 `{int(comp_output.iloc[1, 0]):,}` 원 입니다.
        - `{company_name}`는 평균 보다 `{int(diff_month):,}` 원, :red[약 {percent_value:.2f} %] `{upordown}` `{int(info['월급여추정']):,}` 원을 **월 평균 급여**를 받는 것으로 추정합니다.
        - `{company_name}`는 평균 보다 `{int(diff_year):,}` 원 `{upordown}` `{int(info['연간급여추정']):,}` 원을 **연봉**을 받는 것으로 추정합니다.
        """)

        #  ----------------------------------
        #  🟥비교표를 시각화
        fig, ax = plt.subplots(1, 2)

        p1 = ax[0].bar(x=["Average", "Your Company"], height=(comp_output.iloc[0, 0], info['월급여추정']), width=0.7)
        ax[0].bar_label(p1, fmt='%d')
        p1[0].set_color('black')
        p1[1].set_color('red')
        ax[0].set_title('Monthly Salary')

        p2 = ax[1].bar(x=["Average", "Your Company"], height=(comp_output.iloc[1, 0], info['연간급여추정']), width=0.7)
        p2[0].set_color('black')
        p2[1].set_color('red')
        ax[1].bar_label(p2, fmt='%d')
        ax[1].set_title('Yearly Salary')

        ax[0].tick_params(axis='both', which='major', labelsize=8, rotation=0)
        ax[0].tick_params(axis='both', which='minor', labelsize=6)
        ax[1].tick_params(axis='both', which='major', labelsize=8)
        ax[1].tick_params(axis='both', which='minor', labelsize=6)

        st.pyplot(fig)

        #  ----------------------------------
        #  🟥동종업계 (회사 업종코드와 일치하는 것들) 검색애서 '연간급여추정'액 내림차순으로 보여주기
        st.markdown('### 동종업계')
        df = data.get_data()
        st.dataframe(df.loc[df['업종코드'] == info['업종코드'], ['사업장명', '월급여추정', '연간급여추정', '가입자수']]\
            .sort_values('연간급여추정', ascending=False).head(10).round(0), 
            use_container_width=True
        )

    else:
        st.subheader('검색결과가 없습니다')



