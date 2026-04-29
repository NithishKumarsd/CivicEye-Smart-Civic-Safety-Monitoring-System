"""
CIVICEYE Model Training Script
Trains both image classification and text-based models
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_models.department_model.train_clean import train_ultimate_model
from ai_models.urgency_model.train import train_urgency_model

def main():
    """Train all AI models"""
    print("CIVICEYE AI Model Training")
    print("=" * 50)
    
    # Train image classification model
    print("\n1. Training Image Department Classification Model")
    print("-" * 50)
    try:
        accuracy = train_ultimate_model()
        if accuracy:
            print(f"Image model training completed with {accuracy:.1%} accuracy")
        else:
            print("Image model training failed")
    except Exception as e:
        print(f"Error training image model: {e}")
    
    # Train urgency prediction model  
    print("\n2. Training Urgency Prediction Model")
    print("-" * 50)
    try:
        accuracy = train_urgency_model()
        print(f"Urgency model training completed with {accuracy:.1%} accuracy")
    except Exception as e:
        print(f"Error training urgency model: {e}")
    
    print("\nModel training completed!")
    print("Models saved as .pkl files and ready for use.")

if __name__ == "__main__":
    main()