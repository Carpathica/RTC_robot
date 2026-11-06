"""Open and display an RTSP camera stream with OpenCV.

Example (PowerShell):
  $env:CAMERA_PASSWORD = 'your-password'
  python examples/rtsp_preview.py --host 192.168.1.50 --port 554 --user admin --path Streaming/Channels/101
"""

from __future__ import annotations

import argparse
import os
import time
from urllib.parse import quote

import cv2


def build_rtsp_url(host: str, port: int, user: str, password: str, path: str) -> str:
    """Build an RTSP URL and safely escape special characters in credentials."""
    credentials = f"{quote(user, safe='')}:{quote(password, safe='')}@" if user else ""
    return f"rtsp://{credentials}{host}:{port}/{path.lstrip('/')}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Show an RTSP stream in an OpenCV window.")
    parser.add_argument("--host", required=True, help="Camera IP address or hostname")
    parser.add_argument("--port", type=int, default=554, help="RTSP port; default: 554")
    parser.add_argument("--user", default="", help="Camera user name")
    parser.add_argument("--password", default=os.getenv("CAMERA_PASSWORD", ""), help="Password; prefer CAMERA_PASSWORD")
    parser.add_argument("--path", required=True, help="RTSP path, for example Streaming/Channels/101")
    parser.add_argument("--reconnect-delay", type=float, default=3.0)
    args = parser.parse_args()

    if args.user and not args.password:
        parser.error("Set CAMERA_PASSWORD or pass --password.")

    url = build_rtsp_url(args.host, args.port, args.user, args.password, args.path)
    print(f"Connecting to RTSP camera at {args.host}:{args.port}. Press q or Esc to exit.")
    cv2.namedWindow("RTSP preview", cv2.WINDOW_NORMAL)

    capture: cv2.VideoCapture | None = None
    try:
        while True:
            if capture is None:
                capture = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
                if not capture.isOpened():
                    capture.release()
                    capture = None
                    print(f"Connection failed; retrying in {args.reconnect_delay:g} s")
                    time.sleep(args.reconnect_delay)
                    continue

            received, frame = capture.read()
            if not received:
                capture.release()
                capture = None
                print(f"Stream interrupted; reconnecting in {args.reconnect_delay:g} s")
                continue

            cv2.imshow("RTSP preview", frame)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        if capture is not None:
            capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
