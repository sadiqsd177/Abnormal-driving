import os
import cv2
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from tensorflow import keras

# Load model
model = keras.models.load_model('driver_model.h5', compile=False)
print(f"Model output shape: {model.output_shape}")
print(f"Number of classes: {model.output_shape[-1]}")

# Test with sample video frame
video_path = 'uploads/radio.mp4'
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if ret:
    # Preprocess
    resized = cv2.resize(frame, (150, 150))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    normalized = rgb.astype(np.float32) / 255.0
    input_data = np.expand_dims(normalized, axis=0)
    
    # Predict
    prediction = model.predict(input_data, verbose=0)[0]
    
    print("\n=== Prediction Analysis ===")
    for i, prob in enumerate(prediction):
        print(f"Class {i}: {prob:.4f} ({prob*100:.2f}%)")
    
    print(f"\nHighest probability: Class {np.argmax(prediction)} = {np.max(prediction)*100:.2f}%")
    
    # Common class mappings to try
    print("\n=== Possible Class Mappings ===")
    
    mappings = [
        ['safe_driving', 'texting_right', 'phone_right', 'texting_left', 'phone_left', 
         'radio', 'drinking', 'reaching_behind', 'hair_makeup', 'talking'],
        ['Normal', 'Phone_Right', 'Phone_Left', 'Texting_Right', 'Texting_Left',
         'Radio', 'Drinking', 'Reaching', 'Hair', 'Talking'],
        ['c0_safe', 'c1_texting_right', 'c2_phone_right', 'c3_texting_left', 'c4_phone_left',
         'c5_radio', 'c6_drinking', 'c7_reaching', 'c8_hair', 'c9_talking']
    ]
    
    for idx, mapping in enumerate(mappings):
        print(f"\nMapping {idx+1}:")
        sorted_indices = np.argsort(prediction)[::-1][:3]
        for i in sorted_indices:
            if i < len(mapping):
                print(f"  {mapping[i]}: {prediction[i]*100:.2f}%")
