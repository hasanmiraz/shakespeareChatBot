from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from shakespeareChatBotAI.source.main import user_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return {"I am shake speare"}

@app.get("/chatbot/{chatbotquery}")
async def read_item(chatbotquery: str):
    input_data = chatbotquery
    answer = user_query(input_data)
    return {
        "query": input_data,
        "response": answer
    }
