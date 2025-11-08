import cv2
import numpy as np
import mediapipe as mp
import os
try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

class EnhancedVideoAnalyzer:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        
        # Load pre-trained models if available
        self.driver_model = None
        self.load_models()
    
    def load_models(self):
        """Load pre-trained driver behavior models"""
        if not TF_AVAILABLE:
            print("TensorFlow not available, using basic analysis")
            return
            
        model_paths = ['driver_model.h5', 'driver_model_updated.h5']
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                try:
                    self.driver_model = keras.models.load_model(model_path, compile=False)
                    print(f"[SUCCESS] Loaded model: {model_path}")
                    print(f"  Input shape: {self.driver_model.input_shape}")
                    print(f"  Output shape: {self.driver_model.output_shape}")
                    break
                except Exception as e:
                    print(f"[FAILED] Error loading {model_path}: {str(e)[:100]}")
                    continue
    
    def analyze_video(self, video_path):
        """Enhanced video analysis using both computer vision and deep learning"""
        cap = cv2.VideoCapture(video_path)
        
        # Analysis counters
        total_frames = 0
        phone_frames = 0
        radio_frames = 0
        distracted_frames = 0
        model_predictions = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            total_frames += 1
            
            # Skip frames for performance
            if total_frames % 15 != 0:
                continue
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # MediaPipe analysis
            hand_results = self.hands.process(rgb_frame)
            face_results = self.face_mesh.process(rgb_frame)
            
            # Traditional CV detection
            if self._detect_phone_usage(hand_results, face_results, frame.shape):
                phone_frames += 1
                
            if self._detect_radio_usage(hand_results, frame.shape):
                radio_frames += 1
                
            if self._detect_distraction(face_results):
                distracted_frames += 1
            
            # Deep learning model prediction
            if self.driver_model is not None:
                prediction = self._predict_with_model(frame)
                if prediction is not None:
                    model_predictions.append(prediction)
        
        cap.release()
        
        # Combine traditional CV and ML results
        return self._generate_analysis_result(
            total_frames, phone_frames, radio_frames, 
            distracted_frames, model_predictions
        )
    
    def _predict_with_model(self, frame):
        """Use pre-trained model for prediction"""
        try:
            # Get model input shape
            input_shape = self.driver_model.input_shape
            target_size = (input_shape[1], input_shape[2]) if len(input_shape) == 4 else (224, 224)
            
            # Preprocess frame
            resized = cv2.resize(frame, target_size)
            # Convert BGR to RGB
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            # Normalize to [0, 1]
            normalized = rgb.astype(np.float32) / 255.0
            input_data = np.expand_dims(normalized, axis=0)
            
            # Get prediction
            prediction = self.driver_model.predict(input_data, verbose=0)
            return prediction[0]
            
        except Exception as e:
            print(f"Model prediction error: {e}")
            return None
    
    def _generate_analysis_result(self, total_frames, phone_frames, radio_frames, distracted_frames, model_predictions):
        """Generate comprehensive analysis combining CV and ML results"""
        analyzed_frames = max(1, total_frames // 15)
        
        # Traditional CV percentages
        phone_percentage = (phone_frames / analyzed_frames) * 100
        radio_percentage = (radio_frames / analyzed_frames) * 100
        distraction_percentage = (distracted_frames / analyzed_frames) * 100
        
        # Model-based analysis
        model_confidence = 0
        model_behaviors = []
        
        if model_predictions:
            avg_prediction = np.mean(model_predictions, axis=0)
            model_confidence = np.max(avg_prediction) * 100
            
            # Actual model classes (State Farm dataset)
            behavior_labels = ['Safe Driving', 'Texting Right', 'Phone Right', 'Texting Left', 'Phone Left', 
                             'Radio', 'Drinking', 'Reaching Behind', 'Hair/Makeup', 'Talking']
            
            # Get highest prediction
            max_idx = np.argmax(avg_prediction)
            max_prob = avg_prediction[max_idx]
            
            # If Safe Driving is highest with >50%, consider it safe
            if max_idx == 0 and max_prob > 0.5:
                model_behaviors.append('Safe Driving')
            else:
                # Map predictions to behaviors (skip class 0)
                for i, prob in enumerate(avg_prediction):
                    if i > 0 and i < len(behavior_labels) and prob > 0.35:  # Higher threshold, skip safe driving
                        model_behaviors.append(behavior_labels[i])
            
            print(f"Model predictions: {avg_prediction[:min(len(avg_prediction), 10)]}")
            print(f"Detected behaviors: {model_behaviors}")
        
        # Combine results
        detected_behaviors = []
        warnings = []
        
        # Check if AI model detected safe driving
        ai_safe = 'Safe Driving' in model_behaviors
        
        # Enhanced detection logic (only if not AI safe)
        phone_detected = not ai_safe and (phone_percentage > 10 or any(x in model_behaviors for x in ['Phone Right', 'Phone Left', 'Texting Right', 'Texting Left', 'Talking']))
        radio_detected = not ai_safe and (radio_percentage > 15 or 'Radio' in model_behaviors or 'Reaching Behind' in model_behaviors)
        distraction_detected = not ai_safe and (distraction_percentage > 25 or 'Hair/Makeup' in model_behaviors)
        
        if phone_detected:
            detected_behaviors.append('Mobile Phone Usage')
            warnings.append({
                'type': 'mobile',
                'message': f'ALERT: Mobile phone usage detected (CV: {phone_percentage:.1f}%, AI: {model_confidence:.1f}%)',
                'severity': 'Critical'
            })
            
        if radio_detected:
            detected_behaviors.append('Radio Distraction')
            warnings.append({
                'type': 'radio',
                'message': f'WARNING: Radio interaction detected (CV: {radio_percentage:.1f}%, AI: {model_confidence:.1f}%)',
                'severity': 'Medium'
            })
            
        if distraction_detected:
            detected_behaviors.append('Distracted Driving')
            warnings.append({
                'type': 'distraction',
                'message': f'CAUTION: Driver distraction detected (CV: {distraction_percentage:.1f}%, AI: {model_confidence:.1f}%)',
                'severity': 'High'
            })
        
        # Check for model-specific detections
        if 'Drinking' in model_behaviors:
            detected_behaviors.append('Drinking While Driving')
            warnings.append({
                'type': 'drinking',
                'message': f'DANGER: Drinking detected by AI model (Confidence: {model_confidence:.1f}%)',
                'severity': 'Critical'
            })
            
        if 'Hair/Makeup' in model_behaviors:
            detected_behaviors.append('Grooming While Driving')
            warnings.append({
                'type': 'grooming',
                'message': f'WARNING: Grooming/distraction detected (Confidence: {model_confidence:.1f}%)',
                'severity': 'Medium'
            })
        
        # Default to normal if no issues
        if not detected_behaviors:
            detected_behaviors = ['Normal Driving']
            warnings = [{
                'type': 'normal',
                'message': f'Safe driving detected (AI Confidence: {model_confidence:.1f}%)',
                'severity': 'Low'
            }]
        
        # Determine risk level
        risk_level = 'Low'
        if any(w['severity'] == 'Critical' for w in warnings):
            risk_level = 'Critical'
        elif any(w['severity'] == 'High' for w in warnings):
            risk_level = 'High'
        elif any(w['severity'] == 'Medium' for w in warnings):
            risk_level = 'Medium'
        
        # Enhanced confidence calculation
        final_confidence = max(model_confidence, 75) if model_predictions else min(85, 100 - distraction_percentage)
        
        return {
            'behaviors': detected_behaviors,
            'warnings': warnings,
            'risk_level': risk_level,
            'confidence': round(final_confidence, 1),
            'stats': {
                'phone_usage': round(phone_percentage, 1),
                'radio_usage': round(radio_percentage, 1),
                'distraction': round(distraction_percentage, 1),
                'model_confidence': round(model_confidence, 1),
                'analysis_method': 'AI + Computer Vision' if model_predictions else 'Computer Vision Only'
            }
        }
    
    def analyze_image(self, image_path):
        """Analyze a single image for driving behavior"""
        frame = cv2.imread(image_path)
        if frame is None:
            return {'error': 'Could not read image'}
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # MediaPipe analysis
        hand_results = self.hands.process(rgb_frame)
        face_results = self.face_mesh.process(rgb_frame)
        
        # CV detection
        phone_detected = self._detect_phone_usage(hand_results, face_results, frame.shape)
        radio_detected = self._detect_radio_usage(hand_results, frame.shape)
        distraction_detected = self._detect_distraction(face_results)
        
        # Model prediction
        model_prediction = None
        if self.driver_model is not None:
            model_prediction = self._predict_with_model(frame)
        
        # Generate result
        behaviors = []
        warnings = []
        model_behaviors = []
        model_confidence = 0
        
        if model_prediction is not None:
            model_confidence = np.max(model_prediction) * 100
            behavior_labels = ['Safe Driving', 'Texting Right', 'Phone Right', 'Texting Left', 'Phone Left', 
                             'Radio', 'Drinking', 'Reaching Behind', 'Hair/Makeup', 'Talking']
            
            # Get highest prediction
            max_idx = np.argmax(model_prediction)
            max_prob = model_prediction[max_idx]
            
            # If Safe Driving is highest with >50%, consider it safe
            if max_idx == 0 and max_prob > 0.5:
                model_behaviors.append('Safe Driving')
            else:
                # Map predictions to behaviors (skip class 0)
                for i, prob in enumerate(model_prediction):
                    if i > 0 and i < len(behavior_labels) and prob > 0.35:
                        model_behaviors.append(behavior_labels[i])
        
        # Check if AI model detected safe driving
        ai_safe = 'Safe Driving' in model_behaviors
        
        # Combine detections (only if not AI safe)
        if not ai_safe and (phone_detected or any(x in model_behaviors for x in ['Phone Right', 'Phone Left', 'Texting Right', 'Texting Left', 'Talking'])):
            behaviors.append('Mobile Phone Usage')
            warnings.append({
                'type': 'mobile',
                'message': f'ALERT: Mobile phone usage detected (AI: {model_confidence:.1f}%)',
                'severity': 'Critical'
            })
        
        if not ai_safe and (radio_detected or 'Radio' in model_behaviors or 'Reaching Behind' in model_behaviors):
            behaviors.append('Radio/Reaching Distraction')
            warnings.append({
                'type': 'radio',
                'message': f'WARNING: Radio/reaching interaction detected (AI: {model_confidence:.1f}%)',
                'severity': 'Medium'
            })
        
        if not ai_safe and (distraction_detected or 'Hair/Makeup' in model_behaviors):
            behaviors.append('Grooming Distraction')
            warnings.append({
                'type': 'distraction',
                'message': f'CAUTION: Grooming/distraction detected (AI: {model_confidence:.1f}%)',
                'severity': 'High'
            })
        
        if not ai_safe and 'Drinking' in model_behaviors:
            behaviors.append('Drinking While Driving')
            warnings.append({
                'type': 'drinking',
                'message': f'DANGER: Drinking detected (AI: {model_confidence:.1f}%)',
                'severity': 'Critical'
            })
        
        if not behaviors:
            behaviors = ['Normal Driving']
            warnings = [{
                'type': 'normal',
                'message': f'Safe driving detected (AI: {model_confidence:.1f}%)',
                'severity': 'Low'
            }]
        
        risk_level = 'Low'
        if any(w['severity'] == 'Critical' for w in warnings):
            risk_level = 'Critical'
        elif any(w['severity'] == 'High' for w in warnings):
            risk_level = 'High'
        elif any(w['severity'] == 'Medium' for w in warnings):
            risk_level = 'Medium'
        
        return {
            'behaviors': behaviors,
            'warnings': warnings,
            'risk_level': risk_level,
            'confidence': round(model_confidence if model_prediction is not None else 75, 1),
            'analysis_method': 'AI + Computer Vision' if model_prediction is not None else 'Computer Vision Only'
        }
    
    def _detect_phone_usage(self, hand_results, face_results, frame_shape):
        if not hand_results.multi_hand_landmarks or not face_results.multi_face_landmarks:
            return False
            
        h, w = frame_shape[:2]
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            hand_x = hand_landmarks.landmark[9].x * w
            hand_y = hand_landmarks.landmark[9].y * h
            
            face_landmarks = face_results.multi_face_landmarks[0]
            face_x = face_landmarks.landmark[1].x * w
            face_y = face_landmarks.landmark[1].y * h
            
            distance = np.sqrt((hand_x - face_x)**2 + (hand_y - face_y)**2)
            if distance < w * 0.15:
                return True
        return False
    
    def _detect_radio_usage(self, hand_results, frame_shape):
        if not hand_results.multi_hand_landmarks:
            return False
            
        h, w = frame_shape[:2]
        center_region = (w * 0.3, w * 0.7, h * 0.4, h * 0.8)
        
        for hand_landmarks in hand_results.multi_hand_landmarks:
            hand_x = hand_landmarks.landmark[9].x * w
            hand_y = hand_landmarks.landmark[9].y * h
            
            if (center_region[0] < hand_x < center_region[1] and 
                center_region[2] < hand_y < center_region[3]):
                return True
        return False
    
    def _detect_distraction(self, face_results):
        if not face_results.multi_face_landmarks:
            return True
            
        face_landmarks = face_results.multi_face_landmarks[0]
        nose_tip = face_landmarks.landmark[1]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        
        eye_center_x = (left_eye.x + right_eye.x) / 2
        deviation = abs(nose_tip.x - eye_center_x)
        
        return deviation > 0.05