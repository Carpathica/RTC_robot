import cv2
import mediapipe as mp
import numpy as np

# --- MediaPipe Tasks ---
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

# --- Связи между точками (скелет руки) ---
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),        # большой палец
    (0,5),(5,6),(6,7),(7,8),        # указательный
    (0,9),(9,10),(10,11),(11,12),   # средний
    (0,13),(13,14),(14,15),(15,16), # безымянный
    (0,17),(17,18),(18,19),(19,20)  # мизинец
]

# --- Проверка кулака ---
def is_fist(landmarks):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    wrist = landmarks[0]

    for tip, pip in zip(tips, pips):
        tip_dist = np.linalg.norm(
            np.array([landmarks[tip].x - wrist.x,
                      landmarks[tip].y - wrist.y])
        )

        pip_dist = np.linalg.norm(
            np.array([landmarks[pip].x - wrist.x,
                      landmarks[pip].y - wrist.y])
        )

        if tip_dist > pip_dist:
            return False

    return True


# --- Рисование ---
def draw_hand(image, landmarks):
    h, w, _ = image.shape

    # Рисуем линии (скелет)
    for connection in HAND_CONNECTIONS:
        start = landmarks[connection[0]]
        end = landmarks[connection[1]]

        x1, y1 = int(start.x * w), int(start.y * h)
        x2, y2 = int(end.x * w), int(end.y * h)

        cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Рисуем точки
    for lm in landmarks:
        x, y = int(lm.x * w), int(lm.y * h)
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)


# --- Камера ---
cap = cv2.VideoCapture(0)

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        results = landmarker.detect_for_video(
            mp_image,
            int(cap.get(cv2.CAP_PROP_POS_MSEC))
        )

        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:

                # --- Рисуем скелет ---
                draw_hand(frame, hand_landmarks)

                # --- Проверка кулака ---
                if is_fist(hand_landmarks):
                    text = "FIST"
                    color = (0, 0, 255)
                else:
                    text = "OPEN"
                    color = (0, 255, 0)

                cv2.putText(frame, text, (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("Hand Skeleton", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()