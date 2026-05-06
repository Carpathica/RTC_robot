import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import Int8

from cv_bridge import CvBridge

import cv2
import mediapipe as mp
import numpy as np


class HandFistNode(Node):
    def __init__(self):
        super().__init__('hand_fist_node')

        # --- Publisher ---
        self.publisher_ = self.create_publisher(Int8, '/hand/fist_state', 10)

        # --- Subscriber (камера) ---
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        self.bridge = CvBridge()

        # --- MediaPipe ---
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=1
        )

        self.landmarker = HandLandmarker.create_from_options(options)

    # --- Логика кулака ---
    def is_fist(self, landmarks):
        tips = [8, 12, 16, 20]
        pips = [6, 10, 14, 18]
        wrist = landmarks[0]

        for tip, pip in zip(tips, pips):
            tip_dist = np.linalg.norm([
                landmarks[tip].x - wrist.x,
                landmarks[tip].y - wrist.y
            ])

            pip_dist = np.linalg.norm([
                landmarks[pip].x - wrist.x,
                landmarks[pip].y - wrist.y
            ])

            if tip_dist > pip_dist:
                return 0

        return 1

    # --- Callback ---
    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        result = self.landmarker.detect(mp_image)

        output_msg = Int8()
        output_msg.data = 0

        if result.hand_landmarks:
            fist = self.is_fist(result.hand_landmarks[0])
            output_msg.data = fist

        self.publisher_.publish(output_msg)


def main(args=None):
    rclpy.init(args=args)

    node = HandFistNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
