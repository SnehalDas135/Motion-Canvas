"""
face_mesh.py — REFACTORED for MediaPipe Tasks API
Compatible with Python 3.14 + mediapipe-tasks-vision

Original used solutions.face_mesh; this uses FaceLandmarker.
Requires models/face_landmarker.task to be present.
"""
import cv2
import os
import mediapipe as mp
import numpy as np
from typing import Optional
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import FaceLandmarkerOptions
from mediapipe.tasks.python.vision import FaceLandmarker
from mediapipe.tasks.python.vision import RunningMode

# Locate model file relative to this script
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT, "models", "face_landmarker.task")

class FaceMesh:
    def __init__(self, process_every_n: int = 2):
        """
        process_every_n: skip frames to reduce CPU usage
        """
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"MediaPipe model not found at {MODEL_PATH}")

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False
        )
        self._mesh = FaceLandmarker.create_from_options(options)

        self._process_every = process_every_n
        self._frame_idx     = 0
        self._last_landmarks: Optional[list] = None

    def process(self, bgr_frame: np.ndarray) -> tuple[Optional[list], np.ndarray]:
        """
        Process one webcam frame.
        """
        self._frame_idx += 1

        # Skip frames for performance
        if self._frame_idx % self._process_every != 0:
            return self._last_landmarks, bgr_frame

        # Convert to mp.Image
        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Detect
        results = self._mesh.detect(mp_image)

        annotated = bgr_frame.copy()

        if not results.face_landmarks:
            self._last_landmarks = None
            return None, annotated

        # Get first face
        face = results.face_landmarks[0]

        # Convert landmarks to flat list of [x, y, z] for engine_bridge
        landmarks = [[lm.x, lm.y, lm.z] for lm in face]
        self._last_landmarks = landmarks

        # Simple drawing: iris circles
        h, w = bgr_frame.shape[:2]
        # Common iris indices in 478-landmark set
        # Left: 468-472; Right: 473-477
        iris_indices = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]
        for idx in iris_indices:
            if idx < len(face):
                lm = face[idx]
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(annotated, (cx, cy), 2, (0, 200, 120), -1)

        # Basic face dot drawing (nose tip, mouth, eyes corners)
        # to give some visual feedback without full tessellation
        for idx in [1, 13, 14, 33, 133, 263, 362]:
            if idx < len(face):
                lm = face[idx]
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(annotated, (cx, cy), 1, (0, 255, 120), -1)

        return landmarks, annotated

    def close(self):
        self._mesh.close()
