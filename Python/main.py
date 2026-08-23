
import cv2
import time
import serial
import argparse
from Python.hand_tracking import HandTracker
from Python.gesture_control import GestureController

def main():
    parser = argparse.ArgumentParser(
        description="3-DOF Robotic Arm control via hand gestures"
    )
    parser.add_argument("--port", type=str, default="COM4",
                        help="Arduino serial port (e.g., COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200,
                        help="Baud rate for serial (default: 115200)")
    args = parser.parse_args()

    # --- Initialize Serial Communication with Arduino ---
    try:
        arduino = serial.Serial(args.port, args.baud, timeout=1)
        time.sleep(2)  # Wait for Arduino reset
    except Exception as e:
        print(f"[Error] Could not open serial port {args.port}: {e}")
        return

    # --- Initialize Hand Tracker and Gesture Controller ---
    cap = cv2.VideoCapture(0)
    tracker = HandTracker(max_hands=1)
    controller = GestureController(smoothing=0.2)

    print("[Info] Starting camera and tracking. Press 'q' to quit.")
    while True:
        success, frame = cap.read()
        if not success:
            continue  # skip if frame not captured
        frame = cv2.flip(frame, 1)  # mirror image for natural interaction

        frame, all_landmarks = tracker.find_hands(frame, draw=True)
        if all_landmarks:
            # Use first detected hand
            base_ang, arm_ang, grip_ang = controller.calculate_servo_angles(all_landmarks[0])
            # Prepare serial command
            command = f"{base_ang},{arm_ang},{grip_ang}\n"
            arduino.write(command.encode())  # send as bytes
            # Display angles on frame for debugging
            cv2.putText(frame, f"Base: {base_ang}", (10,30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.putText(frame, f"Arm: {arm_ang}", (10,60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.putText(frame, f"Gripper: {grip_ang}", (10,90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow("3D Robotic Arm Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    arduino.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
