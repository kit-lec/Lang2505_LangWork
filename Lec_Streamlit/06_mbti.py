import streamlit as st
import os
import time

print(f'✅ {os.path.basename(__file__)} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')
api_key = os.getenv("CLOVASTUDIO_TEST_API_KEY")
print(f'\tCLOVASTUDIO_TEST_API_KEY={os.getenv("CLOVASTUDIO_TEST_API_KEY")[:20]}...')

# -*- coding: utf-8 -*-

import requests
import json

class CompletionExecutor:
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        with requests.post(self._host + '/testapp/v3/chat-completions/HCX-005',
                           headers=headers, json=completion_request, stream=True) as r:
            # 응답은 id > event > data > id > event > data > id > event > data > ..

            event_type = ""
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print('🧡', decoded_line)

                    if decoded_line.startswith('event'):
                        event_type = decoded_line.split(":")[1]
                    elif event_type.startswith('result') and decoded_line.startswith('data'):
                        result_answer = json.loads(decoded_line[len('data:'):])['message']['content']

        return result_answer                        


st.title("MBTI 대백과 사전")
question = st.text_input(
    '질문',
    placeholder='질문을 입력해 주세요',
)

if question:
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=f'Bearer {api_key}',
        request_id='0a49825bb1914b599a96083ed76ecd50'
    )

    preset_text = [
        {"role":"system","content":"- MBTI에 대한 지식을 기반으로, MBTI 질문에 답해보세요.\n- 예제의 형식을 참고하여 질문에 대한 답을 간단히 하세요.\n\n질문: ESFJ는 문제에 봉착했을때 어떻게 대응하는가?\n답: 현실적인 해결 방법을 찾기 위해 노력합니다.\n###\n질문: ISFJ는 연인에게 어떻게 대하는 편인가?\n답: 섬세하고 다정하게 케어해주는 편입니다.\n####\n질문: INTP는 사람들이 많은 곳에 가면 어떻게 행동하는가?\n답: 주변의 상황을 파악하기 위해 관찰하는 편입니다.\n###\n질문: ESFJ는 충동적인 선택을 많이 하는 편인가?\n답: 아니다. 계획적으로 움직이는 편입니다."},{"role":"user","content":"ESTP는 학업에 어떤 자세로 임하는가?"},{"role":"user","content":"ESTP 는 학업에 어떤 자세로 임하는가?"},{"role":"assistant","content":"ESTP 유형은 실용적이고 현실적인 방식으로 학업에 접근하며 다음과 같은 특징이 있습니다:\n\n1. **실험적 학습**: 이론보다는 실제 경험을 통해 배우는 것을 선호하므로 실험이나 실습을 좋아합니다.\n2. **문제 해결 중심**: 학문적 지식 자체보다 문제를 해결하는 데 필요한 정보를 습득하는 것에 집중합니다.\n3. **즉각적인 피드백 필요**: 자신의 이해도를 확인하기 위해 즉각적인 피드백을 원할 수 있습니다.\n4. **활동적인 참여**: 수업 시간에 적극적으로 질문하거나 토론에 참여하는 경향이 있습니다.\n5. **유연한 시간 관리**: 시간표에 따라 엄격하게 공부하기보다는 유동적으로 시간을 관리하는 경우가 많습니다.\n\nESTP들은 구조화된 학습 환경보다는 자율성과 유연성을 중시하며, 실질적인 응용과 경험을 통해 더 잘 배울 수 있다는 점을 기억해야 합니다."},{"role":"user","content":"ENFP 성격은 어떻게 되나요?\n"},{"role":"assistant","content":"ENFP의 성격 특성은 다음과 같습니다.\n\n1. **창의적이고 호기심이 많음**: 새로운 아이디어와 가능성에 열려 있으며, 다양한 관심사를 가지고 있습니다.\n2. **열정적이며 이상주의자임**: 자신이 믿는 일에 대해 깊은 열정을 보이며, 세상을 더 나은 곳으로 만들고자 합니다.\n3. **감정이 풍부하고 직관적임**: 타인의 감정을 쉽게 이해하고 공감하며, 감정 표현에 솔직합니다.\n4. **융통성 있고 즉흥적임**: 계획을 세우기보다는 상황에 맞춰 유연하게 대처하며, 즉흥적인 활동을 즐깁니다.\n5. **사교적이고 협력적임**: 다른 사람들과 쉽게 어울리며 팀워크를 중요시합니다.\n\nENFP는 종종 창의적이고 열정적인 사람으로 인식되며, 그들의 독특한 관점과 감수성으로 주변 사람들에게 긍정적인 영향을 미칩니다. 그러나 때로는 과도한 활동이나 산만함으로 인해 어려움을 겪기도 합니다. 이러한 특성을 고려하여 ENFP와의 관계를 구축하거나 협업할 때 이를 염두에 두면 좋습니다."}
        , {
            'role': 'user',
            'content': f'{question}'
        }
        ]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 512,
        'temperature': 0.5,
        'repetitionPenalty': 1.1,
        'stop': ['###'],
        'includeAiFilters': True,
        'seed': 0
    }

    print('🌐', preset_text)
    result_text = completion_executor.execute(request_data)
    st.markdown(result_text)


