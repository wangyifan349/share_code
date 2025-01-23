from transformers import BertModel, BertTokenizer
import torch
import faiss
import numpy as np

# 初始化BERT模型和tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# 问题-答案对，包含真实的OpenCV代码块
# 模拟包含更详细OpenCV代码片段的简短问题
qa_dict = {
    "read image":
        """```python
        import cv2
        # Read and display an image
        image = cv2.imread('image.jpg')
        if image is None:
            print("Error: Image not found.")
        else:
            cv2.imshow('Image', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        ```""",
    
    "grayscale conversion":
        """```python
        import cv2
        # Read the image
        image = cv2.imread('image.jpg')
        if image is None:
            print("Error: Image not found.")
        else:
            # Convert image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.imshow('Grayscale Image', gray_image)
            cv2.imwrite('grayscale_image.jpg', gray_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        ```""",
    
    "edge detection Canny":
        """```python
        import cv2
        # Read the image
        image = cv2.imread('image.jpg')
        if image is None:
            print("Error: Image not found.")
        else:
            # Convert to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Canny edge detection
            edges = cv2.Canny(gray_image, 100, 200)
            cv2.imshow('Canny Edges', edges)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        ```""",
    
    "SIFT feature detection":
        """```python
        import cv2
        # Read the image
        image = cv2.imread('image.jpg')
        if image is None:
            print("Error: Image not found.")
        else:
            # Convert to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Initialize SIFT detector
            sift = cv2.SIFT_create()
            # Detect SIFT features
            keypoints, descriptors = sift.detectAndCompute(gray_image, None)
            # Draw keypoints on the image
            sift_image = cv2.drawKeypoints(gray_image, keypoints, image)
            cv2.imshow('SIFT Features', sift_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        ```"""
}

# 使用上面的代码片段初始化和搜索功能
"""
qa_dict = {
    "What is the capital of France?": "The capital of France is Paris.",
    "How does gravity work?": "Gravity is a force by which a planet or other body draws objects toward its center.",
    "What is the speed of light?": "The speed of light is approximately 299,792,458 meters per second.",
    "Who discovered gravity?": "Gravity was discovered by Sir Isaac Newton.",
    "What is the largest mammal on Earth?": "The blue whale is the largest mammal on Earth."
}
"""


import numpy as np
def cosine_similarity(vec1, vec2):
    """
    计算两个向量之间的余弦相似度。    
    参数:
    - vec1: numpy数组或列表，表示第一个向量。
    - vec2: numpy数组或列表，表示第二个向量。
    返回值:
    - sim: 浮点数，表示两个向量之间的余弦相似度。
           范围在[-1, 1]，其中1表示完全相同，0表示正交，-1表示完全相反。
    """
    # 将输入转换为numpy数组
    vec1 = np.array(vec1)
    vec2 = np.array(vec2) 
    # 计算向量的点积
    dot_product = np.dot(vec1, vec2)
    # 计算向量的范数
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    # 防止零向量导致的除以零的错误
    if norm1 == 0 or norm2 == 0:
        return 0.0
    # 计算余弦相似度
    sim = dot_product / (norm1 * norm2)
    return sim
"""
# 示例使用
vec_a = [1, 2, 3]
vec_b = [4, 5, 6]
similarity = cosine_similarity(vec_a, vec_b)
print(f"Cosine Similarity: {similarity:.4f}")
"""


# 获取句子向量
def get_sentence_embedding(sentence):
    inputs = tokenizer(sentence, return_tensors='pt', padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy()

# 为每个问题计算BERT嵌入
questions = list(qa_dict.keys())
question_embeddings = np.array([get_sentence_embedding(question) for question in questions])

# 创建Faiss索引
dimension = question_embeddings.shape[1]
faiss.normalize_L2(question_embeddings)
index = faiss.IndexFlatIP(dimension)
index.add(question_embeddings)

# 搜索函数
def search(query, top_k=1):
    query_embedding = get_sentence_embedding(query)
    query_embedding = np.expand_dims(query_embedding, axis=0)
    faiss.normalize_L2(query_embedding)

    distances, indices = index.search(query_embedding, top_k)
    
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        matched_question = questions[idx]
        answer = qa_dict[matched_question]
        results.append({
            "matched_question": matched_question,
            "answer": answer,
            "similarity": distance
        })
    return results

# 测试搜索功能
query = "How do I read an image file with OpenCV?"
top_k = 2
results = search(query, top_k=top_k)

# 打印结果
for i, result in enumerate(results):
    print(f"Rank {i + 1}:")
    print(f"  Matched Question: {result['matched_question']}")
    print(f"  Match Score: {result['similarity']:.4f}")
    print(f"  Answer:\n{result['answer']}")
    print("-" * 50)
