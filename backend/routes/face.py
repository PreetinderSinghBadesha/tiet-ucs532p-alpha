import os
import cv2
import dlib
import numpy as np
import base64
from flask import Blueprint, request, jsonify, current_app, send_from_directory

face_bp = Blueprint('face', __name__)

# Initialize Dlib components
detector = dlib.get_frontal_face_detector()
predictor = None

def get_predictor():
    global predictor
    if predictor is None:
        model_path = os.path.join(current_app.root_path, 'models', 'shape_predictor_68_face_landmarks.dat')
        if os.path.exists(model_path):
            try:
                predictor = dlib.shape_predictor(model_path)
            except Exception as e:
                print(f"Error loading predictor: {e}")
    return predictor

@face_bp.route('/face-detect', methods=['POST'])
def face_detect():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    try:
        # 1. Read image into memory
        file_bytes = file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'message': 'Invalid image file (corruption?)'}), 400
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Dlib face detection
        faces = detector(gray)
        
        cropped_face_base64 = None
        landmark_predictor = get_predictor()
        
        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 3. Landmark detection
            if landmark_predictor:
                landmarks = landmark_predictor(gray, face)
                for n in range(0, 68):
                    lx = landmarks.part(n).x
                    ly = landmarks.part(n).y
                    cv2.circle(img, (lx, ly), 2, (0, 0, 255), -1)
            
            # 4. Crop and encode first face detected to Base64
            if cropped_face_base64 is None:
                padding = 20
                x1, y1 = max(0, x - padding), max(0, y - padding)
                x2, y2 = min(img.shape[1], x + w + padding), min(img.shape[0], y + h + padding)
                face_roi = img[y1:y2, x1:x2]
                
                _, buffer = cv2.imencode('.jpg', face_roi)
                cropped_face_base64 = base64.b64encode(buffer).decode('utf-8')

        # Optional: Save for debugging (no longer critical for frontend)
        # cv2.imwrite(os.path.join(current_app.config['UPLOAD_FOLDER'], 'last_processed.jpg'), img)
        
        status_msg = f"Detected {len(faces)} face(s)."
        if not landmark_predictor:
            status_msg += " (Landmarks model loading...)"
        
        return jsonify({
            'message': status_msg,
            'cropped_face_base64': f"data:image/jpeg;base64,{cropped_face_base64}" if cropped_face_base64 else None
        })

    except Exception as e:
        print(f"Backend processing error: {e}")
        return jsonify({'message': f'System error: {str(e)}'}), 500

@face_bp.route('/cropped_face.jpg')
def serve_cropped_face():
    # Keep legacy route for manual uploads if still used, but favor base64
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], 'cropped_face.jpg')
