import cv2
import mediapipe as mp
from mediapipe.tasks import python
import threading
import time

class GestureRecognizer:
    def __init__(self, gesture_callback):
        self.gesture_callback = gesture_callback

    def main(self):
        num_hands = 2
        model_path = "gesture_recognizer.task"
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        self.lock = threading.Lock()
        self.current_gestures = []
        self.hand_landmarks = []
        self.timer_running = False
        self.cooldown_active = False
        self.area_coordinates = None
        options = GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            num_hands=num_hands,
            result_callback=self.__result_callback)
        recognizer = GestureRecognizer.create_from_options(options)

        timestamp = 0
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=num_hands,
                min_detection_confidence=0.65,
                min_tracking_confidence=0.65)

        cap = cv2.VideoCapture(4)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, -1) # Bild drehen
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            np_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if results.multi_hand_landmarks:
                self.hand_landmarks = results.multi_hand_landmarks
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np_array)
                    recognizer.recognize_async(mp_image, timestamp)
                    timestamp = timestamp + 1 # should be monotonically increasing, because in LIVE_STREAM mode

                self.put_gestures(frame)

            self.frame = frame
            cv2.imshow('MediaPipe Hands', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()

    def put_gestures(self, frame):
        with self.lock:
            gestures = self.current_gestures
        y_pos = 60
        for hand_gesture_name in gestures:
            # show the prediction on the frame
            cv2.putText(frame, hand_gesture_name, (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, (0,0,255), 2, cv2.LINE_AA)
            y_pos += 40

        # Tool selection
        tool_selection_result = self.tool_selection(frame)
        if tool_selection_result:
            self.gesture_callback(tool_selection_result)
            self.start_cooldown()

        # Area specification
        area_specification_result = self.area_specification(frame)
        if area_specification_result:
            self.gesture_callback(area_specification_result)
            self.start_cooldown()

        # Error gesture
        error_gesture_result = self.error_gesture(frame)
        if error_gesture_result:
            self.gesture_callback(error_gesture_result)
            self.start_cooldown()
            
    def __result_callback(self, result, output_image, timestamp_ms):
        with self.lock: # solves potential concurrency issues
            self.current_gestures = []
            if result is not None and any(result.gestures):
                gestures_tuple = tuple(single_hand_gesture_data[0].category_name for single_hand_gesture_data in result.gestures)
                self.current_gestures.extend(gestures_tuple)

    def area_specification(self, frame):
        if self.cooldown_active:
            print("Cooldown active, skipping area_specification")
            return None

        with self.lock:
            if self.current_gestures == ['Pointing_Up', 'Pointing_Up']:
                if len(self.hand_landmarks) == 2:
                    index_tip_1 = self.hand_landmarks[0].landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                    index_tip_2 = self.hand_landmarks[1].landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]

                    x1, y1 = int(index_tip_1.x * frame.shape[1]), int(index_tip_1.y * frame.shape[0])
                    x2, y2 = int(index_tip_2.x * frame.shape[1]), int(index_tip_2.y * frame.shape[0])

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Area Specification", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2, cv2.LINE_AA)
                    # Draw the coordinates of the index finger tips
                    cv2.putText(frame, f"({x1}, {y1})", (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"({x2}, {y2})", (x2, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                    # Start a timer to check if the function is activated for 5 seconds
                    if not self.timer_running:
                        self.timer_running = True
                        self.timer = threading.Timer(5.0, self.print_coordinates, args=[x1, y1, x2, y2])
                        self.timer.start()
                        print("Timer started")
        return None

    def tool_selection(self, frame):
        if self.cooldown_active:
            print("Cooldown active, skipping tool_selection")
            return None

        with self.lock:
            sorted_gestures = sorted(self.current_gestures)
            if sorted_gestures == ['Closed_Fist', 'Thumb_Up']:
                cv2.putText(frame, "Tool Selection: Level 1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2, cv2.LINE_AA)
                print("Gesture 1 recognized: Fine Tool selected")
                return "Tool Selection: Level 1"

            elif sorted_gestures == ['Closed_Fist', 'Victory']:
                cv2.putText(frame, "Tool Selection: Level 2", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2, cv2.LINE_AA)
                print("Gesture 2 recognized: Medium Tool selected")
                return "Tool Selection: Level 2"

            elif sorted_gestures == ['Closed_Fist', 'ILoveYou']:
                cv2.putText(frame, "Tool Selection: Level 3", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2, cv2.LINE_AA)
                print("Gesture 3 recognized: Fine Tool selected")
                return "Tool Selection: Level 3"
        return None

    def error_gesture(self, frame):
        if self.cooldown_active:
            print("Cooldown active, skipping error_gesture")
            return None

        with self.lock:
            sorted_gestures = sorted(self.current_gestures)
            if sorted_gestures == ['ILoveYou', 'ILoveYou']:
                cv2.putText(frame, "Error Gesture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2, cv2.LINE_AA)
                print("Error gesture recognized")
                return "Error gesture"
        return None

    def print_coordinates(self, x1, y1, x2, y2):
        print(f"Coordinates after 5 seconds: ({x1}, {y1}), ({x2}, {y2})")
        self.area_coordinates = (x1, y1, x2, y2)
        self.timer_running = False
        self.start_cooldown()
        self.gesture_callback(f"Area specification: ({x1}, {y1}), ({x2}, {y2})")

    def start_cooldown(self):
        self.cooldown_active = True
        threading.Timer(5.0, self.end_cooldown).start()

    def end_cooldown(self):
        self.cooldown_active = False
        print("Cooldown ended")

if __name__ == "__main__":
    def print_gesture(gesture):
        print(f"Detected gesture: {gesture}")

    rec = GestureRecognizer(print_gesture)
    rec.main()