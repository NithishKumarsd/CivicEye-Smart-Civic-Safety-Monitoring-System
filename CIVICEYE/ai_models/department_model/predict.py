"""
Department Classification Prediction Module
"""

import pickle
import os
import re

def load_department_model():
    """Load the trained department classification model"""
    model_path = "ai_models/department_model/model.pkl"
    vectorizer_path = "ai_models/department_model/vectorizer.pkl"
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        return model, vectorizer
    except FileNotFoundError:
        # Train model if not found
        from ai_models.department_model.train import train_department_model
        train_department_model()
        return load_department_model()

def preprocess_text(text):
    """Preprocess text for prediction"""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return ' '.join(text.split())

def predict_department(title, description):
    """Predict department for complaint"""
    model, vectorizer = load_department_model()
    
    # Combine and preprocess text
    full_text = f"{title} {description}"
    processed_text = preprocess_text(full_text)
    
    # Predict
    X = vectorizer.transform([processed_text])
    prediction = model.predict(X)[0]
    confidence = max(model.predict_proba(X)[0])
    
    return prediction, confidence