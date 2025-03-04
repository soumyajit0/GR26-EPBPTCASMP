'''
Make sure to run this server on port 8090 or
change the url path on the background.js script
'''
import os
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import socket
from contextlib import asynccontextmanager

from visualize import visualize_personality_predictions, update_frame, reset
from utils.predictor import (
    load_models, 
    predict_personality, 
    translate_back, 
    update_personality_aggregation, 
    get_aggregated_personality, 
    reset_personality_aggregation,
    get_aggregated_details  # New helper to get the detailed aggregates
)
from image_analysis import download_and_process_image
from utils.DBN_ANN import ANN, DBN, RBM, train_ann_model, train_dbn_model

from __init__ import set_dir

set_dir()

class Input(BaseModel):
    url: str
    text: str
    imgs: List[str]

class Name(BaseModel):
    url: str
    name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    global Verify
    Verify = True if input("Verify results?(Y/N): ") == 'Y' else False
    await set_up()
    threading.Thread(target=visualize_personality_predictions, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Verify = False

@app.get("/")
async def welcome_user(user: str = "user"):
    """
    Welcomes the user.
    """
    return {"message": f"Hello, {user}!"}

@app.post("/send_name")
async def send_user_name(body: Name):
    """
    Receives and processes the user's name.
    """
    name = body.name
    name = " ".join(name.split(" ")[:2])
    url = body.url
    print("User:", name, "Url:", url)
    reset(url, name)
    reset_personality_aggregation()  # Reset aggregation for a new session
    return {"success": True}

@app.get("/reset")
def reset_plot_data():
    """
    Resets the plot data.
    """
    reset(None, "None")
    return {"message": "Complete"}

@app.post("/api")
async def analyze_personality(body: Input):
    """
    Analyzes personality traits based on text and image inputs, updates the aggregation,
    and prints the post details and current aggregates.
    
    Returns:
        dict: Aggregated personality prediction.
    """
    global Verify
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
    print(post_text)
    if whole_image_text:
        print("Image OCR Text:")
        print(whole_image_text)
    if expressions:
        print("Detected Expression(s):")
        for expr in expressions:
            print(expr)

    # Update global personality aggregation with the combined text
    update_personality_aggregation(combined_text, models, vectorizer)
    overall_result = get_aggregated_personality()
    
    print("Aggregated MBTI Prediction:", overall_result)
    
    # Print individual trait aggregates
    aggregates = get_aggregated_details()
    print("Current Aggregation Details:")
    for dichotomy, data in aggregates.items():
        print(f"  {dichotomy}:")
        for letter, stats in data.items():
            print(f"    {letter}: count = {stats['count']}, confidence sum = {stats['conf_sum']:.2f}")
    
    update_frame(url, overall_result)
    if Verify:
        try:
            send_data(message=overall_result)
        except Exception as e:
            print("Verification send error:", e)
    return {"data": overall_result}

async def set_up():
    """
    Loads the models and vectorizer required for personality prediction and stores them globally.
    """
    global models, vectorizer
    models, vectorizer = load_models(
        models_path=r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\models.pkl",
        vectorizer_path=r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\vectorizer.pkl"
    )
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
# -------------------------------------------------------------------------------------------
def send_data(host='127.0.0.1', port=65431, message="Hello, Server!"):
    """
    Sends data to a server for verification purposes.
    
    :param host: IP address of the server.
    :param port: Port the server is listening on.
    :param message: The message to send.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        client_socket.sendall(message.encode('utf-8'))
        return
