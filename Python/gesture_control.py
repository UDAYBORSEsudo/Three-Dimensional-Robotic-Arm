import math

class GestureController:
    """
    Converts hand landmarks to robotic arm servo angles.
    Includes smoothing and safety limits.
    """

    def __init__(self, smoothing=0.2):
        # Initial angles (home positions)
        self.prev_angles = {'base': 90, 'arm': 90, 'gripper': 90}
        self.smoothing = smoothing
        self.gripper_open = 100   # angle for open gripper
        self.gripper_close = 20   # angle for closed gripper

    def calculate_servo_angles(self, landmarks):
        """
        Given one hand's landmarks, compute (base_angle, arm_angle, gripper_angle).
        landmarks: list of (id, x_norm, y_norm).
        Returns a tuple of ints (base, arm, gripper) in [0,180].
        """
        if not landmarks:
            return None

        # Extract key points: wrist (id 0), index tip (id 8), thumb tip (id 4)
        wrist = next((x, y) for (i, x, y) in landmarks if i == 0)
        index = next((x, y) for (i, x, y) in landmarks if i == 8)
        thumb = next((x, y) for (i, x, y) in landmarks if i == 4)

        # Compute raw angles
        base_target = int(wrist[0] * 180)              # horizontal position → 0–180
        arm_target = int((1 - wrist[1]) * 180)         # vertical position → invert y
        # Distance between thumb and index (normalized)
        dist = math.hypot(index[0] - thumb[0], index[1] - thumb[1])
        # Determine gripper target based on distance
        gripper_target = (self.gripper_close 
                          if dist < 0.1 else self.gripper_open)

        # Smooth transitions
        base = int(self.prev_angles['base'] +
                   self.smoothing * (base_target - self.prev_angles['base']))
        arm = int(self.prev_angles['arm'] +
                  self.smoothing * (arm_target - self.prev_angles['arm']))
        grip = int(self.prev_angles['gripper'] +
                   self.smoothing * (gripper_target - self.prev_angles['gripper']))

        # Safety limits
        base = max(0, min(180, base))
        arm = max(0, min(180, arm))
        grip = max(0, min(180, grip))

        # Update previous values
        self.prev_angles = {'base': base, 'arm': arm, 'gripper': grip}
        return base, arm, grip
