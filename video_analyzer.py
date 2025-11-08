import cv2
import mediapipe as mp
import numpy as np
import os
import numpy as np
import os

class VideoAnalyzer:
    def __init__(self):
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
    
    def analyze_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Analysis counters
        total_frames = 0
        phone_frames = 0
        radio_frames = 0
        distracted_frames = 0
        face_detected_frames = 0
        hand_detected_frames = 0
        
        behaviors = []
        warnings = []
        
        # Analyze every 5th frame for better accuracy
        frame_skip = max(5, fps // 6)  # Analyze ~6 frames per second
        analyzed_frames = 0  # explicit counter for processed frames
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            total_frames += 1
            
            # Skip frames for performance
            if total_frames % frame_skip != 0:
                continue
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect hands (phone/radio usage)
            hand_results = self.hands.process(rgb_frame)
            face_results = self.face_mesh.process(rgb_frame)
            
            # Track detection success
            if face_results.multi_face_landmarks:
                face_detected_frames += 1
            if hand_results.multi_hand_landmarks:
                hand_detected_frames += 1
            
            # Count this as an analyzed frame
            analyzed_frames += 1

            # Check for phone usage (hand near face/ear)
            if self._detect_phone_usage(hand_results, face_results, frame.shape):
                phone_frames += 1
                
            # Check for radio usage (hand movements in center/dashboard area)
            if self._detect_radio_usage(hand_results, frame.shape):
                radio_frames += 1
                
            # Check for general distraction (face not forward)
            if self._detect_distraction(face_results):
                distracted_frames += 1
        
        cap.release()
        
        # Calculate percentages
        if analyzed_frames == 0:
            return self._default_analysis()

        # Calculate detection rates
        phone_percentage = (phone_frames / analyzed_frames) * 100
        radio_percentage = (radio_frames / analyzed_frames) * 100
        distraction_percentage = (distracted_frames / analyzed_frames) * 100
        face_detection_rate = (face_detected_frames / analyzed_frames) * 100
        hand_detection_rate = (hand_detected_frames / analyzed_frames) * 100
        
        # Determine behaviors based on thresholds (adjusted for better detection)
        if phone_percentage > 5:  # Lowered threshold for mobile detection
            behaviors.append('Mobile Phone Usage')
            warnings.append({
                'type': 'mobile',
                'message': f'⚠️ ALERT: Mobile phone usage detected in {phone_percentage:.1f}% of video. Avoid using mobile while driving!',
                'severity': 'Critical'
            })

        # Increase radio threshold to avoid spurious warnings when brief hand movements occur
        if radio_percentage > 20:  # Raised threshold for radio detection
            behaviors.append('Radio Distraction')
            warnings.append({
                'type': 'radio',
                'message': f'🔊 WARNING: Radio/dashboard interaction detected in {radio_percentage:.1f}% of video. Keep hands on wheel!',
                'severity': 'Medium'
            })

        # Require a larger sustained distraction percentage to trigger warning
        if distraction_percentage > 30 and face_detection_rate > 30:  # Raised threshold for distraction
            behaviors.append('Distracted Driving')
            warnings.append({
                'type': 'distraction',
                'message': f'👀 CAUTION: Driver looking away detected in {distraction_percentage:.1f}% of video. Stay focused on road!',
                'severity': 'High'
            })
        
        # Check if driver is not visible
        if face_detection_rate < 30:
            behaviors.append('Driver Not Visible')
            warnings.append({
                'type': 'visibility',
                'message': f'⚠️ WARNING: Driver face not clearly visible in video. Ensure proper camera angle.',
                'severity': 'Medium'
            })
        
        # Default to normal if no issues
        if not behaviors:
            behaviors = ['Normal Driving']
            warnings = [{
                'type': 'normal',
                'message': f'✅ Safe driving behavior detected. Driver focused on road. (Face detected: {face_detection_rate:.0f}%)',
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
        
        # Calculate confidence based on detection quality
        base_confidence = 70 + (face_detection_rate * 0.25)
        confidence = min(95, max(60, base_confidence - (distraction_percentage * 0.3)))
        
        return {
            'behaviors': behaviors,
            'warnings': warnings,
            'risk_level': risk_level,
            'confidence': round(confidence, 1),
            'stats': {
                'phone_usage': round(phone_percentage, 1),
                'radio_usage': round(radio_percentage, 1),
                'distraction': round(distraction_percentage, 1),
                'face_detection': round(face_detection_rate, 1),
                'hand_detection': round(hand_detection_rate, 1),
                'frames_analyzed': analyzed_frames,
                'total_frames': total_video_frames
            }
        }
    
    def _detect_phone_usage(self, hand_results, face_results, frame_shape):
        if not hand_results.multi_hand_landmarks or not face_results.multi_face_landmarks:
            return False

        h, w = frame_shape[:2]
        face_landmarks = face_results.multi_face_landmarks[0]

        # Get ear and mouth landmarks for more specific phone detection
        left_ear = face_landmarks.landmark[234]   # Left ear
        right_ear = face_landmarks.landmark[454]  # Right ear
        mouth_left = face_landmarks.landmark[61]  # Left mouth corner
        mouth_right = face_landmarks.landmark[291] # Right mouth corner

        ear_mouth_points = [
            (left_ear.x * w, left_ear.y * h),
            (right_ear.x * w, right_ear.y * h),
            (mouth_left.x * w, mouth_left.y * h),
            (mouth_right.x * w, mouth_right.y * h)
        ]

        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Get hand position (use index finger tip for more precision)
            hand_x = hand_landmarks.landmark[8].x * w  # Index finger tip
            hand_y = hand_landmarks.landmark[8].y * h

            # Check if hand is near ear or mouth (phone usage pattern)
            for point_x, point_y in ear_mouth_points:
                distance = np.sqrt((hand_x - point_x)**2 + (hand_y - point_y)**2)
                if distance < w * 0.08:  # Within 8% of frame width of ear/mouth
                    return True
        return False
    
    def _detect_radio_usage(self, hand_results, frame_shape):
        if not hand_results.multi_hand_landmarks:
            return False

        h, w = frame_shape[:2]
        # Focus on right/center dashboard area, exclude left side (mirror area)
        # Narrower region: center-lower dashboard to reduce false positives
        radio_region = (w * 0.45, w * 0.75, h * 0.55, h * 0.85)  # Right-center dashboard

        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Use index-middle base (landmark 9) for a reliable central hand point
            hand_x = hand_landmarks.landmark[9].x * w
            hand_y = hand_landmarks.landmark[9].y * h

            # Check if hand is in right/center dashboard region (radio controls)
            if (radio_region[0] < hand_x < radio_region[1] and
                radio_region[2] < hand_y < radio_region[3]):
                return True
        return False
    
    def _detect_distraction(self, face_results):
        # If no face landmarks available, do NOT count as distracted here.
        # Missing face is handled separately via face_detection_rate.
        if not face_results.multi_face_landmarks:
            return False
        face_landmarks = face_results.multi_face_landmarks[0]

        # Check head pose using nose and eye landmarks
        nose_tip = face_landmarks.landmark[1]
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]

        # Calculate if face is looking forward (normalized by inter-ocular distance)
        eye_center_x = (left_eye.x + right_eye.x) / 2
        deviation = abs(nose_tip.x - eye_center_x)

        # Normalize deviation by interocular distance to account for camera placement
        interocular = abs(left_eye.x - right_eye.x)
        if interocular <= 0.001:
            # Fallback to raw threshold if landmarks are unreliable
            return deviation > 0.08

        deviation_norm = deviation / interocular

        # Use a normalized threshold (tunable). This reduces false positives
        # caused by camera angle or mirror reflections. Raised slightly.
        return deviation_norm > 0.28
    
    def _default_analysis(self):
        return {
            'behaviors': ['Analysis Failed'],
            'warnings': [{
                'type': 'error',
                'message': '❌ Could not analyze video. Please ensure good lighting and clear view of driver.',
                'severity': 'Medium'
            }],
            'risk_level': 'Medium',
            'confidence': 50.0,
            'stats': {'phone_usage': 0, 'radio_usage': 0, 'distraction': 0}
        }