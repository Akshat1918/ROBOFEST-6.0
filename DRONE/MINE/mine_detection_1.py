from ultralytics import YOLO
import cv2
import os



MODEL_PATH = "C:\\ROBOFEST\\ROBOFEST 6.0\\DRONE\\MINE\\best.pt"

# Image to test
IMAGE_PATH = "C:\\ROBOFEST\\ROBOFEST 6.0\\DRONE\\MINE\\mine_1.jpg"

# Minimum confidence required
CONFIDENCE = 0.40


# ============================================================
# CHECK FILES
# ============================================================

if not os.path.exists(MODEL_PATH):
    print("ERROR: best.pt not found!")
    print("Make sure best.pt is in the same folder as this Python file.")
    exit()

if not os.path.exists(IMAGE_PATH):
    print("ERROR: Image not found!")
    print(f"Check IMAGE_PATH: {IMAGE_PATH}")
    exit()


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("==============================================")
print("          MINE DETECTION SYSTEM")
print("==============================================")
print()

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("Model loaded successfully.")
print()

# Show classes learned by the model
print("Model classes:")
print(model.names)
print()


# ============================================================
# RUN DETECTION
# ============================================================

print("Running detection...")
print()

results = model.predict(
    source=IMAGE_PATH,
    conf=CONFIDENCE,
    imgsz=640,
    verbose=False
)

result = results[0]


# ============================================================
# DISPLAY DETECTION RESULTS
# ============================================================

print("==============================================")
print("             DETECTION RESULTS")
print("==============================================")

if len(result.boxes) == 0:

    print("No objects detected.")

else:

    print(f"Objects detected: {len(result.boxes)}")
    print()

    for i, box in enumerate(result.boxes):

        # Class ID
        class_id = int(box.cls[0])

        # Confidence
        confidence = float(box.conf[0])

        # Class name
        class_name = model.names[class_id]

        # Bounding box
        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        print(
            f"Detection {i + 1}:"
        )

        print(
            f"  Class      : {class_name}"
        )

        print(
            f"  Confidence : {confidence:.2%}"
        )

        print(
            f"  Bounding Box: "
            f"({x1}, {y1}) -> ({x2}, {y2})"
        )

        print()


# ============================================================
# CREATE ANNOTATED IMAGE
# ============================================================

annotated_image = result.plot()


# ============================================================
# DISPLAY IMAGE
# ============================================================

cv2.imshow(
    "Mine Detection",
    annotated_image
)

print("==============================================")
print("Press Q to close the window.")
print("==============================================")


while True:

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cv2.destroyAllWindows()

print()
print("Detection system stopped.")