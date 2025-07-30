import os, time
from dotenv import load_dotenv

load_dotenv()  #

print(f'✅ {os.path.basename( __file__ )} 실행됨 {time.strftime('%Y-%m-%d %H:%M:%S')}')  # 실행파일명, 현재시간출력
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st
import glob

from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser

from langchain_community.vectorstores.faiss import FAISS
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain.storage.file_system import LocalFileStore

import subprocess
import math
from pydub import AudioSegment
import glob
import openai

# ────────────────────────────────────────
# 🎃 LLM 로직
# ────────────────────────────────────────
llm = ChatOpenAI(
    temperature=0.1,
)



# ────────────────────────────────────────
# 🍇 file load & cache
# ────────────────────────────────────────
file_dir = os.path.dirname(os.path.realpath(__file__)) # *.py 파일의 '경로'만
# .cache  ← 업로드한 비디오 와 변환한 mp3
# .cache/chunks ← 분할된 mp3 파일들 저장
upload_dir = os.path.join(file_dir, '.cache/chunks')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

embedding_dir = os.path.join(file_dir, r'./.cache/embeddings')
if not os.path.exists(embedding_dir):
    os.makedirs(embedding_dir)    

# 🐕‍🦺학습용: transcript 한번했으면 중복해서 실행하지 않기
has_transcript = os.path.exists(os.path.join(file_dir, r'.cache/podcast.txt'))    


# 오디오 추출함수
# 업로드한 video(mp4)에서 오디오(mp3) 추출하여 동일 경로에 저장.
@st.cache_resource()
def extract_audio_from_video(video_path):    
    if has_transcript: return   # 🐕‍🦺학습용
    audio_path = video_path.replace("mp4", "mp3")  
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vn",
        audio_path,
        "-y",  # -y 옵션이 있어야 yes / no 물어볼시 yes 자동선택하고 넘어가게 된다.
        ]
    subprocess.run(command)    

# audio_path : 원본 오디오 경로
# chunk_size : minute
# chunks_folder: chunk 들을 저장할 폴더
@st.cache_resource()
def cut_audio_in_chunks(audio_path, chunk_size, chunks_folder):
    if has_transcript: return   # 🐕‍🦺학습용
    track = AudioSegment.from_mp3(audio_path)
    chunk_len = chunk_size * 60 * 1000
    chunks = math.ceil(len(track) / chunk_len)
    for i in range(chunks):
        start_time = i * chunk_len
        end_time = (i + 1) * chunk_len

        chunk = track[start_time:end_time]

        exp_path = os.path.join(chunks_folder, f"chunk_{i}.mp3")
        chunk.export(exp_path, format="mp3")


# chunk_folder :
# destination : 녹취록이 들어간 텍스트 파일이 저장될 디렉토리
@st.cache_resource()
def transcribe_chunks(chunk_folder, destination):
    if has_transcript: return   # 🐕‍🦺학습용
    files = glob.glob(os.path.join(chunk_folder, "chunk*.mp3"))
    files.sort()
    for file in files:
        with open(file, "rb") as audio_file, open(destination, "a") as text_file:# append mode
            print(file, '녹취록 가져오는중...', end='')
            # 각 chunk 별로 녹취록 작성.
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
           
            text_file.write(transcript.text) # 곧바로 텍스트 파일에 저장

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=800,
    chunk_overlap=100,
)

# podcast.txt 를 embed 해야 한다.
@st.cache_resource(show_spinner="Embedding file...")
def embed_file(file_path):
    cache_dir = LocalFileStore(os.path.join(embedding_dir))  

    loader = TextLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)

    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

    vectorstore = FAISS.from_documents(docs, cached_embeddings)

    retriever = vectorstore.as_retriever()
    return retriever

