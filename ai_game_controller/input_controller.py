"""
Input Controller Module
Handles keyboard input simulation with debounce protection
"""

import pyautogui
import time
from config.settings import (
    DEBOUNCE_TIME, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, DEBUG_MODE
)


class InputController:
    """
    Manages keyboard input with debounce/cooldown protection
    """
    
    def __init__(self):
        # Safety settings for pyautogui
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.01      # Small pause between actions
        
        # Debounce tracking
        self.last_gesture = "NONE"
        self.last_press_time = {}
        self.debounce_time = DEBOUNCE_TIME
        
        # Initialize last press times for all keys
        for key in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
            self.last_press_time[key] = 0
        
        self.is_active = True
        
    def handle_gesture(self, gesture):
        """
        Convert gesture to keyboard input with debounce
        
        Args:
            gesture (str): Gesture name (UP, DOWN, LEFT, RIGHT, NONE)
        """
        if not self.is_active or gesture == "NONE":
            return
        
        current_time = time.time()
        
        # Map gesture to key
        key_map = {
            "UP": KEY_UP,
            "DOWN": KEY_DOWN,
            "LEFT": KEY_LEFT,
            "RIGHT": KEY_RIGHT
        }
        
        if gesture not in key_map:
            return
        
        key = key_map[gesture]
        
        # Check debounce
        if current_time - self.last_press_time[key] >= self.debounce_time:
            self._press_key(key)
            self.last_press_time[key] = current_time
            
            if DEBUG_MODE:
                print(f"[INPUT] Pressing: {gesture} ({key})")
    
    def _press_key(self, key):
        """
        Press a key using pyautogui
        
        Args:
            key (str): Key name (up, down, left, right)
        """
        try:
            pyautogui.press(key)
        except Exception as e:
            print(f"[ERROR] Failed to press key '{key}': {e}")
    
    def toggle_active(self):
        """Toggle input on/off"""
        self.is_active = not self.is_active
        status = "ENABLED" if self.is_active else "DISABLED"
        print(f"[INPUT] Control {status}")
    
    def set_active(self, state):
        """Set active state"""
        self.is_active = state
    
    def is_enabled(self):
        """Check if input controller is active"""
        return self.is_active
    
    def reset_cooldowns(self):
        """Reset all cooldown timers (useful for stopping spam)"""
        current_time = time.time()
        for key in self.last_press_time:
            self.last_press_time[key] = current_time - self.debounce_time
