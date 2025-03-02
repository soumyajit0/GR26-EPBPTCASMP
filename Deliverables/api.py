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
from utils.predictor import load_models, predict_personality, translate_back
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
    print("User: ", name, "Url: ", url)
    reset(url, name)
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
    Analyzes personality traits based on text and image inputs.

    Args:
        body (Input): JSON payload with text and image URLs.

    Returns:
        dict: Analyzed personality results.
    """
    global Verify
    body = body.dict()
    url = body.get("url", "NONE")
    received_text = body["text"]  # Text content received
    img_links = body.get('imgs', [])  # Image URLs received

    # Process images and extract text for additional personality analysis
    whole_image_text = ""
    for img_url in img_links:
        extracted_text = download_and_process_image(img_url)
        if extracted_text:
            whole_image_text += extracted_text + ". "
        else:
            print("No text extracted from image.")
        print()

    print("Text from images: ", whole_image_text)
    # Adding the whole image text in front of post text
    received_text = whole_image_text + received_text

    predictions = predict_personality(received_text)
    temp = []
    for personality, result in predictions.items():
        print(f"Personality Type: {personality}")
        print(f"Prediction: {(result['prediction'])}")
        temp.append(result['prediction'])
        print(f"Probability: {result['probability']:.2f}")
        print()

    # Translate and update frame with predictions
    result = translate_back(temp)
    update_frame(url, result)
    if Verify:
        send_data(message=result)
    return {"data": result}

async def set_up():
    """
    Loads the models required for personality prediction.
    """
    result = load_models(models_path = r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\models.pkl",vectorizer_path = r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\vectorizer.pkl")
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
        client_socket.sendall(message.encode('utf-8'))  # Send message
        return