'''
Make sure to run this server on port 8090 or
change the url path on the background.js script
'''
import os
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Union, List
import mimetypes
import cv2
import pytesseract
from pytesseract import Output
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import requests
from visualize import visualize_personality_predictions, update_frame, reset
from utils.predictor import load_models, predict_personality, translate_back

# Define Pydantic models to validate API request data
class Big(BaseModel):
    text: str  # Text content for analysis
    imgs: List[str]  # List of image URLs for analysis

class Item(BaseModel):
    Name: str  # Name of the user
    Age: int   # User age
    Gender: str
    Data: dict # The dict data formed by analysing the user profile
    Post: int  # Number of self posts
    Repost: int  # Number of reposts
    Feed: int  # Number of posts on profile feed
    Image: int  # Number of posts having an image

class Name(BaseModel):
    name: str  # Name of the user

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility function to download an image from a URL
def download_image(url, save_path='downloaded_image.jpg'):
    """
    Downloads an image from the given URL and saves it to the specified path.

    Args:
        url (str): The URL of the image to download.
        save_path (str): The file path to save the downloaded image.

    Returns:
        str: The path to the downloaded image, or None if download failed.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved as {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
        return None

# Utility function to process a file (image or video) and extract text

def process_file(file_path):
    """
    Processes an image file to extract text using Tesseract OCR.

    Args:
        file_path (str): The path to the file to process.

    Returns:
        str: Extracted text from the image.
    """
    try:
        # Determine file type
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type and mime_type.startswith("image"):
            # Process image
            image = cv2.imread(file_path)
            if image is None:
                return "Error: Unable to read the image file."

            # Extract text using Tesseract OCR
            text = pytesseract.image_to_string(image, output_type=Output.STRING).strip()
            return text

        else:
            return "Error: Unsupported file type. Only images are supported."

    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.get("/")
async def welcome_user(user: str = "user"):
    return {"message": f"Hello, {user}!"}

@app.post("/send_name")
async def send_name(body: Name):
    """
    Resets the user environment with the given name.

    Args:
        body (Name): JSON payload with the user's name.

    Returns:
        dict: Success status.
    """
    name = body.name
    print(name)
    reset(name)
    return {"success": True}
  
import socket

def send_data(host='127.0.0.1', port=65431, message="Hello, Server!"):
    """
    Sends data to a server.

    :param host: IP address of the server.
    :param port: Port the server is listening on.
    :param message: The message to send.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        client_socket.sendall(message.encode('utf-8'))  # Send message
        return
@app.post("/api")
async def root(body: Big):
    """
    Analyzes personality traits based on text and image inputs.

    Args:
        body (Big): JSON payload with text and image URLs.

    Returns:
        dict: Analyzed personality results.
    """
    body = body.dict()
    recieved_text = body["text"]  # Text content received
    img_links = body.get('imgs', [])  # Image URLs received

    # Predict personality based on the text
    predictions = predict_personality(recieved_text)
    temp = []
    for personality, result in predictions.items():
        print(f"Personality Type: {personality}")
        print(f"Prediction: {(result['prediction'])}")
        temp.append(result['prediction'])
        print(f"Probability: {result['probability']:.2f}")
        print()

    # Process images and extract text for additional personality analysis
    for img_url in img_links:
        downloaded_path = download_image(img_url)
        if downloaded_path:
            extracted_text = process_file(downloaded_path)
            print(f"Extracted Text from Image: {extracted_text}")
            if extracted_text:
                img_predictions = predict_personality(extracted_text)
                for personality, result in img_predictions.items():
                    print(f"Image Personality Type: {personality}")
                    print(f"Prediction: {(result['prediction'])}")
                    temp.append(result['prediction'])
                    print(f"Probability: {result['probability']:.2f}")
                    print()

    # Translate and update frame with predictions
    result = translate_back(temp)
    update_frame(result)
    send_data(message=result)
    return {"data": result}


async def set_up():
    """
    Loads models and sets up the environment on server startup.
    """
    # Get the directory of the current file (api.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Change the working directory to the current directory
    os.chdir(current_dir)
    result = load_models()
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
    await set_up()
    threading.Thread(target=visualize_personality_predictions, daemon=True).start()
    await set_up()

if __name__ == '__main__':
    uvicorn.run("api:app", port=8090, reload=False)






#for testing only
# @app.get("/test")
# async def test():
#     temp = "This is a text to be evaluated as a temporary placeholder"
#     predictions = predict_personality(temp)

#     # Convert predictions to JSON-serializable format
#     json_serializable_predictions = {
#         personality: {
#             "prediction": int(result['prediction']),  # Convert numpy.int64 to Python int
#             "probability": float(result['probability']),  # Ensure probability is float
#         }
#         for personality, result in predictions.items()
#     }

#     return {"predictions": json_serializable_predictions}

# import uvicorn
# import httpx  # HTTP client for testing

# if __name__ == '__main__':
#     # Start the FastAPI app in a separate thread
#     def run_server():
#         uvicorn.run("api:app", port=8090, reload=False)

#     # Run the server in a thread
#     server_thread = threading.Thread(target=run_server, daemon=True)
#     server_thread.start()

#     # Wait for the server to start (give it a moment)
#     import time
#     time.sleep(2)

#     # Test the /test endpoint
#     print("Testing the /test endpoint...")
#     try:
#         with httpx.Client() as client:
#             response = client.get("http://127.0.0.1:8090/test")
#             if response.status_code == 200:
#                 print("Response from /test endpoint:")
#                 print(response.json())
#             else:
#                 print(f"Error: {response.status_code} - {response.text}")
#     except Exception as e:
#         print(f"An error occurred while testing: {e}")
