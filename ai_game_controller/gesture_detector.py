"""
Gesture Detection Module
Handles hand tracking and gesture recognition using MediaPipe
Supports both MediaPipe API versions (Solutions & Tasks API).
"""

import cv2
import os
import sys
import urllib.request
import zipfile
from collections import deque

from config.settings import (
    GESTURE_UP_THRESHOLD, GESTURE_DOWN_THRESHOLD,
    GESTURE_LEFT_THRESHOLD, GESTURE_RIGHT_THRESHOLD,
    MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE,
    MAX_NUM_HANDS, POSITION_SMOOTHING_ALPHA, SMOOTHING_BUFFER_SIZE,
    DEBUG_MODE
)

# ---------------------------------------------------------------------------
# 1 — Detect which MediaPipe API is available
# ---------------------------------------------------------------------------

_USE_TASKS_API = False

try:
    import mediapipe as mp

    # MediaPipe >= 0.10.30 uses mp.tasks.vision (Tasks API)
    if hasattr(mp, 'tasks') and hasattr(mp.tasks, 'vision'):
        _USE_TASKS_API = True
        print(f"[MEDIAPIPE] Using Tasks API (MediaPipe v{mp.__version__})")
    elif hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands'):
        print(f"[MEDIAPIPE] Using Solutions API (MediaPipe v{mp.__version__})")
    else:
        raise ImportError("No recognisable MediaPipe API structure found")
except (AttributeError, ImportError) as e:
    print(f"[ERROR] Failed to import MediaPipe: {e}")
    print("[ERROR] Install with: pip install mediapipe")
    sys.exit(1)


# ---------------------------------------------------------------------------
# 2 — Model auto-download (Tasks API only)
# ---------------------------------------------------------------------------

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
_MODEL_PATH = os.path.join(_MODEL_DIR, "hand_landmarker.task")

# Google MediaPipe model zoo URL for the hand landmarker (lite version)
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/"
    "hand_landmarker.task"
)


def _ensure_model() -> str:
    """Download the hand_landmarker.task model if it doesn't exist locally."""
    if os.path.isfile(_MODEL_PATH):
        return _MODEL_PATH

    os.makedirs(_MODEL_DIR, exist_ok=True)
    print(f"[MODEL] Downloading hand_landmarker.task from MediaPipe Model Zoo…")
    try:
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        print(f"[MODEL] Saved to {_MODEL_PATH}")
    except Exception as exc:
        print(f"[ERROR] Failed to download model: {exc}")
        print(f"[ERROR] Manually download from: {_MODEL_URL}")
        print(f"[ERROR] Place the file at: {_MODEL_PATH}")
        sys.exit(1)
    return _MODEL_PATH


# ---------------------------------------------------------------------------
# 3 — Unified hand-landmarker wrapper
# ---------------------------------------------------------------------------

