# file: modules/face_auth.py

import cv2
import time
import numpy as np
import face_recognition

# CONFIGURATION

FACE_MATCH_THRESHOLD = 0.50     # lower value = stricter match
REQUIRED_MATCHES = 3            # frames required to confirm identity
VERIFICATION_TIME_LIMIT = 10    # timeout to avoid infinite loop

# FACE REGISTRATION

def capture_face_encoding():
    """
    Capture user's face encoding during registration.
    """

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW for better Windows compatibility
    print("Press 'S' to capture face | ESC to cancel")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)

        # Draw detection boxes to guide user alignment
        for (top,right,bottom,left) in faces:
            cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)

        cv2.imshow("Face Capture",frame)
        key = cv2.waitKey(1)

        # Save encoding when user confirms capture
        if key == ord("s"):

            if len(faces) != 1:
                print("Ensure exactly one face is visible")
                continue

            encodings = face_recognition.face_encodings(rgb,faces)

            cap.release()
            cv2.destroyAllWindows()
            return encodings[0]

        if key == 27:  # ESC cancel
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

# FACE VERIFICATION

def verify_face(stored_encoding):
    """
    Verify user identity using stored face encoding.
    """

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW for better Windows compatibility

    if not cap.isOpened():
        print("Camera not available")
        return False

    print("Face verification started. Look at the camera.")

    stored_encoding = np.array(stored_encoding)
    match_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)

        # Draw bounding boxes to show detection
        for (top,right,bottom,left) in face_locations:
            cv2.rectangle(frame,(left,top),(right,bottom),(0,255,0),2)

        cv2.imshow("Face Verification",frame)

        face_encodings = face_recognition.face_encodings(rgb,face_locations)

        for encoding in face_encodings:

            # Face similarity distance calculation
            distance = face_recognition.face_distance([stored_encoding],encoding)[0]
            print("Face distance:",distance)

            if distance < FACE_MATCH_THRESHOLD:

                match_count += 1
                print("Match frame:",match_count)

                if match_count >= REQUIRED_MATCHES:
                    print("Face verified")
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

        # Prevent endless verification attempts
        if time.time() - start_time > VERIFICATION_TIME_LIMIT:

            print("Verification timeout")
            cap.release()
            cv2.destroyAllWindows()
            return False

        if cv2.waitKey(1) & 0xFF == 27:  # manual exit
            break

    cap.release()
    cv2.destroyAllWindows()
    return False