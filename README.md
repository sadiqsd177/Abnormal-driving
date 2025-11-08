# Abnormal Driving Behavior Detection Dashboard

An AI-powered web dashboard for analyzing driving videos and images to detect abnormal behaviors using deep learning and computer vision.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open browser to `http://localhost:5000`

## Features

- **AI-Powered Analysis**: Uses pre-trained deep learning models (driver_model_updated.h5)
- **Dual Input Support**: Analyze both videos (MP4, AVI, MOV, MKV) and images (JPG, PNG)
- **Multi-Behavior Detection** (10 classes):
  - Safe driving
  - Mobile phone usage (texting/calling - left/right hand)
  - Radio/reaching distraction
  - Drinking while driving
  - Grooming (hair/makeup)
  - Talking to passenger
  - General distraction
- **Hybrid Detection**: Combines AI model predictions with MediaPipe computer vision
- **Real-time Analysis**: Instant feedback with confidence scores
- **Risk Assessment**: Automatic risk level classification (Low/Medium/High/Critical)
- **Visual Dashboard**: Grid layout with detailed analysis cards

## Usage

1. Click "Choose File" to select a driving video or image
2. Click "Analyze File" to upload and process
3. View analysis results with detected behaviors, warnings, and confidence scores
4. Review all analyzed files in the dashboard grid

## Model Information

- Primary model: `driver_model_updated.h5` (17.5 MB)
- Fallback model: `driver_model.h5` (228 MB)
- Input: 224x224 RGB images
- Output: Multi-class behavior predictions

## Testing

Test the analyzer:
```bash
python test_analyzer.py
```