import cv2
import numpy as np
import mediapipe as mp
import time
from keyboards_back.Keyboard import Keyboard
from keyboards_back.HeadMovingKeyboard import HeadMovingKeyboard

def main():
    pTime = 0

    cap = cv2.VideoCapture(0)
    #detector = htm.handDetector(maxHands=1)
    classic_keyboard = Keyboard()
    headMovingKeyboard = HeadMovingKeyboard(classic_keyboard)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    mp_drawing = mp.solutions.drawing_utils

    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

   

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (1080, 768))
        results = face_mesh.process(img)
        #img = detector.findHands(img)
        #lmList = detector.findPosition(img)

        img_h, img_w, img_c = img.shape
        face_3d = []
        face_2d = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199:
                        if idx == 1:
                            nose_2d = (lm.x * img_w, lm.y * img_h)
                            nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 3000)

                        x, y = int(lm.x * img_w), int(lm.y * img_h)

                        # Get the 2D Coordinates
                        face_2d.append([x, y])

                        # Get the 3D Coordinates
                        face_3d.append([x, y, lm.z])       
            
                # Convert it to the NumPy array
                face_2d = np.array(face_2d, dtype=np.float64)

                # Convert it to the NumPy array
                face_3d = np.array(face_3d, dtype=np.float64)

                # The camera matrix
                focal_length = 1 * img_w

                cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                        [0, focal_length, img_w / 2],
                                        [0, 0, 1]])

                # The distortion parameters
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                # Solve PnP
                success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

                # Get rotational matrix
                rmat, jac = cv2.Rodrigues(rot_vec)

                # Get angles
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                # Get the y rotation degree
                x = angles[0] * 360
                y = angles[1] * 360
                z = angles[2] * 360

             

                if y < -8:
                    text = "Looking Left"
                elif y > 8:
                    text = "Looking Right"
                elif x < -8:
                    text = "Looking Down"
                elif x > 8:
                    text = "Looking Up"
                else:
                    text = "Forward"

                
                cv2.putText(img, text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

                angles2 = [x, y]

                headMovingKeyboard.update(img, angles2)
                #handMovingKeyboard.update(img, lmList)

                isCalibrated = " "
                if(headMovingKeyboard.is_calibrated==True):
                    isCalibrated="Calibrated"
                else:
                    isCalibrated="False"

                cv2.putText(img, isCalibrated, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

              

                cv2.putText(img, str(headMovingKeyboard.angles[0]), (600, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                cv2.putText(img, str(headMovingKeyboard.angles[1]), (600, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

                img = classic_keyboard.draw_update(img, 10, 100, 30, 30)

                ###FPS###
                cTime = time.time()
             
              
                fps = 1/(cTime - pTime)

                pTime = cTime

                ###DRAW RESULT###
                img = headMovingKeyboard.drawResult(img, 600, 600)
                #################
        
                cv2.putText(img, str(int(fps)),(0,15), cv2.FONT_HERSHEY_PLAIN, 1 ,(255,0,255), 2)
                cv2.imshow("Image", img)
                cv2.waitKey(1)
                #########

if __name__ == '__main__':
    main()

