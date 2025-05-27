# pose_estimation.py
# Extracts keypoints from video or camera using MediaPipe.

import argparse
import cv2
import mediapipe as mp
import json
import os


def extract_poses(input_path, output_path, use_camera=False):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0 if use_camera else input_path)

    frame_idx = 0
    all_keypoints = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        keypoints = []
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                keypoints.append({
                    'x': lm.x,
                    'y': lm.y,
                    'z': lm.z,
                    'visibility': lm.visibility
                })
        all_keypoints.append({
            'frame': frame_idx,
            'keypoints': keypoints
        })
        frame_idx += 1

    cap.release()
    pose.close()

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_keypoints, f, ensure_ascii=False, indent=2)
    print(f"Pose extraction complete. Output: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Extract 2D pose keypoints from video or camera using MediaPipe.")
    parser.add_argument('--input', help='Path to input video file (ignored if --camera is set)')
    parser.add_argument('--output', default='keypoints.json', help='Output JSON file for keypoints')
    parser.add_argument('--camera', action='store_true', help='Use camera input instead of video file')
    args = parser.parse_args()

    if not args.camera and (not args.input or not os.path.exists(args.input)):
        print('Input video file not found. Use --camera for live input.')
        return

    extract_poses(args.input, args.output, use_camera=args.camera)


if __name__ == '__main__':
    main() 