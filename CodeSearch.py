import torch
from transformers import AutoTokenizer, AutoModel
from datasets import load_dataset

# 1. 加载 CodeSearchNet 模型和分词器
model_name = "microsoft/CodeBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 确保模型在评估模式
model.eval()

# 2. 准备数据集（这里以 Python 代码为例）
# 加载 CodeSearchNet 数据集的 Python 部分
dataset = load_dataset("code_search_net", "python")

# 3. 定义一个函数来编码查询和代码
def encode_query_and_code(query, code):
    # 使用分词器将查询和代码编码为模型输入
    inputs = tokenizer(query, code, return_tensors="pt", padding=True, truncation=True)
    
    # 使用模型生成嵌入
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 使用平均池化来获取句子的嵌入表示
    return outputs.last_hidden_state.mean(dim=1)

# 4. 示例查询
query = "如何定义一个函数"

# 5. 从数据集中选择一个代码片段（这里选择第一个代码片段作为示例）
code_snippet = dataset['train'][0]['code']

# 6. 编码查询和代码
query_embedding = encode_query_and_code(query, code_snippet)
code_embedding = encode_query_and_code(query, code_snippet)

# 7. 计算余弦相似度
similarity = torch.cosine_similarity(query_embedding, code_embedding)

# 8. 输出结果
print(f"查询: {query}")
print(f"代码片段: {code_snippet}")
print(f"查询与代码片段的余弦相似度: {similarity.item()}")
