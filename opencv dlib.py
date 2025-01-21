import cv2
import numpy as np

def sift_feature_matching(img1_path, img2_path):
    # 读取图像
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    # 检查图像是否成功加载
    if img1 is None or img2 is None:
        print("Error: Could not load images.")
        return
    # 创建SIFT检测器
    sift = cv2.SIFT_create()
    # 检测关键点和描述符
    keypoints1, descriptors1 = sift.detectAndCompute(img1, None)
    keypoints2, descriptors2 = sift.detectAndCompute(img2, None)
    # 使用BFMatcher进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    # 匹配描述符
    matches = bf.match(descriptors1, descriptors2)
    # 按照距离排序特征匹配（距离越小越好）
    matches = sorted(matches, key=lambda x: x.distance)
    # 绘制前10个匹配项
    img_matches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # 显示匹配结果
    cv2.imshow('SIFT Feature Matching', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# 调用函数，传入两张待匹配的图像路径
sift_feature_matching('image1.jpg', 'image2.jpg')

import cv2
import numpy as np
def surf_feature_matching(img1_path, img2_path):
    # 读取图像
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        print("Error: Could not load images.")
        return
    # 创建SURF检测器
    surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400)
    # 检测关键点和描述符
    keypoints1, descriptors1 = surf.detectAndCompute(img1, None)
    keypoints2, descriptors2 = surf.detectAndCompute(img2, None)
    # 使用BFMatcher进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    # 按照距离排序特征匹配
    matches = sorted(matches, key=lambda x: x.distance)
    # 绘制前10个匹配项
    img_matches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # 显示匹配结果
    cv2.imshow('SURF Feature Matching', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 调用函数，传入两张待匹配的图像路径
surf_feature_matching('image1.jpg', 'image2.jpg')

import cv2
import numpy as np
def orb_feature_matching(img1_path, img2_path):
    # 读取图像
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        print("Error: Could not load images.")
        return

    # 创建ORB检测器
    orb = cv2.ORB_create()
    # 检测关键点和描述符
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)
    # 使用BFMatcher进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    # 按照距离排序特征匹配
    matches = sorted(matches, key=lambda x: x.distance)
    # 绘制前10个匹配项
    img_matches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # 显示匹配结果
    cv2.imshow('ORB Feature Matching', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 调用函数，传入两张待匹配的图像路径
orb_feature_matching('image1.jpg', 'image2.jpg')


import cv2
import numpy as np
def brief_feature_matching(img1_path, img2_path):
    # 读取图像
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        print("Error: Could not load images.")
        return
    # 使用FAST检测关键点
    fast = cv2.FastFeatureDetector_create()
    keypoints1 = fast.detect(img1, None)
    keypoints2 = fast.detect(img2, None)
    # 使用BRIEF提取描述符
    brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
    keypoints1, descriptors1 = brief.compute(img1, keypoints1)
    keypoints2, descriptors2 = brief.compute(img2, keypoints2)
    # 使用BFMatcher进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    # 按照距离排序特征匹配
    matches = sorted(matches, key=lambda x: x.distance)
    # 绘制前10个匹配项
    img_matches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # 显示匹配结果
    cv2.imshow('BRIEF Feature Matching', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# 调用函数，传入两张待匹配的图像路径
brief_feature_matching('image1.jpg', 'image2.jpg')

import cv2
import numpy as np
def fast_feature_matching(img1_path, img2_path):
    # 读取图像
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        print("Error: Could not load images.")
        return
    # 创建FAST检测器
    fast = cv2.FastFeatureDetector_create()
    # 检测关键点
    keypoints1 = fast.detect(img1, None)
    keypoints2 = fast.detect(img2, None)
    # 使用ORB提取描述符（因为FAST只检测关键点）
    orb = cv2.ORB_create()
    keypoints1, descriptors1 = orb.compute(img1, keypoints1)
    keypoints2, descriptors2 = orb.compute(img2, keypoints2)
    # 使用BFMatcher进行特征匹配
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    # 按照距离排序特征匹配
    matches = sorted(matches, key=lambda x: x.distance)
    # 绘制前10个匹配项
    img_matches = cv2.drawMatches(img1, keypoints1, img2, keypoints2, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    # 显示匹配结果
    cv2.imshow('FAST Feature Matching', img_matches)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# 调用函数，传入两张待匹配的图像路径
fast_feature_matching('image1.jpg', 'image2.jpg')


import cv2
import numpy as np

def affine_transformation(img_path):
    img = cv2.imread(img_path)
    rows, cols, ch = img.shape
    pts1 = np.float32([[50, 50], [200, 50], [50, 200]])
    pts2 = np.float32([[10, 100], [200, 50], [100, 250]])
    M = cv2.getAffineTransform(pts1, pts2)
    dst = cv2.warpAffine(img, M, (cols, rows))
    cv2.imshow('Affine Transformation', dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

affine_transformation('image.jpg')


import cv2

def face_detection(img_path):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
    cv2.imshow('Face Detection', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
face_detection('face.jpg')



import cv2
def edge_detection(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blurred, 100, 200)
    cv2.imshow('Edge Detection', edges)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
edge_detection('image.jpg')



import cv2
def color_space_conversion(img_path):
    img = cv2.imread(img_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow('HSV Image', hsv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
color_space_conversion('image.jpg')







import cv2

def capture_video_from_camera():
    cap = cv2.VideoCapture(0)  # 0表示默认摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Camera Capture', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按'q'退出
            break
    cap.release()
    cv2.destroyAllWindows()

capture_video_from_camera()




import cv2

def record_video(output_path='output.avi'):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow('Recording', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()

record_video()




import cv2

def play_video_from_file(video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video Playback', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

play_video_from_file('video.avi')




import cv2
import numpy as np
import pyautogui
def record_screen(output_path='screen_record.avi', fps=20.0, screen_size=(1920, 1080)):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, screen_size)
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)
        cv2.imshow('Screen Recording', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    out.release()
    cv2.destroyAllWindows()
record_screen()




import cv2
import dlib

def detect_faces(img_path):
    detector = dlib.get_frontal_face_detector()
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for i, face in enumerate(faces):
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        print(f"Face {i+1}: Position (x, y, w, h) = ({x}, {y}, {w}, {h})")
    cv2.imshow('Face Detection', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

detect_faces('face.jpg')



import cv2
import dlib

def detect_landmarks(img_path, model_path='shape_predictor_68_face_landmarks.dat'):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for i, face in enumerate(faces):
        landmarks = predictor(gray, face)
        print(f"Face {i+1} landmarks:")
        for n in range(68):
            x, y = landmarks.part(n).x, landmarks.part(n).y
            cv2.circle(img, (x, y), 2, (0, 255, 0), -1)
            print(f"  Landmark {n+1}: (x, y) = ({x}, {y})")
    cv2.imshow('Facial Landmarks', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

detect_landmarks('face.jpg')





import cv2
import dlib
import numpy as np

def recognize_faces(img_path, model_path='dlib_face_recognition_resnet_model_v1.dat'):
    detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    face_rec_model = dlib.face_recognition_model_v1(model_path)
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for i, face in enumerate(faces):
        shape = shape_predictor(gray, face)
        face_descriptor = face_rec_model.compute_face_descriptor(img, shape)
        print(f"Face {i+1} descriptor (first 5 elements): {face_descriptor[:5]}")
    return face_descriptor

recognize_faces('face.jpg')




import cv2
import dlib

def align_face(img_path, model_path='shape_predictor_68_face_landmarks.dat'):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(model_path)
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    for i, face in enumerate(faces):
        shape = predictor(gray, face)
        aligned_face = dlib.get_face_chip(img, shape)
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        print(f"Face {i+1}: Original position (x, y, w, h) = ({x}, {y}, {w}, {h})")
        cv2.imshow(f'Aligned Face {i+1}', aligned_face)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

align_face('face.jpg')



