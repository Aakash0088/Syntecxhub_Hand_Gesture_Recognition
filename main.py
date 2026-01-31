import cv2
import mediapipe as mp
import pyautogui
from collections import deque, Counter
from gesture_logic import fingers_up, classify_gesture

# ---------------- Camera ----------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ---------------- Window ----------------
WIN_NAME = "Hand Gesture Control Demo"
cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WIN_NAME, 1280, 720)

# ---------------- MediaPipe ----------------
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mpDraw = mp.solutions.drawing_utils

# ---------------- Smoothing ----------------
HISTORY_LEN = 6
gesture_history = {
    "Left": deque(maxlen=HISTORY_LEN),
    "Right": deque(maxlen=HISTORY_LEN)
}

# ---------------- Cooldown ----------------
COOLDOWN_FRAMES = 20
cooldown = 0

prev_action = ""

print("Gesture Control Demo Started")
print("Right hand controls the system")
print("Press Q to quit")

# ---------------- Main Loop ----------------
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    h, w, c = img.shape

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if cooldown > 0:
        cooldown -= 1

    if results.multi_hand_landmarks and results.multi_handedness:
        for idx in range(len(results.multi_hand_landmarks)):

            handLms = results.multi_hand_landmarks[idx]
            hand_label = results.multi_handedness[idx].classification[0].label  # Left / Right

            lmList = []
            for id, lm in enumerate(handLms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            # ---------- Detect ----------
            fingers = fingers_up(lmList)
            gesture = classify_gesture(fingers, lmList)

            # ---------- Smoothing ----------
            gesture_history[hand_label].append(gesture)
            common = Counter(gesture_history[hand_label]).most_common(1)[0][0]

            # ---------- ACTIONS (ONLY RIGHT HAND) ----------
            if hand_label == "Right" and cooldown == 0 and common != prev_action:

                if common == "FIST":
                    pyautogui.press("playpause")
                    cooldown = COOLDOWN_FRAMES

                elif common == "THUMBS_UP":
                    pyautogui.press("volumeup")
                    cooldown = COOLDOWN_FRAMES

                elif common == "THUMBS_DOWN":
                    pyautogui.press("volumedown")
                    cooldown = COOLDOWN_FRAMES

                elif common == "V_SIGN":
                    pyautogui.press("nexttrack")
                    cooldown = COOLDOWN_FRAMES

                elif common == "INDEX":
                    pyautogui.press("volumemute")
                    cooldown = COOLDOWN_FRAMES

                prev_action = common

            # ---------- UI ----------
            x0, y0 = lmList[0][1], lmList[0][2]
            color = (0,255,0) if hand_label == "Right" else (255,0,0)

            text = f"{hand_label} Hand : {common}"
            cv2.putText(img, text, (x0 - 40, y0 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # ---------- Show ----------
    cv2.imshow(WIN_NAME, img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

    if cv2.getWindowProperty(WIN_NAME, cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
