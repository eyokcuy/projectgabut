"""
Advanced Configuration Guide
For fine-tuning the AI Game Controller
"""

# ============================================================================

# GESTURE ZONE CALIBRATION

# ============================================================================

"""
The gesture zones are defined by normalized coordinates (0.0 to 1.0):

- (0, 0) = top-left
- (1, 1) = bottom-right
- X = 0.5 = horizontal center
- Y = 0.5 = vertical center

Default Zones:
┌─────────────────────┐
│ UP ZONE │ Y < 0.25
│ (Jump) │
├─────────────────────┤
│ L │Center│ R │
│ E │ │ I │ 0.25 < Y < 0.75
│ F │(None)│ G │ X < 0.3 or X > 0.7
│ T │ │ H │
│ │ │ T │
├─────────────────────┤
│ DOWN ZONE │ Y > 0.75
│ (Roll/Slide) │
└─────────────────────┘

To calibrate:

1. Run main.py
2. Move hand and note X, Y values in debug output (DEBUG_MODE = True)
3. Adjust thresholds based on your camera setup
   """

# ============================================================================

# HAND DETECTION TUNING

# ============================================================================

"""
MIN_DETECTION_CONFIDENCE (0.0 to 1.0)

- Default: 0.7
- Higher values: More strict, fewer false positives but misses weak detections
- Lower values: More lenient, catches more hands but more false positives
- Range: 0.5 (very lenient) to 0.95 (very strict)

MIN_TRACKING_CONFIDENCE (0.0 to 1.0)

- Default: 0.7
- Higher: More stable tracking but drops hand more often
- Lower: Tracks through partial occlusions but more jittery
- Range: 0.5 to 0.95

Recommendation:

- Indoor, good lighting: 0.7-0.75
- Poor lighting: 0.5-0.6
- Very clean background: 0.8-0.85
  """

# ============================================================================

# SMOOTHING & STABILITY

# ============================================================================

"""
POSITION_SMOOTHING_ALPHA (0.0 to 1.0)

- Default: 0.6
- Higher (0.8-1.0): Less smoothing, more responsive but jittery
- Lower (0.3-0.5): More smoothing, stable but delayed response
- Best for Subway Surfers: 0.6-0.7 (balance of response and stability)

SMOOTHING_BUFFER_SIZE (integer)

- Default: 5 frames
- Higher (7-10): Very smooth but delayed
- Lower (2-3): Responsive but jittery
- Formula: Delay ≈ buffer_size / FPS seconds
- With 5 frames at 30 FPS = ~166ms delay
  """

# ============================================================================

# INPUT RESPONSE TUNING

# ============================================================================

"""
DEBOUNCE_TIME (in seconds)

- Default: 0.4 seconds
- Lower (0.2): Quick, rapid moves but risk of double input
- Higher (0.6): Prevents spam but slower response
- Best for games: 0.3-0.5 seconds

Example debounce times:

- Fast-paced: 0.2-0.3 seconds
- Balanced: 0.4-0.5 seconds
- Deliberate moves: 0.6+ seconds
  """

# ============================================================================

# PERFORMANCE OPTIMIZATION

# ============================================================================

"""
FRAME_SCALE_PERCENT (1-100)

- Default: 70%
- Higher (80-100): Better accuracy but slower FPS
- Lower (40-60): Faster but less accurate
- PC Performance impact: Lower % = Higher FPS

Target FPS calculation:

- Original: 1920x1080 @ 30 FPS
- 70%: 1344x756 @ 40+ FPS
- 50%: 960x540 @ 60+ FPS
- 30%: 576x324 @ 80+ FPS

Recommendation:

- High-end PC: 80-100%
- Mid-range: 60-75%
- Low-end: 40-50%
  """

# ============================================================================

# GAME-SPECIFIC TUNING

# ============================================================================

