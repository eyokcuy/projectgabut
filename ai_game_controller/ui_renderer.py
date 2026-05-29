"""
UI Overlay Module
Displays gesture information and performance metrics on video frame
"""

import cv2
import time
from config.settings import (
    SHOW_LANDMARKS, SHOW_FPS, SHOW_GESTURE_TEXT,
    FONT_SIZE, FONT_COLOR, FONT_COLOR_GESTURE, TEXT_THICKNESS
)


class UIRenderer:
    """
    Renders UI overlays on video frames
    """
    
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_size = FONT_SIZE
        self.font_color = FONT_COLOR
        self.font_color_gesture = FONT_COLOR_GESTURE
        self.thickness = TEXT_THICKNESS
        
        # FPS calculation
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        self.current_fps = 0
    
    def render_overlay(self, frame, gesture, hand_detected, input_active):
        """
        Render all UI overlays on frame
        
        Args:
            frame: Input video frame
            gesture (str): Current detected gesture
            hand_detected (bool): Whether hand is detected
            input_active (bool): Whether input control is active
            
        Returns:
            frame: Frame with overlays rendered
        """
        # Update FPS
        self._update_fps()
        
        # Render gesture text
        if SHOW_GESTURE_TEXT:
            self._render_gesture_text(frame, gesture, hand_detected)
        
        # Render FPS
        if SHOW_FPS:
            self._render_fps(frame)
        
        # Render input status
        self._render_input_status(frame, input_active)
        
        # Render instructions
        self._render_instructions(frame)
        
        return frame
    
    def _render_gesture_text(self, frame, gesture, hand_detected):
        """Render current gesture text"""
        h, w, _ = frame.shape
        
        if hand_detected:
            gesture_text = f"Gesture: {gesture}"
            color = self.font_color_gesture
        else:
            gesture_text = "No Hand Detected"
            color = (0, 0, 255)  # Red
        
        # Position at top-center
        text_size = cv2.getTextSize(gesture_text, self.font, self.font_size, self.thickness)[0]
        x = (w - text_size[0]) // 2
        y = 40
        
        # Draw background
        cv2.rectangle(frame, (x - 10, y - 25), (x + text_size[0] + 10, y + 5), (0, 0, 0), -1)
        cv2.rectangle(frame, (x - 10, y - 25), (x + text_size[0] + 10, y + 5), color, 2)
        
        # Draw text
        cv2.putText(frame, gesture_text, (x, y), self.font, self.font_size, color, self.thickness)
    
    def _render_fps(self, frame):
        """Render FPS counter"""
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(frame, fps_text, (10, 30), self.font, self.font_size, self.font_color, self.thickness)
    
    def _render_input_status(self, frame, input_active):
        """Render input controller status"""
        h, w, _ = frame.shape
        
        status_text = "INPUT: ON" if input_active else "INPUT: OFF"
        status_color = (0, 255, 0) if input_active else (0, 0, 255)  # Green or Red
        
        cv2.putText(frame, status_text, (10, h - 20), self.font, self.font_size, status_color, self.thickness)
    
    def _render_instructions(self, frame):
        """Render control instructions"""
        h, w, _ = frame.shape
        
        instructions = [
            "SPACE: Toggle Input ON/OFF",
            "Q: Quit",
            "T: Toggle Landmarks"
        ]
        
        y_offset = h - 60
        for instruction in instructions:
            cv2.putText(frame, instruction, (10, y_offset), self.font, 0.5, self.font_color, 1)
            y_offset += 20
    
    def _update_fps(self):
        """Update FPS calculation"""
        self.fps_frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.fps_start_time
        
        if elapsed_time >= 1.0:  # Update every second
            self.current_fps = self.fps_frame_count / elapsed_time
            self.fps_frame_count = 0
            self.fps_start_time = current_time
