import cv2
import dlib
import numpy as np
import tensorflow as tf
import time

print("[INFO] Loading blink model...")
model = tf.keras.models.load_model("blink_model.h5")
print("[INFO] Model loaded successfully")

predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()

IMG_SIZE = 64


def preprocess_eye(eye):
    eye = cv2.resize(eye, (IMG_SIZE, IMG_SIZE))
    eye = eye.astype("float32") / 255.0
    eye = np.expand_dims(eye, axis=0)
    return eye


def predict_eye(eye):
    eye = preprocess_eye(eye)
    pred = model.predict(eye, verbose=0)[0][0]

    if pred > 0.5:
        return "open"
    return "closed"


def extract_eye(frame, landmarks, points):
    coords = []

    for p in points:
        x = landmarks.part(p).x
        y = landmarks.part(p).y
        coords.append((x, y))

    x_vals = [p[0] for p in coords]
    y_vals = [p[1] for p in coords]

    x1 = max(min(x_vals) - 5, 0)
    y1 = max(min(y_vals) - 5, 0)
    x2 = min(max(x_vals) + 5, frame.shape[1])
    y2 = min(max(y_vals) + 5, frame.shape[0])

    eye = frame[y1:y2, x1:x2]
    return eye


def liveness_check():
    print("[INFO] Starting AI blink liveness check")

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print("[ERROR] Webcam not opened")
        return False

    blink_count = 0
    prev_state = "open"
    start = time.time()

    while True:
        ret, frame = cap.read()

        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        if len(faces) == 1:

            face = faces[0]
            landmarks = predictor(gray, face)

            left_eye = extract_eye(frame, landmarks, [36, 37, 38, 39, 40, 41])
            right_eye = extract_eye(frame, landmarks, [42, 43, 44, 45, 46, 47])

            if left_eye.size == 0 or right_eye.size == 0:
                continue

            left_state = predict_eye(left_eye)
            right_state = predict_eye(right_eye)

            eye_state = "closed"

            if left_state == "open" or right_state == "open":
                eye_state = "open"

            print("[LIVE] Eye State:", eye_state)

            cv2.putText(
                frame,
                f"Eye: {eye_state}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            if prev_state == "open" and eye_state == "closed":
                blink_count += 1
                print("[INFO] Blink Detected:", blink_count)

            prev_state = eye_state

            if blink_count >= 1:
                print("[SUCCESS] Liveness Verified")
                cap.release()
                cv2.destroyAllWindows()
                return True

        else:
            cv2.putText(
                frame,
                "Show One Face",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

        cv2.imshow("Digivault AI Blink Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

        if time.time() - start > 20:
            print("[TIMEOUT] Verification failed")
            break

    cap.release()
    cv2.destroyAllWindows()
    return False