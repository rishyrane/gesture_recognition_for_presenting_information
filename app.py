#Import necessary libraries
from flask import Flask, render_template, Response
import cv2
from cvzone.HandTrackingModule import HandDetector
import math

#Initialize the Flask app
app = Flask(__name__)

camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            # Create a HandDetector object
            detector = HandDetector(detectionCon=0.8, maxHands=1)
            # Detect hands in the frame
            frame = cv2.flip(frame, 1)  # flip the frame horizontally
            frame = detector.findHands(frame)
            # Get the landmarks for the hand detected
            lmList, bbox = detector.findPosition(frame)

            # Check if a hand is detected
            if lmList:
                # Get the coordinates of the index and middle fingers
                x1, y1 = lmList[8][1:]
                x2, y2 = lmList[12][1:]

                # Calculate the distance between the index and middle fingers
                length = math.hypot(x2 - x1, y2 - y1)

                # Detect gestures based on finger positions
                if length < 40:  # if fingers are close together, it is a zoom-in gesture
                    cv2.putText(frame, 'ZOOM IN', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                elif length > 150:  # if fingers are far apart, it is a zoom-out gesture
                    cv2.putText(frame, 'ZOOM OUT', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                else:  # if fingers are in a horizontal position, it is a swipe gesture
                    if x1 < 300:  # swipe left
                        cv2.putText(frame, 'SWIPE LEFT', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    elif x1 > 500:  # swipe right
                        cv2.putText(frame, 'SWIPE RIGHT', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    elif y1 < 200:  # swipe up
                        cv2.putText(frame, 'SWIPE UP', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    elif y1 > 400:  # swipe down
                        cv2.putText(frame, 'SWIPE DOWN', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
