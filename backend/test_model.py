import os
import cv2
import numpy as np
import tensorflow as tf
import json
from mediapipe.python.solutions import pose as mp_pose
from PIL import Image

# Paths to model and labels
MODEL_PATH = 'yoga_pose_model.h5'
LABELS_PATH = 'yoga_pose_model_labels.json'
TEST_IMAGES_DIR = 'yoga_dataset/test/Dolphin_Pose_or_Ardha_Pincha_Mayurasana_'  # Add your test images here

# Load model
model = tf.keras.models.load_model(MODEL_PATH)

# Load class labels
with open(LABELS_PATH, 'r') as f:
    class_names = json.load(f)['classes']

# Initialize MediaPipe Pose
pose_detector = mp_pose.Pose(static_image_mode=True)

def extract_keypoints(image_path):
    img = cv2.imread(image_path)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose_detector.process(rgb)

    if results.pose_landmarks:
        keypoints = []
        for landmark in results.pose_landmarks.landmark:
            keypoints.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
        return np.array(keypoints)
    else:
        return None

def predict_pose(image_path):
    keypoints = extract_keypoints(image_path)

    if keypoints is None:
        print(f"[✘] No landmarks detected in: {image_path}")
        return

    keypoints_norm = keypoints / np.linalg.norm(keypoints)
    keypoints_norm = keypoints_norm.reshape(1, -1)

    prediction = model.predict(keypoints_norm, verbose=0)
    predicted_idx = np.argmax(prediction)
    confidence = prediction[0][predicted_idx]

    print(f"[✓] {os.path.basename(image_path)} ➜ Pose: {class_names[predicted_idx]} (Confidence: {confidence*100:.2f}%)")

# Run predictions on all test images
if __name__ == '__main__':
    for filename in os.listdir(TEST_IMAGES_DIR):
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            image_path = os.path.join(TEST_IMAGES_DIR, filename)
            predict_pose(image_path)
