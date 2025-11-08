# Quick Start Guide

## 🚀 Start the Application

### Option 1: Using Batch File (Easiest)
```
Double-click: run_app.bat
```

### Option 2: Command Line
```bash
cd f:\shammi\Abnormal
myenv\Scripts\python app.py
```

### Option 3: With Activation
```bash
cd f:\shammi\Abnormal
myenv\Scripts\activate
python app.py
```

## 🌐 Access Dashboard

Open your browser and go to:
```
http://localhost:5000
```

## 📤 Upload & Analyze

1. Click "Choose File"
2. Select a video (MP4, AVI, MOV, MKV) or image (JPG, PNG)
3. Click "Analyze File"
4. View results with detected behaviors and risk levels

## 🧪 Run Tests

```bash
# Test with sample video
myenv\Scripts\python test_analyzer.py

# Full system test
myenv\Scripts\python test_full.py

# Model loading test
myenv\Scripts\python test_model_load.py
```

## 📊 Expected Output

### Console Output
```
[SUCCESS] Loaded model: driver_model.h5
  Input shape: (None, 150, 150, 3)
  Output shape: (None, 10)
 * Running on http://127.0.0.1:5000
```

### Dashboard Features
- Total files analyzed
- Normal behavior count
- Mobile usage count
- Critical cases count
- Individual file analysis cards
- Risk level indicators
- Confidence scores

## ⚠️ Troubleshooting

### Model Not Loading
```bash
# Verify TensorFlow installation
myenv\Scripts\python -c "import tensorflow; print(tensorflow.__version__)"
```

### Port Already in Use
```bash
# Change port in app.py (last line):
app.run(debug=True, port=5001)
```

### File Upload Issues
- Check file size < 100MB
- Ensure uploads/ folder exists
- Verify file format is supported

## 📝 Supported Formats

### Videos
- MP4
- AVI
- MOV
- MKV

### Images
- JPG/JPEG
- PNG
- BMP

## 🎯 Detection Capabilities

The system detects:
1. ✅ Normal Driving
2. 📱 Mobile Phone Usage
3. 📻 Radio Distraction
4. 👀 General Distraction
5. 😴 Drowsy Driving
6. 🚗 Aggressive Driving
7. 🥤 Drinking
8. 🍔 Eating
9. 💬 Texting
10. 📞 Talking

## 💡 Tips

- Use good quality videos with clear view of driver
- Ensure proper lighting in videos/images
- Videos are analyzed every 15th frame for performance
- AI model provides 10-class behavior detection
- Computer vision provides backup detection

## 🆘 Need Help?

Check these files:
- `PROJECT_STATUS.md` - Full project status
- `README.md` - Detailed documentation
- `CHANGES.md` - Recent changes
