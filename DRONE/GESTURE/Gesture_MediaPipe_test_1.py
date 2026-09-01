import cv2
import time
import os
import urllib.request
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)

# Look for existing model in current dir, script dir, parent dir, or root dir
potential_paths = [
    "gesture_recognizer.task",
    os.path.join(SCRIPT_DIR, "gesture_recognizer.task"),
    os.path.join(PARENT_DIR, "gesture_recognizer.task"),
    os.path.join(ROOT_DIR, "gesture_recognizer.task"),
]

MODEL_PATH = next((p for p in potential_paths if os.path.exists(p)), os.path.join(SCRIPT_DIR, "gesture_recognizer.task"))

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-tasks/"
    "gesture_recognizer/gesture_recognizer.task"
)

CAMERA_INDEX = 0

CONFIDENCE_THRESHOLD = 0.40

PALM_HOLD_TIME = 1.0


# ============================================================
# DOWNLOAD MEDIAPIPE MODEL
# ============================================================

if not os.path.exists(MODEL_PATH):

    print()
    print("Downloading MediaPipe Gesture Recognizer model...")
    print()

    urllib.request.urlretrieve(
        MODEL_URL,
        MODEL_PATH
    )

    print("Model downloaded successfully.")
    print()


# ============================================================
# CREATE MEDIAPIPE GESTURE RECOGNIZER
# ============================================================

print("Loading MediaPipe...")

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)


options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


recognizer = vision.GestureRecognizer.create_from_options(
    options
)


print("MediaPipe loaded successfully.")


# ============================================================
# OPEN CAMERA
# ============================================================

print()
print("Starting camera...")

cap = cv2.VideoCapture(
    CAMERA_INDEX,
    cv2.CAP_DSHOW
)


if not cap.isOpened():

    # Try again without CAP_DSHOW
    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )


if not cap.isOpened():

    print()
    print("ERROR: Camera could not be opened.")
    print()
    print("Try changing CAMERA_INDEX from 0 to 1.")
    print()

    recognizer.close()

    exit()


# Camera resolution

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    1280
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    720
)


print("Camera started.")
print()
print("==============================================")
print("       DRONE GESTURE CONTROL SYSTEM")
print("==============================================")
print()
print("Show your hand to the camera.")
print()
print("OPEN PALM  -> TAKEOFF")
print("CLOSED FIST -> LAND / STOP")
print("THUMB UP   -> CONFIRM")
print("VICTORY    -> MODE")
print("POINTING UP -> COMMAND")
print()
print("Hold OPEN PALM for 1 second for TAKEOFF.")
print()
print("Press Q to quit.")
print()


# ============================================================
# VARIABLES
# ============================================================

timestamp = 0

palm_start_time = None

takeoff_triggered = False

last_gesture = "NO HAND"

last_confidence = 0.0


# ============================================================
# UI FUNCTION
# ============================================================