class _HandLandmarkerWrapper:
    """
    Wraps either the Solutions API or Tasks API behind a uniform interface.

    The caller uses:
        result = wrapper.process(rgb_frame)
        result.multi_hand_landmarks   -> list of landmark containers or None
        wrapper.draw_landmarks(frame, hand_landmarks)
    """

    def __init__(self):
        if _USE_TASKS_API:
            self._init_tasks()
        else:
            self._init_solutions()

    # --- Tasks API ---------------------------------------------------------

    def _init_tasks(self):
        from mediapipe.tasks.python.vision import (
            HandLandmarker as _HL,
            HandLandmarkerOptions as _HLOptions,
        )
        from mediapipe.tasks.python.core.base_options import BaseOptions
        from mediapipe.tasks.python.components.containers.landmark import (
            NormalizedLandmark,
        )
        from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
            VisionTaskRunningMode,
        )
        from mediapipe.tasks.python.vision.core.image import Image as MpImage
        import mediapipe as _mp
        self._mp_image_cls = MpImage
        self._mp_srgb = _mp.ImageFormat.SRGB

        model_path = _ensure_model()

        options = _HLOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionTaskRunningMode.VIDEO,
            num_hands=MAX_NUM_HANDS,
            min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self._detector = _HL.create_from_options(options)
        self._landmark_cls = NormalizedLandmark
        self._timestamp_ms = 0

        # Fallback landmark-index enum (Tasks API doesn't provide one)
        class _HandLandmarkIdx:
            WRIST = 0
            THUMB_CMC = 1
            THUMB_MCP = 2
            THUMB_IP = 3
            THUMB_TIP = 4
            INDEX_FINGER_MCP = 5
            INDEX_FINGER_PIP = 6
            INDEX_FINGER_DIP = 7
            INDEX_FINGER_TIP = 8
            MIDDLE_FINGER_MCP = 9
            MIDDLE_FINGER_PIP = 10
            MIDDLE_FINGER_DIP = 11
            MIDDLE_FINGER_TIP = 12
            RING_FINGER_MCP = 13
            RING_FINGER_PIP = 14
            RING_FINGER_DIP = 15
            RING_FINGER_TIP = 16
            PINKY_MCP = 17
            PINKY_PIP = 18
            PINKY_DIP = 19
            PINKY_TIP = 20

        self.hand_landmark_enum = _HandLandmarkIdx()

    # --- Solutions API -----------------------------------------------------

    def _init_solutions(self):
        from mediapipe.python.solutions import hands as _hands
        from mediapipe.python.solutions import drawing_utils as _drawing
        from mediapipe.python.solutions import drawing_styles as _styles

        self._detector = _hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_NUM_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        self._drawing_utils = _drawing
        self._drawing_styles = _styles
        self._landmark_cls = None
        self._timestamp_ms = 0
        self.hand_landmark_enum = _hands.HandLandmark

        # Hand connections
        try:
            self._hand_connections = _hands.HAND_CONNECTIONS
        except AttributeError:
            try:
                from mediapipe.python.solutions.hands_connections import (
                    HAND_CONNECTIONS as _hc,
                )
                self._hand_connections = _hc
            except ImportError:
                self._hand_connections = None

    # --- Public interface --------------------------------------------------

    def process(self, rgb_frame):
        """Process an RGB frame; returns an object with .multi_hand_landmarks."""
        if _USE_TASKS_API:
            return self._process_tasks(rgb_frame)
        return self._detector.process(rgb_frame)

    def _process_tasks(self, rgb_frame):
        self._timestamp_ms += 33  # ~30 fps
        # Ensure the array is C-contiguous (required by the C++ backend)
        rgb_frame = rgb_frame if rgb_frame.flags['C_CONTIGUOUS'] else rgb_frame.copy()
        # Wrap the numpy array in a MediaPipe Image object
        mp_image = self._mp_image_cls(
            image_format=self._mp_srgb,
            data=rgb_frame,
        )
        result = self._detector.detect_for_video(mp_image, self._timestamp_ms)
        return _TasksResultAdapter(result)

    def draw_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on the frame."""
        if _USE_TASKS_API:
            self._draw_tasks(frame, hand_landmarks)
        else:
            self._draw_solutions(frame, hand_landmarks)

    def _draw_tasks(self, frame, hand_landmarks):
        if not hand_landmarks:
            return
        h, w, _ = frame.shape
        try:
            for lm in hand_landmarks:
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),             # thumb
                (0, 5), (5, 6), (6, 7), (7, 8),             # index
                (0, 9), (9, 10), (10, 11), (11, 12),         # middle
                (0, 13), (13, 14), (14, 15), (15, 16),       # ring
                (0, 17), (17, 18), (18, 19), (19, 20),       # pinky
                (5, 9), (9, 13), (13, 17),                    # palm
            ]
            for i, j in connections:
                if i < len(hand_landmarks) and j < len(hand_landmarks):
                    p1 = (int(hand_landmarks[i].x * w), int(hand_landmarks[i].y * h))
                    p2 = (int(hand_landmarks[j].x * w), int(hand_landmarks[j].y * h))
                    cv2.line(frame, p1, p2, (0, 255, 0), 2)
        except Exception as e:
            if DEBUG_MODE:
                print(f"[DEBUG] Landmark draw error: {e}")

    def _draw_solutions(self, frame, hand_landmarks):
        if self._drawing_utils is None:
            return
        try:
            if self._hand_connections is not None and self._drawing_styles is not None:
                self._drawing_utils.draw_landmarks(
                    frame, hand_landmarks, self._hand_connections,
                    self._drawing_styles.get_default_hand_landmarks_style(),
                    self._drawing_styles.get_default_hand_connections_style(),
                )
            elif self._hand_connections is not None:
                self._drawing_utils.draw_landmarks(frame, hand_landmarks,
                                                   self._hand_connections)
            else:
                self._drawing_utils.draw_landmarks(frame, hand_landmarks)
        except Exception as e:
            if DEBUG_MODE:
                print(f"[DEBUG] Landmark draw error: {e}")

    def close(self):
        try:
            self._detector.close()
        except Exception:
            pass


class _TasksResultAdapter:
    """Makes a Tasks API result look like a Solutions result."""

    def __init__(self, result):
        self._result = result

    @property
    def multi_hand_landmarks(self):
        if self._result is None:
            return None
        try:
            return self._result.hand_landmarks
        except AttributeError:
            return None

    def __bool__(self):
        return self._result is not None


# ============================================================================
# 4 — GestureDetector (public API)
# ============================================================================

class GestureDetector:
    """
    Real-time hand gesture detection using MediaPipe.

    Detects gestures from wrist landmark position:
        UP / DOWN / LEFT / RIGHT / NONE
    """

    def __init__(self):
        try:
            self._wrapper = _HandLandmarkerWrapper()
            self.hand_landmark_enum = self._wrapper.hand_landmark_enum
        except Exception as e:
            print(f"[ERROR] MediaPipe init failed: {e}")
            raise

        self.wrist_x_buffer = deque(maxlen=SMOOTHING_BUFFER_SIZE)
        self.wrist_y_buffer = deque(maxlen=SMOOTHING_BUFFER_SIZE)
        self.current_gesture = "NONE"
        self.hand_detected = False
        self.hand_landmarks = None

    def process_frame(self, frame):
        """
        Process a single video frame.

        Returns:
            (frame, gesture, hand_detected, wrist_position)
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._wrapper.process(rgb_frame)

        self.hand_detected = False
        gesture = "NONE"
        wrist_pos = None

        landmarks_list = results.multi_hand_landmarks if results else None
        if landmarks_list and len(landmarks_list) > 0:
            self.hand_detected = True
            hand_landmarks = landmarks_list[0]
            self.hand_landmarks = hand_landmarks

            wrist = hand_landmarks[self.hand_landmark_enum.WRIST]
            wx, wy = wrist.x, wrist.y

            self.wrist_x_buffer.append(wx)
            self.wrist_y_buffer.append(wy)

            sx = sum(self.wrist_x_buffer) / len(self.wrist_x_buffer)
            sy = sum(self.wrist_y_buffer) / len(self.wrist_y_buffer)
            wrist_pos = (sx, sy)

            gesture = self._detect_gesture(sx, sy)
            self._wrapper.draw_landmarks(frame, hand_landmarks)

            if DEBUG_MODE:
                print(f"Wrist: X={sx:.2f} Y={sy:.2f} Gesture={gesture}")

        self.current_gesture = gesture
        return frame, gesture, self.hand_detected, wrist_pos

    def _detect_gesture(self, x, y):
        if y < GESTURE_UP_THRESHOLD:
            return "UP"
        if y > GESTURE_DOWN_THRESHOLD:
            return "DOWN"
        if x < GESTURE_LEFT_THRESHOLD:
            return "LEFT"
        if x > GESTURE_RIGHT_THRESHOLD:
            return "RIGHT"
        return "NONE"

    def get_current_gesture(self):
        return self.current_gesture

    def is_hand_detected(self):
        return self.hand_detected

    def close(self):
        self._wrapper.close()