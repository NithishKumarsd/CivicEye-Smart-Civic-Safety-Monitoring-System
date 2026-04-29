"""
Ultimate Department Model - Clean Version for 75%+ Accuracy
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
import cv2

class UltimateDepartmentClassifier:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = "ai_models/department_model/model.pkl"
        self.scaler_path = "ai_models/department_model/scaler.pkl"
        self.dataset_path = "../dataset"
        self.image_size = (64, 64)
        self.ensure_model_dir()
    
    def ensure_model_dir(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def extract_features(self, image_path):
        """Extract comprehensive features for department classification"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            img = cv2.resize(img, self.image_size)
            features = []
            
            # Color spaces
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 1. RGB statistics
            for channel in cv2.split(img):
                features.extend([
                    channel.mean(), channel.std(),
                    np.percentile(channel, 25), np.percentile(channel, 75)
                ])
            
            # 2. HSV features
            features.extend([
                hsv[:,:,0].mean(), hsv[:,:,1].mean(), hsv[:,:,2].mean(),
                hsv[:,:,1].std()
            ])
            
            # 3. Texture features
            kernel = np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]])
            lbp = cv2.filter2D(gray, -1, kernel)
            features.extend([lbp.mean(), lbp.std()])
            
            # 4. Edge features
            edges = cv2.Canny(gray, 50, 150)
            features.extend([
                edges.mean(), edges.std(),
                np.sum(edges > 0) / edges.size
            ])
            
            # 5. Contour features
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 10]
                if areas:
                    features.extend([len(areas), np.mean(areas), max(areas)])
                else:
                    features.extend([0, 0, 0])
            else:
                features.extend([0, 0, 0])
            
            # 6. Brightness features
            features.extend([
                gray.mean(), gray.std(),
                gray.max() - gray.min()
            ])
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def load_dataset(self):
        """Load and augment dataset"""
        print("Loading dataset...")
        
        X, y = [], []
        
        dept_mapping = {
            'Electricity': 'Electricity',
            'Public_Safety': 'Public Safety', 
            'Roads': 'Roads',
            'Sanitation': 'Sanitation'
        }
        
        for folder_name, dept_name in dept_mapping.items():
            folder_path = os.path.join(self.dataset_path, folder_name)
            
            if not os.path.exists(folder_path):
                continue
            
            print(f"Processing {folder_name}...")
            
            image_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.avif'))]
            
            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                features = self.extract_features(image_path)
                
                if features is not None:
                    X.append(features)
                    y.append(dept_name)
        
        X, y = np.array(X), np.array(y)
        
        # Data augmentation - add noise
        X_aug, y_aug = [], []
        for i in range(len(X)):
            X_aug.append(X[i])
            y_aug.append(y[i])
            
            # Add noisy version
            noise = np.random.normal(0, 0.02, X[i].shape)
            X_aug.append(X[i] + noise)
            y_aug.append(y[i])
        
        print(f"Dataset: {len(X_aug)} samples (with augmentation)")
        return np.array(X_aug), np.array(y_aug)
    
    def train_model(self):
        """Train optimized model"""
        print("Training Ultimate Department Model...")
        
        X, y = self.load_dataset()
        
        if len(X) == 0:
            return False
        
        # Preprocessing
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Optimized Random Forest
        self.model = RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            random_state=42,
            class_weight='balanced',
            bootstrap=True,
            oob_score=True
        )
        
        print("Training model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.3f}")
        print(f"OOB Score: {self.model.oob_score_:.3f}")
        print("\\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.save_model()
        return accuracy
    
    def save_model(self):
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            return True
        except FileNotFoundError:
            return self.train_model()
    
    def predict_department_from_image(self, image_path):
        if not self.model:
            self.load_model()
        
        features = self.extract_features(image_path)
        if features is None:
            return None, 0.0
        
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict(features_scaled)[0]
        confidence = max(self.model.predict_proba(features_scaled)[0])
        
        return prediction, confidence

# Global instance
ultimate_classifier = UltimateDepartmentClassifier()

def train_ultimate_model():
    return ultimate_classifier.train_model()

def predict_from_ultimate_image(image_path):
    return ultimate_classifier.predict_department_from_image(image_path)

if __name__ == "__main__":
    classifier = UltimateDepartmentClassifier()
    accuracy = classifier.train_model()
    print(f"Final accuracy: {accuracy:.1%}")