def draw_ui(
    frame,
    gesture,
    confidence,
    drone_status,
    fps
):

    height, width, _ = frame.shape


    # ========================================================
    # HEADER
    # ========================================================

    cv2.rectangle(
        frame,
        (0, 0),
        (width, 80),
        (20, 30, 45),
        -1
    )


    cv2.putText(
        frame,
        "DRONE GESTURE CONTROL",
        (30, 52),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


    # FPS

    cv2.putText(
        frame,
        f"FPS: {fps:.0f}",
        (width - 130, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )


    # ========================================================
    # GESTURE PANEL
    # ========================================================

    cv2.rectangle(
        frame,
        (25, 105),
        (390, 260),
        (30, 42, 58),
        -1
    )


    cv2.putText(
        frame,
        "DETECTED GESTURE",
        (45, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (170, 180, 190),
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        gesture,
        (45, 195),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        f"Confidence: {confidence:.0%}",
        (45, 235),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )


    # ========================================================
    # DRONE STATUS PANEL
    # ========================================================

    cv2.rectangle(
        frame,
        (420, 105),
        (800, 260),
        (30, 42, 58),
        -1
    )


    cv2.putText(
        frame,
        "DRONE STATUS",
        (445, 140),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (170, 180, 190),
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        drone_status,
        (445, 200),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


    # ========================================================
    # COMMAND PANEL
    # ========================================================

    cv2.rectangle(
        frame,
        (25, height - 155),
        (800, height - 25),
        (20, 30, 45),
        -1
    )


    cv2.putText(
        frame,
        "GESTURE COMMANDS",
        (45, height - 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (170, 180, 190),
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        "OPEN PALM -> TAKEOFF",
        (45, height - 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (235, 235, 235),
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        "CLOSED FIST -> LAND / STOP",
        (300, height - 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (235, 235, 235),
        1,
        cv2.LINE_AA
    )


    cv2.putText(
        frame,
        "THUMB UP | VICTORY | POINTING UP",
        (45, height - 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (200, 200, 200),
        1,
        cv2.LINE_AA
    )


    # ========================================================
    # CENTER TAKEOFF MESSAGE
    # ========================================================

    if takeoff_triggered:

        cv2.rectangle(
            frame,
            (width // 2 - 250, 300),
            (width // 2 + 250, 390),
            (0, 100, 0),
            -1
        )


        cv2.putText(
            frame,
            "TAKEOFF COMMAND",
            (width // 2 - 205, 355),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )


        cv2.putText(
            frame,
            "OPEN PALM DETECTED",
            (width // 2 - 175, 385),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (230, 255, 230),
            1,
            cv2.LINE_AA
        )


    return frame


# ============================================================
# FPS CALCULATION
# ============================================================

previous_time = time.time()

fps = 0


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:


        # ----------------------------------------------------
        # READ CAMERA
        # ----------------------------------------------------

        ret, frame = cap.read()


        if not ret:

            print(
                "ERROR: Could not read camera frame."
            )

            break


        # ----------------------------------------------------
        # MIRROR IMAGE
        # ----------------------------------------------------

        frame = cv2.flip(
            frame,
            1
        )


        # ----------------------------------------------------
        # RGB
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # CREATE MEDIAPIPE IMAGE
        # ----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )


        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = int(
            time.time() * 1000
        )


        # ----------------------------------------------------
        # MEDIAPIPE RECOGNITION
        # ----------------------------------------------------

        result = recognizer.recognize_for_video(
            mp_image,
            timestamp
        )


        # ----------------------------------------------------
        # DEFAULT VALUES
        # ----------------------------------------------------

        gesture = "NO HAND"

        confidence = 0.0


        # ----------------------------------------------------
        # CHECK GESTURE
        # ----------------------------------------------------

        if result.gestures:

            category = result.gestures[0][0]

            gesture = category.category_name

            confidence = category.score


        # ----------------------------------------------------
        # TAKEOFF LOGIC
        # ----------------------------------------------------

        if (
            gesture == "Open_Palm"
            and
            confidence >= CONFIDENCE_THRESHOLD
        ):


            if palm_start_time is None:

                palm_start_time = time.time()


            held_time = (
                time.time()
                - palm_start_time
            )


            if held_time >= PALM_HOLD_TIME:

                takeoff_triggered = True

                drone_status = (
                    "TAKEOFF COMMAND"
                )


            else:

                remaining = (
                    PALM_HOLD_TIME
                    - held_time
                )

                drone_status = (
                    f"HOLD PALM {remaining:.1f}s"
                )


        else:

            palm_start_time = None

            takeoff_triggered = False

            drone_status = "DRONE READY"


        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        current_time = time.time()

        delta = (
            current_time
            - previous_time
        )


        if delta > 0:

            fps = 1 / delta


        previous_time = current_time


        # ----------------------------------------------------
        # DRAW UI
        # ----------------------------------------------------

        display_frame = draw_ui(
            frame,
            gesture.replace("_", " "),
            confidence,
            drone_status,
            fps
        )


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        cv2.imshow(
            "Drone Gesture Control",
            display_frame
        )


        # ----------------------------------------------------
        # KEYBOARD
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF


        if key == ord("q"):

            break


except KeyboardInterrupt:

    print()
    print("Interrupted by user.")


finally:

    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()

    cv2.destroyAllWindows()

    recognizer.close()

    print()
    print("==========================================")
    print("       DRONE GESTURE SYSTEM STOPPED")
    print("==========================================")