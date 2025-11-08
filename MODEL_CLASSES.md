# Model Class Information

## Correct Class Mapping

The model is trained on the **State Farm Distracted Driver Detection** dataset with 10 classes:

| Class | Label | Description |
|-------|-------|-------------|
| 0 | Safe Driving | Driver is focused on the road |
| 1 | Texting Right | Texting with right hand |
| 2 | Phone Right | Talking on phone with right hand |
| 3 | Texting Left | Texting with left hand |
| 4 | Phone Left | Talking on phone with left hand |
| 5 | Radio | Operating radio/controls |
| 6 | Drinking | Drinking beverage |
| 7 | Reaching Behind | Reaching behind seat |
| 8 | Hair/Makeup | Grooming (hair or makeup) |
| 9 | Talking | Talking to passenger |

## Sample Video Analysis (radio.mp4)

### AI Model Predictions:
```
Class 0 (Safe Driving):     1.36%
Class 1 (Texting Right):    0.04%
Class 2 (Phone Right):      1.83%
Class 3 (Texting Left):     5.39%
Class 4 (Phone Left):       0.76%
Class 5 (Radio):            5.35%
Class 6 (Drinking):         5.58%
Class 7 (Reaching Behind): 37.34% ← HIGHEST
Class 8 (Hair/Makeup):     29.41% ← SECOND
Class 9 (Talking):         12.95%
```

### Interpretation:
- **Primary Detection**: Reaching Behind (37.34%)
  - Driver is reaching for something (likely radio/controls)
- **Secondary Detection**: Hair/Makeup (29.41%)
  - Some grooming/distraction behavior detected

### Combined Output:
- **AI Detection**: Reaching Behind, Hair/Makeup
- **CV Detection**: Radio interaction (31.6%), Distraction (57.9%)
- **Final Behaviors**: Radio Distraction, Distracted Driving, Grooming
- **Risk Level**: High
- **Confidence**: 75%

## Detection Thresholds

- **AI Model**: 25% confidence threshold
- **Computer Vision**: 
  - Phone usage: >10% of frames
  - Radio usage: >15% of frames
  - Distraction: >25% of frames

## Behavior Mapping

### Terminal Output (AI Model):
Shows raw model predictions and detected classes

### Web Interface Output:
Shows combined AI + CV analysis with user-friendly labels:
- "Mobile Phone Usage" (Classes 1-4, 9)
- "Radio Distraction" (Classes 5, 7)
- "Grooming While Driving" (Class 8)
- "Drinking While Driving" (Class 6)
- "Distracted Driving" (General distraction from CV)

## Why Different Outputs?

**Terminal** shows:
- Raw AI predictions
- Individual class detections
- Debug information

**Web Interface** shows:
- Combined AI + CV results
- Grouped behaviors for clarity
- User-friendly descriptions

Both are correct - just different levels of detail!
