import cv2

def sift_feature_matching(img1_path, img2_path, display_matches=True):  # SIFT特征提取与匹配
    img1, img2 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE), cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    sift, bf = cv2.SIFT_create(), cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    kp1, des1 = sift.detectAndCompute(img1, None); kp2, des2 = sift.detectAndCompute(img2, None)
    matches = sorted(bf.match(des1, des2), key=lambda x: x.distance)  # 匹配+排序
    if display_matches: cv2.imshow('SIFT Matches', cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None)); cv2.waitKey(0); cv2.destroyAllWindows()
    return matches
def surf_feature_matching(img1_path, img2_path, display_matches=True, hessian_threshold=400):  # SURF特征提取与匹配
    img1, img2 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE), cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    surf, bf = cv2.xfeatures2d.SURF_create(hessianThreshold=hessian_threshold), cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    kp1, des1 = surf.detectAndCompute(img1, None); kp2, des2 = surf.detectAndCompute(img2, None)
    matches = sorted(bf.match(des1, des2), key=lambda x: x.distance)
    if display_matches: cv2.imshow('SURF Matches', cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None)); cv2.waitKey(0); cv2.destroyAllWindows()
    return matches
def flann_sift_matching(img1_path, img2_path):  # 使用FLANN进行SIFT特征匹配
    img1, img2 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE), cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    sift = cv2.SIFT_create(); kp1, des1 = sift.detectAndCompute(img1, None); kp2, des2 = sift.detectAndCompute(img2, None)
    flann = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), dict(checks=50))
    matches = flann.knnMatch(des1, des2, k=2)
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]  # 筛选优质匹配
    cv2.imshow("FLANN SIFT Matches", cv2.drawMatchesKnn(img1, kp1, img2, kp2, [good_matches], None, flags=2))
    cv2.waitKey(0); cv2.destroyAllWindows()
def fast_keypoints_detection(img_path, draw_keypoints=True):  # FAST角点检测
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    fast = cv2.FastFeatureDetector_create()
    keypoints = fast.detect(img, None)
    if draw_keypoints: cv2.imshow("FAST Keypoints", cv2.drawKeypoints(img, keypoints, None, color=(255, 0, 0))); cv2.waitKey(0); cv2.destroyAllWindows()
    return keypoints
def harris_corner_detection(img_path):  # Harris角点检测
    img, gray = cv2.imread(img_path), cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    corners = cv2.cornerHarris(gray, 2, 3, 0.04)
    img[corners > 0.01 * corners.max()] = [0, 0, 255]  # 红色标记角点
    cv2.imshow("Harris Corners", img); cv2.waitKey(0); cv2.destroyAllWindows()
def akaze_matching(img1_path, img2_path):  # AKAZE特征提取与匹配
    img1, img2 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE), cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
    akaze, bf = cv2.AKAZE_create(), cv2.BFMatcher(cv2.NORM_HAMMING)
    kp1, des1 = akaze.detectAndCompute(img1, None); kp2, des2 = akaze.detectAndCompute(img2, None)
    matches = sorted(bf.match(des1, des2), key=lambda x: x.distance)
    cv2.imshow("AKAZE Matches", cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None, flags=2)); cv2.waitKey(0); cv2.destroyAllWindows()
def hog_descriptor(img_path):  # HOG特征提取
    img, hog = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE), cv2.HOGDescriptor()
    features = hog.compute(img)
    print(f"HOG Feature Length: {features.shape}")
    return features

# 加载两张图像（假设图像路径为 image1.jpg 和 image2.jpg）
img1_path, img2_path = 'image1.jpg', 'image2.jpg'
# 进行 SIFT 匹配
sift_feature_matching(img1_path, img2_path)
# 使用 SURF 匹配
surf_feature_matching(img1_path, img2_path)
# FAST 关键点检测
fast_keypoints_detection(img1_path)
# Harris 角点检测
harris_corner_detection(img1_path)
# AKAZE 匹配
akaze_matching(img1_path, img2_path)
# 提取 HOG 描述符
hog_descriptor(img1_path)


import cv2
import dlib
import numpy as np
from imutils import face_utils

def extract_facial_landmarks(image_path, predictor_path):
    # Initialize dlib's face detector (HOG-based) and create the facial landmark predictor
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)

    # Load the input image, convert it to grayscale
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = detector(gray)

    # Dictionary to hold facial landmark positions
    landmarks_dict = {}

    for (_, rect) in enumerate(faces):
        # Determine the facial landmarks for the face region
        shape = predictor(gray, rect)
        shape_np = face_utils.shape_to_np(shape)

        # Loop over the facial landmarks and map them to their corresponding part names
        for (name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
            landmarks_dict[name] = shape_np[i:j]

    # Display the image with landmarks
    for (name, points) in landmarks_dict.items():
        for (x, y) in points:
            cv2.circle(img, (x, y), 2, (0, 255, 0), -1)

    cv2.imshow("Facial Landmarks", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return landmarks_dict

def compute_face_descriptor(image_path, predictor_path, face_rec_model_path):
    # Initialize dlib's face detector and create models for facial landmarks and face recognition
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)
    face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)

    # Load the input image, convert it to grayscale
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = detector(gray)
    descriptors = []

    for (_, rect) in enumerate(faces):
        # Compute landmarks and 128D descriptor
        shape = predictor(gray, rect)
        descriptor = face_rec_model.compute_face_descriptor(img, shape)
        descriptors.append(np.array(descriptor))

    return descriptors

# Define the paths to the model files and the input image
predictor_path = "shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"
image_path = "image.jpg"

# Extract facial landmarks and compute face descriptors
landmarks = extract_facial_landmarks(image_path, predictor_path)
descriptors = compute_face_descriptor(image_path, predictor_path, face_rec_model_path)

# Output the facial landmarks and feature descriptors
print("Facial Landmarks:")
for part, points in landmarks.items():
    print(f"{part}: {points}")

print("\n128D Face Descriptors:")
for i, desc in enumerate(descriptors):
    print(f"Descriptor {i+1}: {desc}")




  
      
