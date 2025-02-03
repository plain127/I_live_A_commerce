import uvicorn
import asyncio
import os
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, Form, BackgroundTasks, Body
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import FileResponse, JSONResponse
from live_streaming import main, channels
from live_stt import voice2text
from live_rag import insert_rag
from live_summarization import run_summary
from live_ner import ner_predict
from live_recommend import recommend
from live_llm import calling_llm
from live_tts import run_tts
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

category_map = {
    '뷰티' : 1,
    '푸드' : 2,
    '패션' : 3,
    '라이프' : 4,
    '여행/체험' : 5,
    '키즈' : 6,
    '테크' : 7,
    '취미레저' : 8,
    '문화생활' : 9 
}


#패시브 작동
#방송당 300초 주기로 업데이트    
def update(category_str, channel):

    category = category_map.get(category_str, 0)
    channel_num = channel
    
    voice2text(category, channel_num) 
    
    summ = run_summary(category, channel_num)
    topic = ner_predict(summ)
    recommend(category, channel_num, topic, topic)
    insert_rag(category, channel_num)

#AI 업데이트 함수
async def sync_db(scheduler):
    exisiting_jobs = set()
    
    while True:
        current_jobs = {(ch['Category'], ch['Channel']) for ch in channels}
        
        new_jobs = current_jobs - exisiting_jobs
        for category, channel in new_jobs:
            job_id = f'{category}_{channel}'
            scheduler.add_job(
                update,
                'interval', 
                seconds = 93, 
                args = [category, channel],
                id = job_id
            )

        removed_jobs = exisiting_jobs - current_jobs
        for category, channel in removed_jobs:
            job_id = f'{category}_{channel}'
            scheduler.remove_job(job_id)
            
        exisiting_jobs = current_jobs
        
        await asyncio.sleep(5)


#시작부터 계속 돌아가는 패시브 함수
@asynccontextmanager
async def stream(app:FastAPI):
    asyncio.create_task(main()) #크롤링 함수
    
    #일정 주기마다 돌아갈 수 있도록 만듦
    scheduler = BackgroundScheduler()
    scheduler.start()
    
    asyncio.create_task(sync_db(scheduler)) #AI Update 함수
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=stream)

# CORS 설정: React 앱에서 FastAPI 서버에 접근 가능하도록 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React 앱의 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/home')
async def home():
    return JSONResponse(content=channels)

@app.post('/sentiment')
async def sentiment(request:dict=Body(...)):
    category_str = request.get('Category')
    category = category_map.get(category_str, 0)
    channel_num = request.get('Channel')
    
    if not os.path.exists('DB/sentiment_scores.csv'):
        return {"score":None}
    
    df = pd.read_csv('DB/sentiment_scores.csv')
    sentiment_score = df.loc[
        (df['category']==category) & (df['channel']==int(channel_num))
    ]
    if sentiment_score.empty:
        return {"score":None}
    return sentiment_score.to_dict(orient='records')

@app.post('/chat')
async def chat(request:dict=Body(...)):
    
    category_str = request.get('Category')
    category = category_map.get(category_str, 0)
    channel_num = request.get('Channel')
    
    input_txt = request.get('Text')
    output_txt = calling_llm(category, channel_num, input_txt)
    
    voice = request.get('Voice')
    who = request.get('Who')
    
    if voice == True:
        voice_complete = run_tts(category, channel_num, who, output_txt)
        if voice_complete:
            voice_path = f'DB/{category}_{channel_num}/voice.wav'
            return JSONResponse(content={'Text':output_txt, 'Voice': voice_path})

    return JSONResponse(content={'Text':output_txt, 'Voice':'/'})

# 정적 파일 제공: /streaming 경로에서 DB 디렉토리를 정적으로 제공
app.mount("/streaming", StaticFiles(directory="DB"), name="streaming")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=1700)  