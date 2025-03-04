import os
import requests
import cv2
import pytesseract
import numpy as np
from pytesseract import Output
import mimetypes

# Ensure Tesseract is correctly set up (adjust the path if needed)
pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe"

from __init__ import set_dir
set_dir()

def download_and_process_image(url):
    """
    Downloads an image from a URL, processes it in memory to extract text using OCR,
    and, if a face is detected, performs a dummy expression detection.
    
    Args:
        url (str): The URL of the image.
    
    Returns:
        dict: Contains:
            - 'ocr_text': Extracted text from the image (empty string if blank).
            - 'expression': Detected expression label if a face is found; else empty string.
    """
    result = {"ocr_text": "", "expression": ""}
    try:
        # Download the image with a timeout for robustness
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Check if the response is an image
        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            return result
        
        # Decode the image from bytes (in memory)
        image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
        if image is None:
            return result
        
        # Preprocess for OCR: convert to grayscale, apply adaptive thresholding and median blur
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        processed = cv2.medianBlur(thresh, 3)
        
        # Perform OCR on the processed image
        ocr_text = pytesseract.image_to_string(processed, output_type=Output.STRING).strip()
        result['ocr_text'] = ocr_text
        
        # Detect face and get an expression label instead of coordinates
        expression = detect_face_expression(image)
        if expression:
            result['expression'] = expression
        
        return result

    except Exception as e:
        # On exception, return empty strings
        return result

def detect_face_expression(image):
    """
    Detects a face in the image using a Haar cascade and returns a dummy expression label.
    
    Args:
        image (numpy.ndarray): The input image.
    
    Returns:
        str: A dummy expression (e.g., "Happy", "Neutral", "Sad") if a face is detected;
             otherwise, an empty string.
    """
    try:
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 0:
            return ""
        
        # For simplicity, consider only the first detected face
        (x, y, w, h) = faces[0]
        face_img = image[y:y+h, x:x+w]
        
        # Get an expression label using a dummy function
        expression = detect_expression_dummy(face_img)
        return expression
    except Exception as e:
        return ""

def detect_expression_dummy(face_img):
    """
    Dummy facial expression detection based on mean brightness.
    
    Args:
        face_img (numpy.ndarray): The cropped face image.
    
    Returns:
        str: A simulated expression label ("Happy", "Neutral", or "Sad").
    """
    try:
        # Convert the face image to grayscale and compute the mean brightness
        gray_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        mean_val = np.mean(gray_face)
        # Simple heuristic: brighter face implies "Happy", medium brightness "Neutral", lower "Sad"
        if mean_val > 150:
            return "Happy"
        elif mean_val > 100:
            return "Neutral"
        else:
            return "Sad"
    except Exception as e:
        return ""

if __name__=="__main__":
    # Example URL for testing – replace with an appropriate image URL
    test_url = "https://i.sstatic.net/IvV2y.png"
    result = download_and_process_image(test_url)
    print("OCR Text:", result.get('ocr_text'))
    if result.get('expression'):
        print("Detected Expression:", result.get('expression'))
