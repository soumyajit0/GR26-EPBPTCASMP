import cv2
import pytesseract
from pytesseract import Output
import os
import mimetypes
from deepface import DeepFace
import requests

def process_file(file_path):
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

            # Analyze facial expressions if faces are detected
            try:
                analysis = DeepFace.analyze(img_path=file_path, actions=['emotion'], enforce_detection=False)
                if isinstance(analysis, list) and len(analysis) > 0:
                    dominant_emotion = analysis[0].get('dominant_emotion', 'Unknown')
                else:
                    dominant_emotion = 'Unknown'
                return f"Detected Text: {text}\nDominant Facial Expression: {dominant_emotion}"
            except Exception as e:
                return f"Detected Text: {text}\nFacial Expression Analysis Error: {str(e)}"

        elif mime_type and mime_type.startswith("video"):
            # Process video
            cap = cv2.VideoCapture(file_path)

            frame_count = 0
            expressions = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if frame_count % 30 == 0:  # Analyze every 30th frame
                    temp_path = "temp_frame.jpg"
                    cv2.imwrite(temp_path, frame)
                    try:
                        analysis = DeepFace.analyze(img_path=temp_path, actions=['emotion'], enforce_detection=False)
                        if isinstance(analysis, list) and len(analysis) > 0:
                            dominant_emotion = analysis[0].get('dominant_emotion', 'Unknown')
                            expressions.append(dominant_emotion)
                    except:
                        pass
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

            cap.release()

            if expressions:
                most_common_expression = max(set(expressions), key=expressions.count)
                return f"Dominant Facial Expression in Video: {most_common_expression}"

            return "No facial expressions detected in the video."

        else:
            return "Error: Unsupported file type. Only images and videos are supported."

    except Exception as e:
        return f"An error occurred: {str(e)}"

    finally:
        # Delete the file
        if os.path.exists(file_path):
            print("File removed")
            os.remove(file_path)

def download_image(url, save_path='downloaded_image.jpg'):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved as {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")

# url = "https://scontent.fccu31-2.fna.fbcdn.net/v/t39.30808-6/468727013_1135215774637515_2086417753404857117_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=833d8c&_nc_ohc=nZ8UksoF_JQQ7kNvgFp2Fyi&_nc_zt=23&_nc_ht=scontent.fccu31-2.fna&_nc_gid=AqUzAYKvClTI4FYS0vLexxd&oh=00_AYDJ-aFYQ4RI8_bZmQpvMDNczLisYZhMgd8RbdFkiop_5g&oe=676EF9AA"
# download_image(url)
# file_path = "downloaded_image.jpg"
# result = process_file(file_path)
# print(result)