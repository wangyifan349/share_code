import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# 加载微调后的BERT模型和分词器
model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"  # 或者使用 distilbert-base-uncased-distilled-squad
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

# 初始化记忆字典
memory_dict = {
    "学习": "今天我学习了关于定期锻炼的重要性。",
    "目标": "我的目标是每周至少锻炼三次。",
    "情感": "我感到很开心，因为我完成了一个重要的任务。",
    "事件": "上周末我参加了一个朋友的婚礼。"
}

# 信息抽取函数
def extract_information(question, long_text):
    inputs = tokenizer(question, long_text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    answer_start = torch.argmax(outputs.start_logits)  # 找到答案的起始位置
    answer_end = torch.argmax(outputs.end_logits) + 1  # 找到答案的结束位置
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][answer_start:answer_end]))
    
    return answer

# 问答功能
def answer_question(question):
    for memory_type, long_text in memory_dict.items():
        if question.lower() in memory_type.lower():
            return extract_information(question, long_text)
    return "没有找到相关信息。"

# 示例问答
question = "我今天学习了什么？"
answer = answer_question("学习")
print(f"问题: {question}")
print(f"回答: {answer}")

question = "我的目标是什么？"
answer = answer_question("目标")
print(f"问题: {question}")
print(f"回答: {answer}")

question = "我感到怎么样？"
answer = answer_question("情感")
print(f"问题: {question}")
print(f"回答: {answer}")

question = "发生了什么事件？"
answer = answer_question("事件")
print(f"问题: {question}")
print(f"回答: {answer}")
