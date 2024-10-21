import os
# ML imports
from sklearn.linear_model import LogisticRegression
import re
import numpy as np
import pickle
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from nltk.corpus import stopwords
import nltk
from nltk.data import find
from nltk import download

models = None
tfidf_vectorizer = None

def download_if_not_exists(resource, identifier):
    try:
        find(identifier)
        print(resource,"exists")
    except LookupError:
        download(resource)

# Download NLTK data
download_if_not_exists('stopwords', 'corpora/stopwords.zip')
download_if_not_exists('wordnet', 'corpora/wordnet.zip')

# Defining stop words and lemmatizer
useless_words = set(stopwords.words('english'))
lemmatiser = WordNetLemmatizer()

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


def load_models():
    global models
    global tfidf_vectorizer
    
    try:
        # Load the trained models
        model_path = os.path.join(os.path.dirname(os.getcwd()), 'Pickle Files', 'mbti_models.pkl')
        with open(model_path, 'rb') as f:
            models = pickle.load(f)
        print(f"Models loaded: {models is not None}")

        # Load the trained TF-IDF vectorizer
        vectorizer_path = os.path.join(os.path.dirname(os.getcwd()), 'Pickle Files', 'tfidf_vectorizer.pkl')
        with open(vectorizer_path, 'rb') as f:
            tfidf_vectorizer = pickle.load(f)
        print(f"TF-IDF Vectorizer loaded: {tfidf_vectorizer is not None}")

        return models is not None and tfidf_vectorizer is not None
    
    except Exception as e:
        print(f"An error occurred while loading the models: {e}")
        return False
    

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

if __name__=="__main__":
    print("OK")
    