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

# ML imports
from sklearn.linear_model import LogisticRegression
import re
import numpy as np
import pickle
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import stopwords
import nltk

# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

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

# MBTI unique types and binary translation dictionaries
unique_type_list = [
    'infj', 'entp', 'intp', 'intj', 'entj', 'enfj', 'infp', 'enfp',
    'istp', 'isfp', 'isfj', 'istj', 'estp', 'esfp', 'estj', 'esfj'
]
b_Pers = {'I': 0, 'E': 1, 'N': 0, 'S': 1, 'F': 0, 'T': 1, 'J': 0, 'P': 1}
b_Pers_list = [{0: 'I', 1: 'E'}, {0: 'N', 1: 'S'}, {0: 'F', 1: 'T'}, {0: 'J', 1: 'P'}]

def translate_personality(personality):
    return [b_Pers[l] for l in personality]

def translate_back(personality):
    s = ""
    for i, l in enumerate(personality):
        s += b_Pers_list[i][l]
    return s

# Defining stop words and lemmatizer
useless_words = set(stopwords.words('english'))
lemmatiser = WordNetLemmatizer()

# Load the trained models
with open('pkls/mbti_models.pkl', 'rb') as f:
    models = pickle.load(f)

# Load the trained TF-IDF vectorizer
with open('pkls/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)

personality_type = [
    "IE: Introversion (I) / Extroversion (E)",
    "NS: Intuition (N) / Sensing (S)",
    "FT: Feeling (F) / Thinking (T)",
    "JP: Judging (J) / Perceiving (P)"
]

def preprocess_posts(posts, remove_stop_words=True, remove_mbti_profiles=True):
    temp = posts

    # Remove url links
    temp = re.sub(r'http[s]?://\S+', ' ', temp)

    # Remove Non-words - keep only words
    temp = re.sub(r"[^a-zA-Z]", " ", temp)

    # Remove spaces > 1
    temp = re.sub(r' +', ' ', temp).lower()

    # Remove multiple letter repeating words
    temp = re.sub(r'([a-z])\1{2,}', '', temp)

    # Remove stop words
    if remove_stop_words:
        temp = " ".join([lemmatiser.lemmatize(w) for w in temp.split() if w not in useless_words])
    else:
        temp = " ".join([lemmatiser.lemmatize(w) for w in temp.split()])

    # Remove MBTI personality words from posts
    if remove_mbti_profiles:
        for t in unique_type_list:
            temp = temp.replace(t, "")

    return temp

def predict_personality(input_text):
    preprocessed_text = preprocess_posts(input_text)
    transformed_text = tfidf_vectorizer.transform([preprocessed_text])

    predictions = {}
    for personality in personality_type:
        model = models[personality]
        prediction = model.predict(transformed_text)[0]
        probability = model.predict_proba(transformed_text)[0]
        predictions[personality] = {
            'prediction': prediction,
            'probability': probability[1] if prediction == 1 else probability[0]
        }

    return predictions

import uvicorn

if __name__ == '__main__':
    uvicorn.run("api:app", port=8090, reload=True)
