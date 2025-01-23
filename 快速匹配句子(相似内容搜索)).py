from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 加载句子嵌入模型
model = SentenceTransformer('all-MiniLM-L6-v2')  # 一个轻量级预训练 Sentence-BERT 模型

# 存储的长句子列表
sentences = [
    "I love natural language processing and machine learning.",
    "Artificial intelligence and deep learning are revolutionizing many industries.",
    "Natural language processing is a subset of artificial intelligence.",
    "Python is a great programming language for data analysis and machine learning.",
    "The future of AI lies in more ethical and explainable artificial intelligence systems.",
]

# 生成句子嵌入
sentence_embeddings = model.encode(sentences)

# 用户输入句子
user_sentence = input("Enter your sentence: ")
user_embedding = model.encode([user_sentence])

# 计算余弦相似度
cosine_sim = cosine_similarity(user_embedding, sentence_embeddings)

# 找到最相似的句子
similarities = cosine_sim[0]
top_indices = similarities.argsort()[::-1][:3]  # 取前3个
for i in top_indices:
    print(f"'{sentences[i]}' with similarity score: {similarities[i]:.4f}")





from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# 存储一些长句子作为数据
sentences = [
    "I love natural language processing and machine learning.",
    "Artificial intelligence and deep learning are revolutionizing many industries.",
    "Natural language processing is a subset of artificial intelligence.",
    "Python is a great programming language for data analysis and machine learning.",
    "The future of AI lies in more ethical and explainable artificial intelligence systems.",
]

def find_most_similar_sentence(user_input, sentences, topn=3):
    """
    根据用户输入，找到与存储句子最相似的句子。

    参数：
    - user_input: 用户输入的句子
    - sentences: 存储的句子列表
    - topn: 返回的相似句子数量
    返回：
    - 与输入句子最相似的句子及其相似度分数
    """
    # 将用户输入的句子合并到句子列表中
    all_sentences = sentences + [user_input]
    # 创建 TF-IDF 向量化器
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_sentences)  # 输出稀疏矩阵
    # 计算余弦相似度
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])  # 最后一行对比前面所有行
    similarity_scores = cosine_sim[0]  # 获取相似度得分为 1D 数组
    # 排序并获取 topn 个最相似句子的索引和分数
    ranked_indices = similarity_scores.argsort()[::-1]  # 按相似度从高到低排序
    top_matches = [(sentences[i], similarity_scores[i]) for i in ranked_indices[:topn]]
    return top_matches

def main():
    # 打印存储的长句子
    print("Stored sentences:")
    for i, sentence in enumerate(sentences, start=1):
        print(f"{i}. {sentence}")
    # 用户输入句子
    user_input = input("\nEnter your sentence: ")
    # 查找最相似的句子
    result = find_most_similar_sentence(user_input, sentences)
    # 输出结果
    print("\nMost similar sentences:")
    for sentence, score in result:
        print(f"'{sentence}' with similarity score: {score:.4f}")

if __name__ == "__main__":
    main()









