import os
import requests
import cv2
import pytesseract
import mimetypes
import random
from pytesseract import Output
from PIL import Image
import requests

# taken from https://github.com/UB-Mannheim/tesseract/wiki
pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe"


from __init__ import set_dir
set_dir()


def download_and_process_image(url, save_dir='downloads'):
    """
    Downloads an image from a URL, assigns a unique name, extracts text using OCR, and deletes the image.

    Args:
        url (str): The URL of the image.
        save_dir (str): The directory where the image should be saved.

    Returns:
        str: Extracted text from the image or an error message.
    """
    try:
        # Ensure the save directory exists
        os.makedirs(save_dir, exist_ok=True)

        # Generate a unique filename
        while True:
            random_number = random.randint(1000, 9999)
            save_path = os.path.join(save_dir, f"image#{random_number}.jpg")
            if not os.path.exists(save_path):
                break

        # Download the image
        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            file.write(response.content)

        print(f"Image saved as {save_path}")

        # Process the image
        text = process_file(save_path)

        # Delete the image after processing
        os.remove(save_path)
        print(f"Deleted {save_path}")

        return text

    except Exception as e:
        return f"Error: {str(e)}"

def process_file(file_path):
    """
    Processes an image file to extract text using Tesseract OCR.

    Args:
        file_path (str): The path to the file to process.

    Returns:
        str: Extracted text from the image.
    """
    try:
        mime_type, _ = mimetypes.guess_type(file_path)

        if mime_type and mime_type.startswith("image"):
            image = cv2.imread(file_path)
            if image is None:
                return "Error: Unable to read the image file."

            text = pytesseract.image_to_string(image, output_type=Output.STRING).strip()
            return text

        return "Error: Unsupported file type. Only images are supported."

    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__=="__main__":
    url="https://i.sstatic.net/IvV2y.png"
    response=download_and_process_image(url)
    print(response)