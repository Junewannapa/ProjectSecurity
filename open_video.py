# open_video.py

import cv2
import sys

def play_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file.")
        sys.exit(1)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow("Hidden Video", frame)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python open_video.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    play_video(video_path)
