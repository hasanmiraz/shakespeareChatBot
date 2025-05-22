from fastapi import FastAPI
import time

app = FastAPI()

@app.get('/')
async def root():
    return {"I am shake speare"}

@app.get("/chatbot/{chatbotquery}")
async def read_item(chatbotquery: str):
    # send data to the model
    input_data = chatbotquery
    time.sleep(5) # simulate delay
    output_data = f"shake_speare_says: {chatbotquery}"
    
    return {
        "query" : input_data, 
        "response": output_data
    }