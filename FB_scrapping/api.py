'''
Make sure to run this server on port 8090 or
change the url path on the background.js script
'''
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Union
import string

from utils.predictor import load_models,predict_personality, translate_back


class Big(BaseModel):
    text: str

class Item(BaseModel):
    Name: str  # Name of the user
    Age: int   # User age
    Gender: str
    Data: dict # The dict data formed by analysing the user profile
    Post: int  # Number of self posts
    Repost: int  # Number of reposts
    Feed: int  # Number of posts on profile feed
    Image: int  # Number of posts having an image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def welcome_user(user: str = "user"):
    return {"message": f"Hello, {user}!"}

@app.post("/api")
async def root(body: Big):
    body = body.dict()
    recieved = body["text"]
    Text = recieved  # This is the post text received
    print(Text)  # You should see the post in your terminal

    # Process and predict
    temp = []
    predictions = predict_personality(Text)
    for personality, result in predictions.items():
        print(f"Personality Type: {personality}")
        print(f"Prediction: {(result['prediction'])}")
        temp.append(result['prediction'])
        print(f"Probability: {result['probability']:.2f}")
        print()

    print(translate_back(temp))
    result = "openness"  # Dummy return; replace with actual result if necessary
    return {"data": result}


def set_up():
    # Get the directory of the current file (api.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Change the working directory to the current directory
    os.chdir(current_dir)
    result=load_models()
    if result:
        print()
        print('--------------------------------------------')
        print("Models loaded successfully")
        print('--------------------------------------------')
    else:
        print()
        print('--------------------------------------------')
        print("There was some error in loading models!")
        print('--------------------------------------------')
        exit()


@app.on_event("startup")
async def startup_event():
    set_up()

if __name__ == '__main__':
    uvicorn.run("api:app", port=8090, reload=True)

