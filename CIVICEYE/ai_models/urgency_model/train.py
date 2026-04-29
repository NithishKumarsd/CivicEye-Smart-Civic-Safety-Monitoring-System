"""
Urgency Prediction AI Model
Predicts complaint urgency: Low, Medium, High
"""

import pickle
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import re

class UrgencyPredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = "ai_models/urgency_model/model.pkl"
        self.vectorizer_path = "ai_models/urgency_model/vectorizer.pkl"
        self.ensure_model_dir()
    
    def ensure_model_dir(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def preprocess_text(self, text):
        if not text:
            return ""
        text = str(text).lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        return ' '.join(text.split())
    
    def get_training_data(self):
        """Generate comprehensive training data for urgency prediction"""
        data = []
        
        # High urgency - Emergency situations (50 samples)
        high_urgency = [
            "emergency water pipe burst flooding street immediate help",
            "electricity wire fallen dangerous sparking fire risk",
            "gas leak smell strong evacuation needed urgent",
            "accident happened injured people bleeding help needed",
            "fire emergency immediate assistance required now",
            "building collapse danger evacuation urgent emergency",
            "sewer overflow contaminated water disease outbreak",
            "tree fallen blocking entire road traffic emergency",
            "manhole cover missing pedestrian fell injured",
            "dangerous construction debris sharp objects children",
            "transformer explosion sparking dangerous electricity",
            "major water leak flooding basement emergency",
            "road completely blocked accident emergency vehicles",
            "electrical fire sparks flying dangerous situation",
            "gas cylinder leaking strong smell evacuation",
            "bridge crack dangerous collapse risk urgent",
            "landslide blocking road emergency rescue needed",
            "chemical spill toxic fumes dangerous area",
            "building fire smoke emergency evacuation needed",
            "power line down live wire dangerous",
            "flood water rising emergency situation help",
            "explosion heard gas leak emergency response",
            "structural damage building unsafe evacuation",
            "toxic waste spill contamination emergency",
            "major accident multiple injuries emergency",
            "electrical shock incident emergency medical",
            "fire spreading rapidly emergency services needed",
            "gas main rupture emergency evacuation zone",
            "building foundation crack collapse danger",
            "hazardous material leak emergency response",
            "severe flooding emergency rescue operations",
            "electrical explosion transformer fire emergency",
            "dangerous chemical leak toxic emergency",
            "major structural failure emergency evacuation",
            "live electrical wire exposed dangerous",
            "gas explosion risk emergency situation",
            "building collapse imminent danger evacuation",
            "toxic gas leak emergency response needed",
            "major fire emergency services required",
            "electrical hazard shock risk emergency",
            "dangerous debris falling emergency area",
            "chemical fire toxic smoke emergency",
            "gas leak explosion risk immediate danger",
            "structural collapse emergency evacuation required",
            "electrical fire spreading emergency response",
            "toxic spill contamination emergency cleanup",
            "major flooding emergency rescue needed",
            "dangerous gas leak emergency situation",
            "building fire emergency evacuation now",
            "electrical explosion emergency services needed"
        ]
        
        # Medium urgency - Problems needing attention (50 samples)
        medium_urgency = [
            "street light not working visibility poor safety",
            "garbage collection irregular delay problem smell",
            "pothole causing vehicle damage inconvenience repair",
            "water pressure low timing irregular supply",
            "drainage slow water logging rain problem",
            "noise pollution construction site disturbing residents",
            "traffic congestion peak hours slow movement",
            "road repair needed cracks developing safety",
            "waste segregation not happening mixed garbage",
            "parking space insufficient residential area problem",
            "streetlight flickering electrical problem repair needed",
            "garbage bin overflowing attracting pests smell",
            "road surface uneven causing vehicle problems",
            "water supply intermittent timing issues",
            "drain blockage causing water stagnation",
            "construction noise disturbing sleep patterns",
            "traffic signal timing causing delays",
            "pavement cracks need repair before worsening",
            "waste collection truck missed schedule",
            "parking violations blocking residential access",
            "street cleaning not done regularly dirty",
            "public toilet maintenance required cleaning",
            "road marking faded visibility issues",
            "water meter reading incorrect billing",
            "drainage system needs cleaning maintenance",
            "noise from machinery disturbing area",
            "traffic bottleneck causing regular delays",
            "sidewalk repair needed pedestrian safety",
            "garbage sorting not proper mixed waste",
            "vehicle parking blocking fire hydrant",
            "street sweeping irregular dust accumulation",
            "public facility maintenance required repair",
            "road shoulder erosion needs attention",
            "water quality issues taste smell",
            "storm drain cleaning required blockage",
            "construction dust pollution problem",
            "traffic flow optimization needed congestion",
            "walkway maintenance required safety",
            "waste bin capacity insufficient area",
            "parking meter malfunction payment issues",
            "street furniture repair needed maintenance",
            "public lighting insufficient dark areas",
            "road signage maintenance visibility issues",
            "water connection leak minor repair",
            "drainage improvement needed flooding prevention",
            "noise control measures needed residential",
            "traffic management improvement required",
            "infrastructure maintenance needed repair",
            "waste management optimization required",
            "public safety measures improvement needed"
        ]
        
        # Low urgency - Routine maintenance (50 samples)
        low_urgency = [
            "street light bulb replacement routine maintenance",
            "garbage bin additional capacity request",
            "small pothole minor inconvenience routine",
            "water meter reading schedule request",
            "general complaint feedback suggestion improvement",
            "road marking paint faded renewal routine",
            "park maintenance grass cutting scheduled",
            "information request municipal services inquiry",
            "complaint status inquiry follow up",
            "tree pruning beautification garden maintenance",
            "routine inspection request scheduled maintenance",
            "information about municipal services available",
            "suggestion for improvement community facilities",
            "request for additional amenities park",
            "inquiry about service schedules timing",
            "feedback on service quality improvement",
            "request for community event permission",
            "information about waste collection schedule",
            "suggestion for traffic improvement measures",
            "request for additional street furniture",
            "inquiry about building permit process",
            "feedback on municipal website usability",
            "request for community notice board",
            "information about tax payment methods",
            "suggestion for park improvement facilities",
            "request for additional parking spaces",
            "inquiry about service complaint process",
            "feedback on customer service experience",
            "request for community development programs",
            "information about municipal regulations",
            "suggestion for environmental improvement",
            "request for public facility enhancement",
            "inquiry about service availability areas",
            "feedback on municipal communication",
            "request for community safety programs",
            "information about municipal planning",
            "suggestion for service delivery improvement",
            "request for public awareness campaigns",
            "inquiry about municipal budget allocation",
            "feedback on service accessibility",
            "request for community engagement activities",
            "information about municipal policies",
            "suggestion for digital service improvement",
            "request for public consultation meetings",
            "inquiry about service quality standards",
            "feedback on municipal transparency",
            "request for community feedback mechanisms",
            "information about municipal achievements",
            "suggestion for sustainable development",
            "request for public participation opportunities"
        ]
        
        # Create balanced dataset
        for complaint in high_urgency:
            data.append({"text": complaint, "urgency": "High"})
        
        for complaint in medium_urgency:
            data.append({"text": complaint, "urgency": "Medium"})
        
        for complaint in low_urgency:
            data.append({"text": complaint, "urgency": "Low"})
        
        return pd.DataFrame(data)
    
    def train_model(self):
        """Train the urgency prediction model"""
        print("Training Urgency Prediction Model...")
        
        # Get training data
        df = self.get_training_data()
        
        # Preprocess text
        df['processed_text'] = df['text'].apply(self.preprocess_text)
        
        # Create vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        
        # Vectorize text
        X = self.vectorizer.fit_transform(df['processed_text'])
        y = df['urgency']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model with optimized parameters
        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight='balanced',
            max_depth=15,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt'
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Urgency model trained with accuracy: {accuracy:.3f}")
        
        # Save model
        self.save_model()
        
        return accuracy
    
    def save_model(self):
        """Save model and vectorizer to files"""
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(self.vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"Urgency model saved to {self.model_path}")
    
    def load_model(self):
        """Load model and vectorizer from files"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            return True
        except FileNotFoundError:
            print("⚠️ Urgency model not found. Training new model...")
            self.train_model()
            return True
        except Exception as e:
            print(f"❌ Error loading urgency model: {e}")
            return False
    
    def predict_urgency(self, complaint_text, complaint_title="", has_image=False, 
                       near_emergency=False):
        """Predict urgency for a complaint"""
        if not self.model or not self.vectorizer:
            self.load_model()
        
        # Combine title and text
        full_text = f"{complaint_title} {complaint_text}"
        processed_text = self.preprocess_text(full_text)
        
        # Check for emergency keywords
        emergency_keywords = [
            'emergency', 'urgent', 'danger', 'fire', 'accident', 'flood',
            'gas', 'explosion', 'collapse', 'injured', 'bleeding'
        ]
        
        has_emergency_keyword = any(word in processed_text for word in emergency_keywords)
        
        # Vectorize
        X = self.vectorizer.transform([processed_text])
        
        # Predict
        prediction = self.model.predict(X)[0]
        confidence = max(self.model.predict_proba(X)[0])
        
        # Apply business rules
        if has_emergency_keyword or near_emergency:
            prediction = "High"
        elif has_image and prediction == "Low":
            prediction = "Medium"  # Images usually indicate more serious issues
        
        return prediction, confidence

# Global instance
urgency_predictor = UrgencyPredictor()

def predict_urgency(title, description, has_image=False, near_emergency=False):
    """Convenience function to predict urgency"""
    return urgency_predictor.predict_urgency(description, title, has_image, near_emergency)

def train_urgency_model():
    """Train the urgency prediction model"""
    return urgency_predictor.train_model()

if __name__ == "__main__":
    # Train model on first run
    predictor = UrgencyPredictor()
    predictor.train_model()
    
    # Test predictions
    test_cases = [
        "Emergency gas leak help needed",
        "Street light not working",
        "Small pothole on road",
        "Water pipe burst flooding"
    ]
    
    for case in test_cases:
        urgency, conf = predictor.predict_urgency(case)
        print(f"'{case}' -> {urgency} (confidence: {conf:.3f})")