"""
SUBWAY SURFERS SPECIFICS:

For Faster Gameplay:

- Decrease DEBOUNCE_TIME to 0.25-0.3
- Increase POSITION_SMOOTHING_ALPHA to 0.75-0.8
- Reduce SMOOTHING_BUFFER_SIZE to 3

For Precision Mode:

- Increase DEBOUNCE_TIME to 0.5-0.6
- Decrease POSITION_SMOOTHING_ALPHA to 0.4-0.5
- Increase SMOOTHING_BUFFER_SIZE to 7-8

For Consistent Play:

- Use balanced defaults
- Focus on clear, deliberate hand movements
- Maintain good camera distance (1-2 meters)
  """

# ============================================================================

# TESTING CONFIGURATIONS

# ============================================================================

"""

1. SENSITIVITY TEST
   - Slightly increase thresholds
   - Check if all gestures are recognized
   - Adjust if some gestures feel unresponsive

2. JITTER TEST
   - Raise hand and hold steady
   - If gesture changes rapidly, increase smoothing:
     - Increase SMOOTHING_BUFFER_SIZE
     - Decrease POSITION_SMOOTHING_ALPHA

3. RESPONSE TIME TEST
   - Make quick gesture
   - Check if input registers
   - If slow, decrease DEBOUNCE_TIME

4. DETECTION TEST
   - Use debug mode: DEBUG_MODE = True
   - Monitor detection confidence in console
   - Adjust MIN_DETECTION_CONFIDENCE accordingly
     """

# ============================================================================

# ENVIRONMENT SETUP

# ============================================================================

"""
LIGHTING:

- Front lighting (3000-5000K) is ideal
- Avoid backlighting (shadows)
- Avoid direct sunlight on camera

BACKGROUND:

- Neutral background works best
- Complex backgrounds may reduce accuracy
- BlurI background helps: sit in front of plain wall

CAMERA:

- Position camera at eye level
- 1-2 meters distance
- 60° field of view minimum
- 1080p minimum resolution

HAND:

- Keep hand visible in frame
- Avoid rapid out-of-frame movements
- Keep fingers visible
- Avoid full hand closure (fist)
  """

# ============================================================================

# DEBUG MODE

# ============================================================================

"""
Enable DEBUG_MODE = True in config/settings.py to see:

- Hand detection confidence
- Smoothed X, Y coordinates (0.0-1.0)
- Detected gesture in real-time
- Console output: [DEBUG] messages

Example output:
[DEBUG] Wrist Position: X=0.45, Y=0.32, Gesture: UP
[INPUT] Pressing: UP (up)
"""

# ============================================================================

# CUSTOM MODIFICATIONS

# ============================================================================

"""
ADDING NEW GESTURES:

1. Modify gesture_detector.py \_detect_gesture() method
2. Example - Pinch detection:

   def \_detect_pinch_detected(self, landmarks): # Calculate distance between thumb and index finger
   thumb = landmarks[4]
   index = landmarks[8]
   distance = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2)\*\*0.5
   return distance < 0.05 # Threshold

3. Add to gesture mapping:
   if self.\_detect_pinch():
   return "PINCH"

CUSTOM KEY MAPPINGS:

1. Modify input_controller.py key_map dictionary
2. Example:
   key_map = {
   "UP": "w",
   "DOWN": "s",
   "LEFT": "a",
   "RIGHT": "d"
   }

ADDING NEW CONTROLS:

1. Modify main.py \_handle_keyboard() method
2. Add new key handler
3. Call appropriate method based on key
   """

# ============================================================================

# PERFORMANCE BENCHMARKS

# ============================================================================

"""
Expected Performance (varies by PC):

High-End PC (RTX 3060+):

- 70% scale, 50+ FPS
- Smooth hand tracking
- Minimal latency (~50ms)

Mid-Range PC (GTX 1660 / Ryzen 5):

- 60% scale, 35-45 FPS
- Smooth tracking
- Acceptable latency (~100ms)

Low-End PC (Integrated GPU):

- 40-50% scale, 25-35 FPS
- Functional but may feel slow
- Latency ~150-200ms

Optimization Priority:

1. Increase FRAME_SCALE_PERCENT (biggest impact)
2. Reduce SMOOTHING_BUFFER_SIZE
3. Lower MIN_DETECTION_CONFIDENCE
4. Close background applications
   """

print(**doc**)
