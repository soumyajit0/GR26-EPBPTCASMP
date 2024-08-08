'''
Make sure to run this server on port 8090 or
change the url path on the background.js script
'''

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Union
import string


class Big(BaseModel):
    text: str


class Item(BaseModel):
    Name:str    #Name of the user
    Age:int     #user age
    Gender:str  
    Data:dict   #the dict data formed by analysing the user profile
    Post:int    #no of self posts
    Repost:int  #no of reposts
    Feed:int    #no of posts on profile feed
    Image:int   #no of posts having an image

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

        
#This route is unused currently
@app.get("/")
async def welcome_user(user: str = "user"):
    return {"message": f"Hello, {user}!"}


#This is the route where calls from the frontend is recieved if it is asking for prediction
#the data recieved is a json object like {"text":"the text to analyse"}
@app.post("/api")
async def root(
    body: Big
):
    body = body.dict()
    # Use the preprocess_and_predict function from predictor.py
    recieved = body["text"]
    Text= recieved      # This is the post text received
    print(Text)         # you should see the post in your terminal
    
    # TODO call your own process_and_predict function
    #result = preprocess_and_predict(Text)      # < -- This preprocess_and_predict needs a string as parameter
    
    # print(result)
    
    #The below is a dummy return 
    # once processed return your own result instead
    result= "openness"
    return {"data":result}

'''
Make sure to run this server on port 8090 or
change the url path on the background.js script
'''

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Union
import string


class Big(BaseModel):
    text: str


class Item(BaseModel):
    Name:str    #Name of the user
    Age:int     #user age
    Gender:str  
    Data:dict   #the dict data formed by analysing the user profile
    Post:int    #no of self posts
    Repost:int  #no of reposts
    Feed:int    #no of posts on profile feed
    Image:int   #no of posts having an image

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

        
#This route is unused currently
@app.get("/")
async def welcome_user(user: str = "user"):
    return {"message": f"Hello, {user}!"}


#This is the route where calls from the frontend is recieved if it is asking for prediction
#the data recieved is a json object like {"text":"the text to analyse"}
@app.post("/api")
async def root(
    body: Big
):
    body = body.dict()
    # Use the preprocess_and_predict function from predictor.py
    recieved = body["text"]
    Text= recieved      # This is the post text received
    print(Text)         # you should see the post in your terminal
    
    # TODO call your own process_and_predict function
    #result = preprocess_and_predict(Text)      # < -- This preprocess_and_predict needs a string as parameter
    
    # print(result)
    
    #The below is a dummy return 
    # once processed return your own result instead
    result= "openness"
    return {"data":result}

import uvicorn

if __name__=='__main__':
    uvicorn.run("api:app", port=8090, reload=True)