# ────────────────────────────────────────
# ⭕ Streamlit 로직
# ────────────────────────────────────────
st.set_page_config(
    page_title="MeetingGPT",
    page_icon="🎤",
)
st.markdown(
    """
# MeetingGPT
            
Welcome to MeetingGPT, upload a video and I will give you a transcript, a summary and a chat bot to ask any questions about it.

Get started by uploading a video file in the sidebar.
"""
)

with st.sidebar:
    video = st.file_uploader(
        label="Video",
        type=["mp4", "avi", "mkv", "mov"],
    )

if video:
    with st.status("Loading video...") as status:
        video_content = video.read()
        video_path = os.path.join(file_dir, rf'.cache/{video.name}')
        audio_path = video_path.replace("mp4", "mp3")
        with open(video_path, 'wb') as f:
            f.write(video_content)

        status.update(label="Extracting audio...")
        extract_audio_from_video(video_path)

        chunks_folder = os.path.join(file_dir, r'./.cache/chunks')
    
        status.update(label="Cutting audio segments...")
        cut_audio_in_chunks(audio_path, 10, chunks_folder)  # chunk_size 10분

        transcript_path = video_path.replace("mp4", "txt")
        status.update(label="Transcripting Audio..")
        transcribe_chunks(chunks_folder, transcript_path)

    # 3개의 tab
    transcript_tab, summary_tab, qa_tab = st.tabs(["Transcript", "Summary", "Q&A"])

    with transcript_tab:
        with open(transcript_path, 'r') as file:
            st.write(file.read())    


    with summary_tab:
        start = st.button("Generate summary")

        # ↓ 2개의 chain 을 시작
        #  첫번째 chain : 첫번째 document 를 요약 (summarize)
        #  두번째 chain : 다른 모든 document 를 요약
        #      LLM 에게 '이전의 summary' 와 새 context 를 사용하여 새로운 summary 를 만들게 함 (refine!).

        if start:
            loader = TextLoader(transcript_path)

            docs = loader.load_and_split(text_splitter=splitter)
            # st.write(len(docs)) # 확인용
            # st.write(docs) # 확인용

            # 🟢첫번째 chain: 첫번째 Document 요약            
            first_summary_prompt = ChatPromptTemplate.from_template(
                # 정확한 요약 (concise summary) 를 위한 프롬프트
                """
                Write a concise summary of the following:
                "{text}"
                CONCISE SUMMARY:                
            """
            )

            first_summary_chain = first_summary_prompt | llm | StrOutputParser()

            summary = first_summary_chain.invoke({"text": docs[0].page_content})

            # st.write(summary) # 확인용


            # 🟢나머지 Document 들을 요약할 chain
            refine_prompt = ChatPromptTemplate.from_template(
                """
                Your job is to produce a final summary.
                We have provided an existing summary up to a certain point: {existing_summary}
                We have the opportunity to refine the existing summary (only if needed) with some more context below.
                ------------
                {context}
                ------------
                Please refine the existing summary using the additional context, if necessary.
                If the additional context does not require any changes to the existing summary, **return the existing summary exactly as it is.**
                Do NOT explain your decision. Just output the final summary.
                """
            )

            refine_chain = refine_prompt | llm | StrOutputParser()

            # 나머지 모든 Document(들) 에 대해 
            with st.status("Summarizing...") as status:
                for i, doc in enumerate(docs[1:]):
                    status.update(label=f"Processing document {i+1}/{len(docs)-1} ")

                    # 기존의 summary 를 새로운 응답으로 덮어쓰기 (refine!)
                    summary = refine_chain.invoke({
                        "existing_summary": summary,   # 이전 summary 와 
                        "context": doc.page_content,   # 다음 Document 를 사용
                    })

                    st.write("🔷 ", summary)  # 중간단계 누적 확인

            st.write("✅ ", summary) # 최종 요약

    with qa_tab:
        retriever = embed_file(transcript_path)
        docs = retriever.invoke("Do they talk about marcus aurelius?")
        st.write(docs)











