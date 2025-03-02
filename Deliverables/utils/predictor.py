import os
import re
import pickle
import numpy as np
import torch
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import download
from nltk.data import find
from sklearn.feature_extraction.text import TfidfVectorizer

# Import custom models and training functions from DBN_ANN module
from .DBN_ANN import ANN, DBN, RBM, train_ann_model, train_dbn_model

# --- Global Personality Definitions ---
personality_type = ["IE", "NS", "FT", "JP"]  # List of personality dichotomies
b_Pers = {'I': 0, 'E': 1, 'N': 0, 'S': 1, 'F': 0, 'T': 1, 'J': 0, 'P': 1}  # Mapping letters to binary
b_Pers_list = [
    {0: 'I', 1: 'E'},  # Mapping binary values back to letters
    {0: 'N', 1: 'S'},
    {0: 'F', 1: 'T'},
    {0: 'J', 1: 'P'}
]

def download_if_not_exists(resource, identifier):
    try:
        find(identifier)
        print(f"✅ {resource} exists.")
    except LookupError:
        download(resource)

# Download necessary NLTK data
download_if_not_exists('stopwords', 'corpora/stopwords.zip')
download_if_not_exists('wordnet', 'corpora/wordnet.zip')

# Define stop words and lemmatizer for text preprocessing
useless_words = set(stopwords.words('english'))
lemmatiser = WordNetLemmatizer()

def preprocess_posts(text):
    """
    Preprocesses the input text by removing URLs, non-alphabetic characters,
    long repeated characters, and stopwords, and then lemmatizes the words.
    """
    text = re.sub('http[s]?://\S+', '', text)            # Remove URLs
    text = re.sub("[^a-zA-Z]", " ", text).lower()          # Remove non-alphabetic characters and lowercase
    text = re.sub(r'([a-z])\1{2,}', '', text)              # Remove long repeated characters
    tokens = [lemmatiser.lemmatize(word) for word in text.split() if word not in useless_words]
    return " ".join(tokens)

def extract_dichotomy_labels(data):
    """
    Extracts binary labels for each personality dichotomy from the input data.
    """
    labels = data['type'].apply(lambda x: [b_Pers[x[0]], b_Pers[x[1]], b_Pers[x[2]], b_Pers[x[3]]])
    return np.array(labels.tolist())

def vectorize_text(posts, max_features=1000):
    """
    Vectorizes the input text using TF-IDF.
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    X = vectorizer.fit_transform(posts)
    return X, vectorizer

def predict_personality(input_text, models, vectorizer):
    """
    Predicts the personality type for the given input text using the loaded models and vectorizer.
    """
    preprocessed_text = preprocess_posts(input_text)
    transformed_text = vectorizer.transform([preprocessed_text])
    
    predictions = {}
    mbti = ""
    for i, dichotomy in enumerate(personality_type):
        model = models[dichotomy]
        if hasattr(model, "forward"):  # PyTorch model
            input_dense = torch.FloatTensor(transformed_text.toarray()).to(next(model.parameters()).device)
            model.eval()
            with torch.no_grad():
                output = model(input_dense)
            pred = int(output.item() > 0.5)
            prob = output.item()
        else:  # scikit-learn model
            pred = model.predict(transformed_text)[0]
            prob = model.predict_proba(transformed_text)[0][pred] if hasattr(model, "predict_proba") else None
        predictions[dichotomy] = {'prediction': pred, 'probability': prob}
        mbti += b_Pers_list[i][pred]
    predictions['MBTI'] = mbti
    return predictions

def translate_back(pred_list):
    """
    Translates a list of binary predictions back into a 4-letter MBTI type.
    """
    mbti = ""
    for i, pred in enumerate(pred_list):
        mbti += b_Pers_list[i][pred]
    return mbti

def save_models(models, vectorizer, models_path="models.pkl", vectorizer_path="vectorizer.pkl"):
    """
    Saves the trained models and vectorizer to disk.
    """
    with open(models_path, 'wb') as f:
        pickle.dump(models, f)
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"✅ Models saved to {models_path}")
    print(f"✅ Vectorizer saved to {vectorizer_path}")

def load_models(models_path="models.pkl", vectorizer_path="vectorizer.pkl"):
    """
    Loads the trained models and vectorizer from disk.
    """
    with open(models_path, 'rb') as f:
        models = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    print(f"✅ Loaded models from {models_path}")
    print(f"✅ Loaded vectorizer from {vectorizer_path}")
    return models, vectorizer

# Define paths to your pickled models and vectorizer
models_path = r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\models.pkl"
vectorizer_path = r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\vectorizer.pkl"

if __name__ == "__main__":
    try:
        models, vectorizer = load_models(models_path=models_path, vectorizer_path=vectorizer_path)
        print("✅ Models and vectorizer loaded successfully.")
    except (FileNotFoundError, AttributeError, pickle.UnpicklingError) as e:
        print(f"❌ Error loading models or vectorizer: {e}")
