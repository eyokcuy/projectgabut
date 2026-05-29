"""
Calibration Tool - Test and Calibrate Gesture Zones
Run this to find optimal gesture thresholds for your setup
"""

import cv2

# Try different MediaPipe import methods for compatibility
try:
    import mediapipe as mp
    hands_module = mp.solutions.hands
    drawing_module = mp.solutions.drawing_utils
    drawing_styles_module = mp.solutions.drawing_styles
except (AttributeError, ImportError):
    try:
        from mediapipe.python.solutions import hands as hands_module
        from mediapipe.python.solutions import drawing_utils as drawing_module
        from mediapipe.python.solutions import drawing_styles as drawing_styles_module
    except ImportError:
        from mediapipe.tasks.python.vision import hand_landmarker
        hands_module = hand_landmarker
        drawing_module = None
        drawing_styles_module = None

from config.settings import (
    GESTURE_UP_THRESHOLD, GESTURE_DOWN_THRESHOLD,
    GESTURE_LEFT_THRESHOLD, GESTURE_RIGHT_THRESHOLD,
    MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE,
    MAX_NUM_HANDS, FRAME_SCALE_PERCENT
)


class CalibrationTool:
    """Gesture zone calibration tool"""
    
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
        self.mp_drawing = solutions.drawing_utils
        self.mp_drawing_styles = solutions.drawing_styles
        
        # Thresholds
        self.up_threshold = GESTURE_UP_THRESHOLD
        self.down_threshold = GESTURE_DOWN_THRESHOLD
        self.left_threshold = GESTURE_LEFT_THRESHOLD
        self.right_threshold = GESTURE_RIGHT_THRESHOLD
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[ERROR] Cannot open webcam")
            exit(1)
    
    def run(self):
        """Main calibration loop"""
        print("\n" + "="*60)
        print("🎮 GESTURE ZONE CALIBRATION TOOL")
        print("="*60)
        print("\nInstructions:")
        print("1. Position your hand in the webcam frame")
        print("2. Check the X, Y values displayed")
        print("3. Adjust thresholds based on your gesture zones")
        print("\nControls:")
        print("  U/D: Adjust UP threshold (currently: {:.2f})".format(self.up_threshold))
        print("  L/R: Adjust LEFT threshold (currently: {:.2f})".format(self.left_threshold))
        print("  [/]: Adjust DOWN threshold (currently: {:.2f})".format(self.down_threshold))
        print("  </> : Adjust RIGHT threshold (currently: {:.2f})".format(self.right_threshold))
        print("  C: Reset to defaults")
        print("  S: Save thresholds to file")
        print("  Q: Quit")
        print("="*60 + "\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize for performance
            frame = self._resize_frame(frame)
            
            # Flip horizontally
            frame = cv2.flip(frame, 1)
            
            # Process hand
            frame = self._process_frame(frame)
            
            # Draw zones
            frame = self._draw_zones(frame)
            
            # Display frame
            cv2.imshow('Calibration Tool', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if not self._handle_key(key):
                break
        
        self.cleanup()
    
    def _resize_frame(self, frame):
        """Resize frame"""
        h, w = frame.shape[:2]
        scale = FRAME_SCALE_PERCENT / 100
        return cv2.resize(frame, (int(w * scale), int(h * scale)))
    
    def _process_frame(self, frame):
        """Detect hand and draw landmarks"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            wrist = hand_landmarks.landmark[0]
            
            # Display coordinates
            h, w, _ = frame.shape
            x_px = int(wrist.x * w)
            y_px = int(wrist.y * h)
            
            # Show X, Y values
            cv2.circle(frame, (x_px, y_px), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"X: {wrist.x:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"Y: {wrist.y:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Draw landmarks
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        
        return frame
    
    def _draw_zones(self, frame):
        """Draw gesture zones on frame"""
        h, w, _ = frame.shape
        
        # UP zone
        up_y = int(self.up_threshold * h)
        cv2.line(frame, (0, up_y), (w, up_y), (255, 0, 0), 2)
        cv2.putText(frame, f"UP ({self.up_threshold:.2f})", (10, up_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 1)
        
        # DOWN zone
        down_y = int(self.down_threshold * h)
        cv2.line(frame, (0, down_y), (w, down_y), (0, 0, 255), 2)
        cv2.putText(frame, f"DOWN ({self.down_threshold:.2f})", (10, down_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        
        # LEFT zone
        left_x = int(self.left_threshold * w)
        cv2.line(frame, (left_x, 0), (left_x, h), (0, 255, 0), 2)
        cv2.putText(frame, f"L ({self.left_threshold:.2f})", (left_x + 5, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        # RIGHT zone
        right_x = int(self.right_threshold * w)
        cv2.line(frame, (right_x, 0), (right_x, h), (255, 255, 0), 2)
        cv2.putText(frame, f"R ({self.right_threshold:.2f})", (right_x - 80, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        
        return frame
    
    def _handle_key(self, key):
        """Handle keyboard input"""
        step = 0.05
        
        if key == ord('q'):
            return False
        elif key == ord('u'):
            self.up_threshold = min(0.5, self.up_threshold + step)
            print(f"UP threshold: {self.up_threshold:.2f}")
        elif key == ord('d'):
            self.up_threshold = max(0.0, self.up_threshold - step)
            print(f"UP threshold: {self.up_threshold:.2f}")
        elif key == ord('l'):
            self.left_threshold = max(0.0, self.left_threshold - step)
            print(f"LEFT threshold: {self.left_threshold:.2f}")
        elif key == ord('r'):
            self.left_threshold = min(0.5, self.left_threshold + step)
            print(f"LEFT threshold: {self.left_threshold:.2f}")
        elif key == ord('['):
            self.down_threshold = min(1.0, self.down_threshold + step)
            print(f"DOWN threshold: {self.down_threshold:.2f}")
        elif key == ord(']'):
            self.down_threshold = max(0.5, self.down_threshold - step)
            print(f"DOWN threshold: {self.down_threshold:.2f}")
        elif key == ord('<'):
            self.right_threshold = min(1.0, self.right_threshold + step)
            print(f"RIGHT threshold: {self.right_threshold:.2f}")
        elif key == ord('>'):
            self.right_threshold = max(0.5, self.right_threshold - step)
            print(f"RIGHT threshold: {self.right_threshold:.2f}")
        elif key == ord('c'):
            self._reset_defaults()
        elif key == ord('s'):
            self._save_thresholds()
        
        return True
    
    def _reset_defaults(self):
        """Reset to default thresholds"""
        self.up_threshold = GESTURE_UP_THRESHOLD
        self.down_threshold = GESTURE_DOWN_THRESHOLD
        self.left_threshold = GESTURE_LEFT_THRESHOLD
        self.right_threshold = GESTURE_RIGHT_THRESHOLD
        print("✓ Reset to defaults")
    
    def _save_thresholds(self):
        """Save thresholds to file"""
        content = f"""# Updated Gesture Thresholds
GESTURE_UP_THRESHOLD = {self.up_threshold}
GESTURE_DOWN_THRESHOLD = {self.down_threshold}
GESTURE_LEFT_THRESHOLD = {self.left_threshold}
GESTURE_RIGHT_THRESHOLD = {self.right_threshold}

# Copy these values to config/settings.py
"""
        with open('calibration_results.txt', 'w') as f:
            f.write(content)
        print(f"✓ Thresholds saved to calibration_results.txt")
        print(content)
    
    def cleanup(self):
        """Clean up resources"""
        self.hands.close()
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    import cv2
    cap = cv2.VideoCapture(0)
    tool = CalibrationTool()
    tool.cap = cap
    tool.run()
