import face_recognition
import numpy as np

def compare_faces_with_similarity(image1_path, image2_path):
    # 加载两张图片
    image1 = face_recognition.load_image_file(image1_path)
    image2 = face_recognition.load_image_file(image2_path)
    
    # 提取人脸特征向量（128维）
    face_encodings1 = face_recognition.face_encodings(image1)
    face_encodings2 = face_recognition.face_encodings(image2)
    
    # 确保每张图片至少包含一张人脸
    if len(face_encodings1) == 0:
        print("No faces found in the first image.")
        return
    if len(face_encodings2) == 0:
        print("No faces found in the second image.")
        return

    # 假设每张图片只检测到一张人脸，取第一张脸的特征向量
    face_encoding1 = face_encodings1[0]
    face_encoding2 = face_encodings2[0]
    
    # 计算欧几里得距离
    distance = np.linalg.norm(face_encoding1 - face_encoding2)
    
    # 设置一个相似度度量标准
    similarity_threshold = 0.6  # 通常阈值在0.6左右，越小越严格
    is_match = distance < similarity_threshold

    # 输出结果
    result = {
        "image1_encoding": face_encoding1.tolist(),  # 将ndarray转换为列表便于打印
        "image2_encoding": face_encoding2.tolist(),
        "euclidean_distance": distance,
        "is_match": is_match
    }
    
    return result


# 使用图像文件路径调用函数
image1_path = "person1.jpg"  # 第一张图片路径
image2_path = "person2.jpg"  # 第二张图片路径

# 比较人脸并获取相似度和特征向量
result = compare_faces_with_similarity(image1_path, image2_path)

# 输出结果
if result:
    print("Feature Vector of Image 1 (128D):", result["image1_encoding"])
    print("Feature Vector of Image 2 (128D):", result["image2_encoding"])
    print("Euclidean Distance (Similarity):", result["euclidean_distance"])
    if result["is_match"]:
        print("The faces are a match!")
    else:
        print("The faces are not a match!")
