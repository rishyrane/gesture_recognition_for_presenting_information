# Import necessary libraries
from flask import Flask, render_template, Response
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
from flask_socketio import SocketIO

# Initialize the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socket = SocketIO(app)

# Define a global variable to store the gesture name
gesture_name = ""

camera = cv2.VideoCapture(0)

def gen_frames():
    global gesture_name  # access the global gesture_name variable
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

                # if fingers are in a horizontal position, it is a swipe gesture
                if x1 < 300:  # swipe left
                    cv2.putText(frame, 'SWIPE LEFT', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    gesture_name = 'SWIPE LEFT'
                elif x1 > 500:  # swipe right
                    cv2.putText(frame, 'SWIPE RIGHT', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    gesture_name = 'SWIPE RIGHT'
                elif y1 < 200:  # swipe up
                    cv2.putText(frame, 'SWIPE UP', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    gesture_name = 'SWIPE UP'
                elif y1 > 400:  # swipe down
                    cv2.putText(frame, 'SWIPE DOWN', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    gesture_name = 'SWIPE DOWN'

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@socket.on('gesture')
def handle_gesture():
    # Emit the "gesture" event along with the updated gesture_name value
    socket.emit('gesture', {'gesture_name': gesture_name})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')