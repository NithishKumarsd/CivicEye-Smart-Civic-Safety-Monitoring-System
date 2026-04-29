"""
Urgency Prediction Module
"""

import pickle
import os
import re

def load_urgency_model():
    """Load the trained urgency prediction model"""
    model_path = "ai_models/urgency_model/model.pkl"
    vectorizer_path = "ai_models/urgency_model/vectorizer.pkl"
    
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        return model, vectorizer
    except FileNotFoundError:
        # Train model if not found
        from ai_models.urgency_model.train import train_urgency_model
        train_urgency_model()
        return load_urgency_model()

def preprocess_text(text):
    """Preprocess text for prediction"""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    return ' '.join(text.split())

def predict_urgency(title, description, has_image=False, near_emergency=False):
    """Predict urgency for complaint"""
    model, vectorizer = load_urgency_model()
    
    # Combine and preprocess text
    full_text = f"{title} {description}"
    processed_text = preprocess_text(full_text)
    
    # Check for emergency keywords
    emergency_keywords = [
        'emergency', 'urgent', 'danger', 'fire', 'accident', 'flood',
        'gas', 'explosion', 'collapse', 'injured', 'bleeding'
    ]
    
    has_emergency_keyword = any(word in processed_text for word in emergency_keywords)
    
    # Predict
    X = vectorizer.transform([processed_text])
    prediction = model.predict(X)[0]
    confidence = max(model.predict_proba(X)[0])
    
    # Apply business rules
    if has_emergency_keyword or near_emergency:
        prediction = "High"
    elif has_image and prediction == "Low":
        prediction = "Medium"
    
    return prediction, confidence