import dlib
import cv2
import numpy as np

def load_models(predictor_path, face_rec_model_path):
    print("Loading models...")
    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_path)
    face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)
    print("Models loaded successfully.")
    return detector, shape_predictor, face_rec_model

def detect_and_display(image, detector, shape_predictor, face_rec_model, window_name="Face Detection"):
    print("Detecting faces...")
    faces = detector(image, 1)
    print(f"Detected {len(faces)} faces.")
    descriptors = []
    for i, face in enumerate(faces):
        print(f"Processing face {i+1}...")
        left, top, right, bottom = face.left(), face.top(), face.right(), face.bottom()
        cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
        shape = shape_predictor(image, face)
        for n in range(68):
            x = shape.part(n).x
            y = shape.part(n).y
            cv2.circle(image, (x, y), 2, (255, 0, 0), -1)
            cv2.putText(image, str(n), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 255), 1)
        
        face_descriptor = face_rec_model.compute_face_descriptor(image, shape)
        descriptors.append(np.array(face_descriptor))
        print(f"Computed descriptor for face {i+1}: {face_descriptor[:5]}... (truncated)")
    
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Detection and display completed.")
    return descriptors

def calculate_similarity(face_descriptor1, face_descriptor2):
    print("Calculating similarity...")
    distance = np.linalg.norm(face_descriptor1 - face_descriptor2)
    print(f"Euclidean distance between the two faces: {distance}")
    if distance < 0.6:
        print("Faces are likely the same person.")
    else:
        print("Faces are likely different people.")
    return distance

# 示例用法：
predictor_path = "shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"
detector, shape_predictor, face_rec_model = load_models(predictor_path, face_rec_model_path)

image_path1 = "example1.jpg"
image1 = cv2.imread(image_path1)
descriptors1 = detect_and_display(image1, detector, shape_predictor, face_rec_model, "Image 1")

image_path2 = "example2.jpg"
image2 = cv2.imread(image_path2)
descriptors2 = detect_and_display(image2, detector, shape_predictor, face_rec_model, "Image 2")

# 假设每张图片中只检测到一个人脸
if descriptors1 and descriptors2:
    distance = calculate_similarity(descriptors1[0], descriptors2[0])
