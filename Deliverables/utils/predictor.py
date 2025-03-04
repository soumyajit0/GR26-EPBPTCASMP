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

# Import custom models and training functions from DBN_ANN.py
from DBN_ANN import ANN, DBN, RBM, train_ann_model, train_dbn_model

# Global Personality Definitions
personality_type = ["IE", "NS", "FT", "JP"]  # Each dichotomy (e.g., IE for Introversion/Extroversion)
# Mapping letters to binary values: e.g., I=0, E=1, etc.
b_Pers = {'I': 0, 'E': 1, 'N': 0, 'S': 1, 'F': 0, 'T': 1, 'J': 0, 'P': 1}
# Mapping binary values back to letters for each dichotomy
b_Pers_list = [
    {0: 'I', 1: 'E'},
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

# Download necessary NLTK data if not already present.
download_if_not_exists('stopwords', 'corpora/stopwords.zip')
download_if_not_exists('wordnet', 'corpora/wordnet.zip')

# Set up stopwords and lemmatizer for text preprocessing.
useless_words = set(stopwords.words('english'))
lemmatiser = WordNetLemmatizer()

def preprocess_posts(text):
    """
    Preprocess the input text: remove URLs, non-alphabet characters,
    long repeated characters, and stopwords; then lemmatize the words.
    """
    text = re.sub('http[s]?://\S+', '', text)            # Remove URLs
    text = re.sub("[^a-zA-Z]", " ", text).lower()          # Keep only alphabets and lowercase
    text = re.sub(r'([a-z])\1{2,}', '', text)              # Remove long repeated characters
    tokens = [lemmatiser.lemmatize(word) for word in text.split() if word not in useless_words]
    return " ".join(tokens)

def vectorize_text(posts, max_features=1000):
    """
    Vectorize the input text using TF-IDF.
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    X = vectorizer.fit_transform(posts)
    return X, vectorizer

def predict_personality(input_text, models, vectorizer):
    """
    Predict the personality dichotomies from input text.
    
    Args:
        input_text (str): The raw text input.
        models (dict): A dictionary containing models for each dichotomy (keys: "IE", "NS", "FT", "JP").
        vectorizer: A fitted TF-IDF vectorizer.
        
    Returns:
        dict: For each dichotomy, a dictionary with:
              'prediction': 0 or 1, and
              'probability': confidence score.
              Also includes an 'MBTI' key with the 4-letter personality type.
    """
    preprocessed_text = preprocess_posts(input_text)
    transformed_text = vectorizer.transform([preprocessed_text])
    
    predictions = {}
    mbti = ""
    for i, dichotomy in enumerate(personality_type):
        model = models[dichotomy]
        if hasattr(model, "forward"):  # For PyTorch models
            input_dense = torch.FloatTensor(transformed_text.toarray()).to(next(model.parameters()).device)
            model.eval()
            with torch.no_grad():
                output = model(input_dense)
            pred = int(output.item() > 0.5)
            prob = output.item()
        else:  # For scikit-learn models
            pred = model.predict(transformed_text)[0]
            prob = model.predict_proba(transformed_text)[0][pred] if hasattr(model, "predict_proba") else None
        predictions[dichotomy] = {'prediction': pred, 'probability': prob}
        mbti += b_Pers_list[i][pred]
    predictions['MBTI'] = mbti
    return predictions

def translate_back(pred_list):
    """
    Translate a list of binary predictions into a 4-letter MBTI type.
    """
    mbti = ""
    for i, pred in enumerate(pred_list):
        mbti += b_Pers_list[i][pred]
    return mbti

def save_models(models, vectorizer, models_path="models.pkl", vectorizer_path="vectorizer.pkl"):
    """
    Save the trained models and vectorizer to disk.
    """
    with open(models_path, 'wb') as f:
        pickle.dump(models, f)
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"✅ Models saved to {models_path}")
    print(f"✅ Vectorizer saved to {vectorizer_path}")

def load_models(models_path, vectorizer_path):
    """
    Load trained models and vectorizer from disk.
    """
    with open(models_path, 'rb') as f:
        models = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    print(f"✅ Loaded models from {models_path}")
    print(f"✅ Loaded vectorizer from {vectorizer_path}")
    return models, vectorizer

# -----------------------------------------------------------------------------
# Global aggregation for personality predictions from multiple posts.
# We now store both the cumulative confidence and count for each trait.
personality_aggregation = {
    "IE": {"I": {"count": 0, "conf_sum": 0.0}, "E": {"count": 0, "conf_sum": 0.0}},
    "NS": {"N": {"count": 0, "conf_sum": 0.0}, "S": {"count": 0, "conf_sum": 0.0}},
    "FT": {"F": {"count": 0, "conf_sum": 0.0}, "T": {"count": 0, "conf_sum": 0.0}},
    "JP": {"J": {"count": 0, "conf_sum": 0.0}, "P": {"count": 0, "conf_sum": 0.0}}
}

def update_personality_aggregation(post_text, models, vectorizer):
    """
    Processes a single post's text, predicts personality dichotomies,
    and updates the global aggregation.
    
    Args:
        post_text (str): Text from a single post.
        models (dict): Models for each dichotomy.
        vectorizer: A fitted TF-IDF vectorizer.
    """
    global personality_aggregation
    predictions = predict_personality(post_text, models, vectorizer)
    for dichotomy in personality_type:
        pred_info = predictions[dichotomy]
        binary_pred = pred_info['prediction']  # 0 or 1
        prob = pred_info['probability']
        # For a prediction of 0 (e.g., "I"), use (1 - prob) as confidence;
        # for a prediction of 1 (e.g., "E"), use prob.
        confidence = (1 - prob) if binary_pred == 0 else prob
        idx = personality_type.index(dichotomy)
        letter = b_Pers_list[idx][binary_pred]
        personality_aggregation[dichotomy][letter]["count"] += 1
        personality_aggregation[dichotomy][letter]["conf_sum"] += confidence

def get_aggregated_personality():
    """
    Computes the overall MBTI type using the average confidence for each trait.
    
    For each dichotomy, the average confidence is computed as:
        average = conf_sum / count (if count > 0, else 0)
    The letter with the higher average is selected.
    
    Returns:
        str: Overall MBTI type.
    """
    overall_mbti = ""
    for dichotomy in personality_type:
        data = personality_aggregation[dichotomy]
        letters = list(data.keys())
        letter1, letter2 = letters[0], letters[1]
        count1 = data[letter1]["count"]
        count2 = data[letter2]["count"]
        avg1 = data[letter1]["conf_sum"] / count1 if count1 > 0 else 0.0
        avg2 = data[letter2]["conf_sum"] / count2 if count2 > 0 else 0.0
        if avg1 > avg2:
            overall_mbti += letter1
        elif avg2 > avg1:
            overall_mbti += letter2
        else:
            # Tie-breaker using counts.
            overall_mbti += letter1 if count1 >= count2 else letter2
    return overall_mbti

def reset_personality_aggregation():
    """
    Resets the global personality aggregation to its initial state.
    """
    global personality_aggregation
    personality_aggregation = {
        "IE": {"I": {"count": 0, "conf_sum": 0.0}, "E": {"count": 0, "conf_sum": 0.0}},
        "NS": {"N": {"count": 0, "conf_sum": 0.0}, "S": {"count": 0, "conf_sum": 0.0}},
        "FT": {"F": {"count": 0, "conf_sum": 0.0}, "T": {"count": 0, "conf_sum": 0.0}},
        "JP": {"J": {"count": 0, "conf_sum": 0.0}, "P": {"count": 0, "conf_sum": 0.0}}
    }

def get_aggregated_details():
    """
    Returns the current global aggregation details for all personality traits.
    
    Returns:
        dict: The personality_aggregation dictionary.
    """
    global personality_aggregation
    return personality_aggregation

# -----------------------------------------------------------------------------
# For testing purposes: load models and perform a test aggregation.
if __name__ == "__main__":
    try:
        models, vectorizer = load_models(
            r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\models.pkl",
            r"C:\Users\HP\Desktop\final_yr_project\Deliverables\pkls\ANN_pkl\vectorizer.pkl"
        )
        # A diverse list of posts representing different personality aspects:
        posts = [
            "I love spending time alone reading and reflecting on my thoughts.",                # Likely Introverted (I)
            "I enjoy lively parties and meeting lots of new people; social energy fuels me.",      # Likely Extroverted (E)
            "I rely on my intuition and abstract ideas to understand complex concepts.",         # Likely Intuitive (N)
            "I prefer dealing with concrete facts and observable details in my everyday work.",    # Likely Sensing (S)
            "I deeply care about others and let my emotions guide my decisions.",                 # Likely Feeling (F)
            "I make decisions based solely on logic and objective analysis.",                     # Likely Thinking (T)
            "I like to plan every detail in advance and keep my schedule structured.",             # Likely Judging (J)
            "I enjoy a flexible lifestyle, embracing spontaneity and unexpected adventures."       # Likely Perceiving (P)
        ]
        
        # Process each post one by one and show iteration details.
        for idx, post in enumerate(posts, start=1):
            print(f"\n----- Iteration {idx}: Processing Post -----")
            print("Post Text:")
            print(post)
            
            # Get the per-post personality prediction
            prediction = predict_personality(post, models, vectorizer)
            print("Predicted MBTI for this post:", prediction['MBTI'])
            
            # Update the aggregation with the current post.
            update_personality_aggregation(post, models, vectorizer)
            
            # Retrieve the current overall personality and detailed aggregates.
            overall = get_aggregated_personality()
            details = get_aggregated_details()
            
            print("Current Overall MBTI Prediction:", overall)
            print("Current Aggregation Details:")
            for dichotomy, data in details.items():
                print(f" {dichotomy}:")
                for letter, stats in data.items():
                    avg = stats['conf_sum'] / stats['count'] if stats['count'] > 0 else 0.0
                    print(f"   {letter}: count = {stats['count']}, average confidence = {avg:.2f}")
            print("-" * 50)
        
        # Final overall personality after processing all posts.
        print("\nFinal Overall MBTI:", overall)
    except Exception as e:
        print("Error during testing:", e)


