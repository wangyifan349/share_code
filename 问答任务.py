import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import torch

# 加载模型和分词器
model_name = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 准备问题和答案字典
qa_pairs = {
    "What are the symptoms of COVID-19?": "Common symptoms include fever, dry cough, and tiredness.",
    "What are the signs of COVID-19?": "Common symptoms include fever, dry cough, and tiredness.",
    "How is hypertension diagnosed?": "Hypertension is diagnosed by measuring blood pressure over time.",
    "What is the recommended treatment for type 2 diabetes?": "Treatment includes lifestyle changes such as diet and exercise.",
    "What is the treatment for diabetes?": "Treatment includes lifestyle changes such as diet and exercise.",
}

# 准备输入数据
def get_embeddings(sentences):
    inputs = tokenizer(sentences, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0, :]  # 取[CLS] token的嵌入
    return embeddings.numpy()

# 获取问题的嵌入
questions = list(qa_pairs.keys())
answers = list(qa_pairs.values())
question_embeddings = get_embeddings(questions)

# 使用FAISS构建索引
index = faiss.IndexFlatIP(question_embeddings.shape[1])  # 使用内积（余弦相似度）
index.add(question_embeddings)  # 添加问题嵌入到索引中

# 查询相似度
def find_most_similar_answers(input_question, top_k=1):
    input_embedding = get_embeddings([input_question])
    D, I = index.search(input_embedding, k=top_k)  # 找到最相似的前K个问题
    
    results = []
    for j in range(top_k):
        answer_index = I[0][j]
        similarity_score = D[0][j]
        matched_question = questions[answer_index]  # 获取最接近的问题
        results.append((matched_question, answers[answer_index], similarity_score))  # 添加匹配的问题、答案和相似度到结果列表
    
    return results

# 测试查询
input_question = "What are the symptoms of the virus?"
top_k = 3
similar_answers = find_most_similar_answers(input_question, top_k)

print(f"Input Question: {input_question}")
for matched_question, answer, similarity in similar_answers:
    print(f"Matched Question: {matched_question}")
    print(f"Corresponding Answer: {answer}")
    print(f"Similarity (Cosine Similarity): {similarity:.4f}")
