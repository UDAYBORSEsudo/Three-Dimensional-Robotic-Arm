import cv2
import mediapipe as mp

class HandTracker:
    """Hand tracking using MediaPipe."""

    def __init__(self, max_hands=1, detection_conf=0.7, track_conf=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=track_conf
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, frame, draw=True):
        """
        Detects hand landmarks in a BGR frame.
        Returns: (frame, landmarks_list)
        - frame: image with landmarks drawn (if draw=True).
        - landmarks_list: list of hands; each is list of (id, x_norm, y_norm).
        Coordinates x_norm,y_norm are normalized [0,1] as per MediaPipe.
        """
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        all_hands = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if draw:
                    # Draw landmarks and connections on the frame
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, 
                                                self.mp_hands.HAND_CONNECTIONS)
                single_hand = []
                for idx, lm in enumerate(hand_landmarks.landmark):
                    # x and y are normalized to [0,1]
                    single_hand.append((idx, lm.x, lm.y))
                all_hands.append(single_hand)
        return frame, all_hands
