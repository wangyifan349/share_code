import tensorflow as tf
from transformers import BertTokenizerFast, TFBertModel
import json
import numpy as np

# 从 JSON 文件加载数据
def load_data_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 数据预处理函数
def preprocess_data(data, tokenizer, max_seq_length=384):
    input_ids_list = []
    attention_masks_list = []
    token_type_ids_list = []
    start_positions = []
    end_positions = []

    for item in data:
        question = item['question']
        context = item['context']
        answer = item['answer']
        start_char = item['start_position']  # 答案在 context 中的起始字符索引
        end_char = item['end_position']      # 答案在 context 中的结束字符索引（不包含）

        # 编码 context，获取字符到 token 的映射
        encoded_context = tokenizer(context, return_offsets_mapping=True, max_length=max_seq_length, truncation=True)
        offsets = encoded_context['offset_mapping']

        # 找到答案的起始和结束 token 索引
        start_token_idx = None
        end_token_idx = None

        for idx, (start, end) in enumerate(offsets):
            if start_char >= start and start_char < end:
                start_token_idx = idx
            if end_char > start and end_char <= end:
                end_token_idx = idx
                break

        if start_token_idx is None or end_token_idx is None:
            print(f"Warning: Could not find token indices for the answer: {answer}")
            continue

        # 编码 question 和 context，构建模型输入
        inputs = tokenizer.encode_plus(
            question,
            context,
            max_length=max_seq_length,
            truncation='only_second',
            padding='max_length',
            return_offsets_mapping=False,
            return_token_type_ids=True,
            return_attention_mask=True
        )

        input_ids_list.append(inputs['input_ids'])
        attention_masks_list.append(inputs['attention_mask'])
        token_type_ids_list.append(inputs['token_type_ids'])

        # 调整起始和结束位置索引，加上 question 部分的偏移
        sep_index = inputs['input_ids'].index(tokenizer.sep_token_id, 1)  # 第一个 [SEP] 的索引
        start_positions.append(start_token_idx + sep_index + 1)
        end_positions.append(end_token_idx + sep_index + 1)

    return {
        'input_ids': tf.constant(input_ids_list),
        'attention_mask': tf.constant(attention_masks_list),
        'token_type_ids': tf.constant(token_type_ids_list),
        'start_positions': tf.constant(start_positions),
        'end_positions': tf.constant(end_positions)
    }

# 构建模型
def build_model(model_name, max_seq_length=384):
    input_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name='input_ids')
    attention_mask = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name='attention_mask')
    token_type_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name='token_type_ids')

    bert_model = TFBertModel.from_pretrained(model_name)
    sequence_output = bert_model(
        input_ids,
        attention_mask=attention_mask,
        token_type_ids=token_type_ids
    )[0]  # [batch_size, seq_length, hidden_size]

    # 输出层，预测每个位置是起始位置和结束位置的概率
    start_logits = tf.keras.layers.Dense(1, name='start_logit')(sequence_output)  # [batch_size, seq_length, 1]
    start_logits = tf.keras.layers.Flatten()(start_logits)  # [batch_size, seq_length]

    end_logits = tf.keras.layers.Dense(1, name='end_logit')(sequence_output)
    end_logits = tf.keras.layers.Flatten()(end_logits)

    start_probs = tf.keras.layers.Activation(tf.nn.softmax, name='start_probs')(start_logits)
    end_probs = tf.keras.layers.Activation(tf.nn.softmax, name='end_probs')(end_logits)

    model = tf.keras.Model(
        inputs=[input_ids, attention_mask, token_type_ids],
        outputs=[start_probs, end_probs]
    )
    return model

# 训练模型
def train_model(model, train_data, batch_size=8, epochs=3):
    optimizer = tf.keras.optimizers.Adam(learning_rate=3e-5)
    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False)
    model.compile(optimizer=optimizer, loss={'start_probs': loss_fn, 'end_probs': loss_fn})

    model.fit(
        x={
            'input_ids': train_data['input_ids'],
            'attention_mask': train_data['attention_mask'],
            'token_type_ids': train_data['token_type_ids']
        },
        y={
            'start_probs': train_data['start_positions'],
            'end_probs': train_data['end_positions']
        },
        batch_size=batch_size,
        epochs=epochs
    )

# 加载数据
print("Loading data from JSON...")
data = load_data_from_json('qa_dataset.json')

# 加载 BERT 分词器
print("Loading BERT tokenizer...")
model_name = 'bert-base-uncased'
tokenizer = BertTokenizerFast.from_pretrained(model_name)

# 数据预处理
print("Preprocessing data...")
processed_data = preprocess_data(data, tokenizer)

# 构建模型
print("Building model...")
model = build_model(model_name)

# 训练模型
print("Training model...")
train_model(model, processed_data)

print("Training complete!")
