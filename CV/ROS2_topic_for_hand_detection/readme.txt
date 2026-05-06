Hand Fist Detection (ROS2 + MediaPipe)

Этот проект представляет собой ROS2-ноду для распознавания сжатого кулака с помощью MediaPipe.

Нода:

подписывается на изображение с камеры (/image_raw)
определяет, сжат кулак или нет
публикует результат в топик /hand/fist_state

Требования:

ROS2 Humble
Python 3.8+
Веб-камера

Установка:

Создать workspace:
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
Скопировать пакет:
Поместите папку hand_gesture в директорию src
Установить зависимости:
pip install -r requirements.txt
sudo apt update
sudo apt install ros-humble-cv-bridge

Модель MediaPipe:

Скачайте модель:
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task

Поместите файл в:
~/ros2_ws/hand_landmarker.task

Либо укажите путь к модели в коде.

Сборка:

cd ~/ros2_ws
colcon build

Активация:

source install/setup.bash

Запуск камеры:

ros2 run v4l2_camera v4l2_camera_node

Если нужно выбрать камеру:
ros2 run v4l2_camera v4l2_camera_node --ros-args -p video_device:=/dev/video3

Запуск ноды:

ros2 run hand_gesture fist_checker

Просмотр результата:

ros2 topic echo /hand/fist_state

Значения:
0 — ладонь
1 — кулак

Просмотр изображения:

ros2 run image_tools showimage --ros-args -r image:=/image_raw