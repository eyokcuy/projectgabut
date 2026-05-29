# Configuration Settings for AI Game Controller

# ==================== GESTURE ZONES ====================
# Y-axis thresholds (0.0 to 1.0, where 0 = top, 1 = bottom)
GESTURE_UP_THRESHOLD = 0.40       # Jump gesture (hand in upper zone)
GESTURE_DOWN_THRESHOLD = 0.60     # Roll/slide gesture (hand in lower zone)

# X-axis thresholds (0.0 to 1.0, where 0 = left, 1 = right)
GESTURE_LEFT_THRESHOLD = 0.40     # Move left
GESTURE_RIGHT_THRESHOLD = 0.60    # Move right

# ==================== INPUT SETTINGS ====================
# Debounce/cooldown time in seconds
DEBOUNCE_TIME = 0.4              # Minimum time between key presses (prevents spam)

# Key mappings to keyboard arrow keys
KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'

# ==================== HAND DETECTION ====================
MIN_DETECTION_CONFIDENCE = 0.5    # MediaPipe confidence threshold (0-1)
MIN_TRACKING_CONFIDENCE = 0.5     # MediaPipe tracking confidence (0-1)
MAX_NUM_HANDS = 1                 # Only detect 1 hand

# ==================== PERFORMANCE ====================
FRAME_SCALE_PERCENT = 70          # Resize frame to 70% of original (performance)
TARGET_FPS = 30                   # Target frames per second
FRAME_WIDTH_DISPLAY = 800         # Display window width
FRAME_HEIGHT_DISPLAY = 600        # Display window height

# ==================== SMOOTHING ====================
POSITION_SMOOTHING_ALPHA = 0.6    # Higher = less smoothing, lower = more smoothing (0.0-1.0)
SMOOTHING_BUFFER_SIZE = 5         # Number of frames for moving average

# ==================== UI OVERLAY ====================
SHOW_LANDMARKS = True             # Draw hand landmarks on screen
SHOW_FPS = True                   # Display FPS counter
SHOW_GESTURE_TEXT = True          # Display current gesture
FONT_SIZE = 0.8
FONT_COLOR = (0, 255, 0)          # BGR: Green
FONT_COLOR_GESTURE = (255, 255, 0)  # BGR: Cyan
TEXT_THICKNESS = 2

# ==================== DEBUG ====================
DEBUG_MODE = True                 # Print debug info to console