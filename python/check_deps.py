try:
    import tkinter
    print("tkinter: OK")
except ImportError as e:
    print(f"tkinter: MISSING ({e})")

try:
    import cv2
    print("opencv: OK")
except ImportError as e:
    print(f"opencv: MISSING ({e})")

try:
    import mediapipe
    print("mediapipe: OK")
except ImportError as e:
    print(f"mediapipe: MISSING ({e})")

try:
    import pynput
    print("pynput: OK")
except ImportError as e:
    print(f"pynput: MISSING ({e})")

try:
    import flask
    print("flask: OK")
except ImportError as e:
    print(f"flask: MISSING ({e})")

try:
    import flask_socketio
    print("flask_socketio: OK")
except ImportError as e:
    print(f"flask_socketio: MISSING ({e})")

try:
    import speech_recognition
    print("speech_recognition: OK")
except ImportError as e:
    print(f"speech_recognition: MISSING ({e})")

try:
    import numpy
    print("numpy: OK")
except ImportError as e:
    print(f"numpy: MISSING ({e})")
