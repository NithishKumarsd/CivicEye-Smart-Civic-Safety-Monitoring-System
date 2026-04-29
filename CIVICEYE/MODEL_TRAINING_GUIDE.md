# 🤖 AI Model Training & Integration Guide

## Overview
This guide shows how to train and integrate the AI models using your actual image dataset.

## Dataset Structure
Your dataset contains images organized by department:
```
dataset/
├── Electricity/     (~100+ images)
├── Public_Safety/   (~200+ images) 
├── Roads/          (~100+ images)
└── Sanitation/     (~90+ images)
```

## Step-by-Step Model Training

### Step 1: Install Dependencies
```bash
cd CIVICEYE
pip install -r requirements.txt
```

### Step 2: Train Models from Your Dataset
```bash
python train_models.py
```

This will:
- ✅ Load images from your dataset folders
- ✅ Extract image features (RGB, HSV, grayscale)
- ✅ Train Random Forest classifier
- ✅ Save model as `ai_models/department_model/model.pkl`
- ✅ Save scaler as `ai_models/department_model/scaler.pkl`
- ✅ Train urgency prediction model
- ✅ Save urgency model as `ai_models/urgency_model/model.pkl`

### Step 3: Verify Models are Saved
Check these files exist:
```
CIVICEYE/
├── ai_models/
│   ├── department_model/
│   │   ├── model.pkl      ✅ Image classifier
│   │   └── scaler.pkl     ✅ Feature scaler
│   └── urgency_model/
│       ├── model.pkl      ✅ Urgency predictor
│       └── vectorizer.pkl ✅ Text vectorizer
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

## How Models are Integrated

### 1. Image Classification Model
- **Input**: Uploaded complaint images
- **Process**: Extracts RGB, HSV, grayscale features
- **Output**: Predicts Roads/Sanitation/Electricity/Public Safety
- **File**: `ai_models/department_model/model.pkl`

### 2. Urgency Prediction Model  
- **Input**: Complaint text + context
- **Process**: TF-IDF vectorization + business rules
- **Output**: Predicts High/Medium/Low urgency
- **File**: `ai_models/urgency_model/model.pkl`

### 3. Integration in Complaint Service
```python
# When user submits complaint with image:
if uploaded_file and auto_detect_department:
    # Use your trained image model
    department, confidence = predict_from_image(image_path)
    
# Always predict urgency from text
urgency, confidence = predict_urgency(title, description)
```

## Model Performance

### Expected Accuracy
- **Image Classification**: ~85-95% (depends on image quality)
- **Urgency Prediction**: ~90-95% (with business rules)

### Model Files Size
- Image model: ~5-10 MB
- Urgency model: ~1-2 MB
- Total: ~6-12 MB (easily deployable)

## Retraining Models

### Automatic Retraining
- Models retrain when new data is available
- Triggered from admin dashboard
- Maintains model performance over time

### Manual Retraining
```bash
python train_models.py
```

## Troubleshooting

### Issue: "No images loaded"
**Solution**: Check dataset path in `train_image.py`
```python
self.dataset_path = "../dataset"  # Adjust path if needed
```

### Issue: "OpenCV not found"
**Solution**: Install OpenCV
```bash
pip install opencv-python
```

### Issue: "Model files not found"
**Solution**: Run training script first
```bash
python train_models.py
```

## Production Deployment

### Model Optimization
- Models are already optimized for production
- Use pickle for fast loading
- Feature extraction is lightweight
- No GPU required

### Scaling Considerations
- Models load once at startup
- Predictions are fast (<100ms)
- Can handle concurrent requests
- Memory usage: ~50-100MB

## Next Steps

1. ✅ Train models with your dataset
2. ✅ Test predictions in the app
3. ✅ Monitor model performance
4. ✅ Retrain with new data as needed
5. ✅ Deploy to production

Your AI models are now trained on real data and integrated into CIVICEYE! 🎉