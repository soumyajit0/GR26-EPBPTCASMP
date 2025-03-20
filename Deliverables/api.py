'''
Make sure to run this server on port 8090 or
change the url path on the background.js script
'''
import os
import json
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
import socket
from contextlib import asynccontextmanager
from utils.DBN_ANN import ANN, DBN, RBM, train_ann_model, train_dbn_model

from utils.predictor import (
    load_models, 
    update_personality_aggregation, 
    get_aggregated_personality, 
    reset_personality_aggregation,
    get_aggregated_details  
)
from image_analysis import download_and_process_image

from __init__ import set_dir

set_dir()

Result=dict()
Verify =False       #Was used to validate results, not used for now
User_name="none"

class Input(BaseModel): #User's post
    url: str
    text: str
    imgs: List[str]

class Name(BaseModel):  #User's name
    url: str
    name: str
    
class Profile(BaseModel):   #web service sends a new profile link
    url:str




@asynccontextmanager
async def lifespan(app: FastAPI):
    global Verify
    Verify = False #True if input("Verify results?(Y/N): ") == 'Y' else False
    await set_up()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/public", StaticFiles(directory="public"), name="public")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_main():
    return FileResponse("public/html/main.html")


@app.post("/send_name")
async def get_user_name(body: Name):
    """
    Receives and processes the user's name.
    """
    global User_name
    name = body.name
    name = " ".join(name.split(" ")[:2])
    url = body.url
    print("User:", name, "Url:", url)
    User_name=name
    return {"success": True}

@app.get('/get_name')
async def send_name():
    global User_name
    return {"name":User_name}

@app.get("/result")
async def get_result():
    return dict(Result)

@app.post("/profile")
async def receive_profile_link(body:Profile):
    """
    Receives and processes the user's name.
    """
    global Result,User_name
    User_name="none"
    Result.clear()
    link = body.url
    print("New Profile: ",link)
    reset_personality_aggregation()  #Reset aggregation for a new session
    send_data(msg_type="PROFILE",msg_data=link)
    return {"success": True}


@app.get("/reset")
def reset_all():
    """
    Resets the plot data.
    """
    global User_name,Result
    Result.clear()
    reset_personality_aggregation()
    User_name="none"
    send_data(msg_type='STOP SCROLL')
    return {"message": "Reset Complete"}


@app.post("/api")
async def analyze_personality(body: Input):
    """
    Analyzes personality traits based on text and image inputs, updates the aggregation,
    and prints the post details and current aggregates.
    
    Returns:
        dict: Aggregated personality prediction.
    """
    global Verify,vectorizer,Result
    body = body.dict()
    url = body.get("url", "NONE")
    post_text = body["text"]  # Text content received
    img_links = body.get("imgs", [])  # Image URLs received

    # Process images: extract OCR text and expression label if any.
    whole_image_text = ""
    expressions = []
    for img_url in img_links:
        result = download_and_process_image(img_url)
        extracted_text = result.get("ocr_text", "")
        if extracted_text:
            whole_image_text += extracted_text + ". "
        if result.get("expression"):
            expressions.append(result.get("expression"))

    combined_text = whole_image_text + post_text

    # Print out the details of this post
    print("----- New Post Received -----")
    print("Post Text:")
    print(post_text[:100])
    if whole_image_text:
        print("Image OCR Text:")
        print(whole_image_text)
    if expressions:
        print("Detected Expression(s):")
        for expr in expressions:
            print(expr)

    # Update global personality aggregation with the combined text
    update_personality_aggregation(combined_text,url, models, vectorizer)
    overall_result = get_aggregated_personality()
    
    print("Aggregated MBTI Prediction:", overall_result)
    
    # Print individual trait aggregates
    aggregates = get_aggregated_details()
    print("Current Aggregation Details:")
    for dichotomy, data in aggregates.items():
        print(f"  {dichotomy}:")
        for letter, stats in data.items():
            print(f"    {letter}: count = {stats['count']}, confidence sum = {stats['conf_sum']:.2f}")
    
    #update_frame(url, overall_result)  # Gives output in native window, no longer used
    if overall_result in Result:
        Result[overall_result]+=1
    else:
        Result[overall_result]=1
    return {"data": overall_result}



async def set_up():
    """
    Loads the models and vectorizer required for personality prediction and stores them globally.
    """
    send_data(msg_type="LOGIN")         #Initial fb login
    global models, vectorizer
    models, vectorizer = load_models()
    if models and vectorizer:
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

if __name__ == '__main__':
    uvicorn.run("api:app", port=8090, reload=False)

# --------------------------For verification don't touch -------------------------------------
# --------------------------------------------------------------------------------------------
def send_data(host='127.0.0.1', port=65431, msg_type="default", msg_data="Hello, Server!"):
    """
    Sends a structured message (type and data) to a server.

    :param host: IP address of the server.
    :param port: Port the server is listening on.
    :param msg_type: Type of the message.
    :param msg_data: The actual data of the message.
    """
    message = json.dumps({"type": msg_type, "data": msg_data})  # Convert to JSON

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        client_socket.sendall(message.encode('utf-8'))  # Send JSON message
