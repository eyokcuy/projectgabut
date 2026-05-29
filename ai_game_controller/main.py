"""
AI Webcam Game Controller - Main Application
Controls Subway Surfers using hand gestures
"""

import cv2
import sys
from gesture_detector import GestureDetector
from input_controller import InputController
from ui_renderer import UIRenderer
from config.settings import (
    FRAME_SCALE_PERCENT, TARGET_FPS, SHOW_LANDMARKS, DEBUG_MODE
)


class GameController:
    """
    Main game controller application
    Manages gesture detection, input, and rendering
    """ 
    
    def __init__(self):
        print("[INIT] Webcam Game Controller...")
        
        # Initialize components
        self.gesture_detector = GestureDetector()
        self.input_controller = InputController()
        self.ui_renderer = UIRenderer()
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[ERROR] Cannot open webcam")
            sys.exit(1)
        
        print("[INIT] Webcam initialized")
        print("[INIT] Components loaded successfully")
        print("\n" + "="*60)
        print("Cam Controller")
        print("="*60)
        print("Controls:")
        print("  - UP gesture:    Jump")
        print("  - DOWN gesture:  Roll/Slide")
        print("  - LEFT gesture:  Move Left")
        print("  - RIGHT gesture: Move Right")
        print("\nKeyboard:")
        print("  - SPACE:  Toggle input ON/OFF")
        print("  - T:      Toggle hand landmarks display")
        print("  - Q:      Quit")
        print("="*60 + "\n")
        
        # State variables
        self.running = True
        self.show_landmarks = SHOW_LANDMARKS
        self.frame_count = 0
    
    def run(self):
        """Main application loop"""
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("[ERROR] Failed to read frame from webcam")
                    break
                
                # Flip horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Resize for performance
                frame = self._resize_frame(frame)
                
                # Process hand gestures
                frame, gesture, hand_detected, wrist_pos = self.gesture_detector.process_frame(frame)
                
                # Handle gesture input
                self.input_controller.handle_gesture(gesture)
                
                # Render UI overlay
                frame = self.ui_renderer.render_overlay(
                    frame,
                    gesture,
                    hand_detected,
                    self.input_controller.is_enabled()
                )
                
                # Display frame
                cv2.imshow('AI Game Controller - Subway Surfers', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                self._handle_keyboard(key)
                
                self.frame_count += 1
                
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.cleanup()
    
    def _resize_frame(self, frame):
        """
        Resize frame while maintaining aspect ratio
        
        Args:
            frame: Input frame
            
        Returns:
            frame: Resized frame
        """
        h, w = frame.shape[:2]
        scale = FRAME_SCALE_PERCENT / 100
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(frame, (new_w, new_h))
    
    def _handle_keyboard(self, key):
        """
        Handle keyboard input
        
        Args:
            key: Key code from cv2.waitKey
        """
        if key == ord('q'):  # Quit
            print("[INFO] Quitting...")
            self.running = False
        
        elif key == ord(' '):  # Space - toggle input
            self.input_controller.toggle_active()
        
        elif key == ord('t'):  # T - toggle landmarks
            self.show_landmarks = not self.show_landmarks
            status = "ON" if self.show_landmarks else "OFF"
            print(f"[UI] Hand landmarks: {status}")
        
        elif key == ord('r'):  # R - reset cooldowns
            self.input_controller.reset_cooldowns()
            print("[INFO] Cooldowns reset")
    
    def cleanup(self):
        """Clean up resources"""
        print("[CLEANUP] Releasing resources...")
        self.gesture_detector.close()
        self.cap.release()
        cv2.destroyAllWindows()
        print("[CLEANUP] Done. Goodbye!")


def main():
    """Entry point"""
    controller = GameController()
    controller.run()


if __name__ == "__main__":
    main()
