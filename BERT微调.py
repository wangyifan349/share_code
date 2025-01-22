import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text  # 必须安装 tensorflow-text
import json

# 从 JSON 文件加载数据
def load_data_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# 数据预处理函数
def preprocess_data(data, tokenizer, max_seq_length=384):
    input_word_ids = []
    input_mask = []
    segment_ids = []
    start_positions = []
    end_positions = []

    for item in data:
        question = item['question']
        context = item['context']
        start_char = item['start_position']
        end_char = item['end_position']

        # 使用 BERT 分词器对问题和上下文进行编码
        inputs = tokenizer([question], [context], max_seq_length=max_seq_length)

        # 获取编码后的输入 ID
        input_ids = inputs['input_word_ids'][0].numpy()

        # 初始化答案的起始和结束索引
        token_start_index = None
        token_end_index = None

        # 寻找答案的起始和结束 token 索引
        for idx, token_id in enumerate(input_ids):
            if token_id == start_char:
                token_start_index = idx
            if token_id == end_char:
                token_end_index = idx
                break

        # 如果找不到答案的起始或结束索引，则跳过该条数据
        if token_start_index is None or token_end_index is None:
            print(f"Warning: Could not find start or end token for question: {question}")
            continue

        # 保存结果
        input_word_ids.append(input_ids)
        input_mask.append(inputs['input_mask'][0].numpy())
        segment_ids.append(inputs['segment_ids'][0].numpy())
        start_positions.append(token_start_index)
        end_positions.append(token_end_index)

    return {
        'input_word_ids': tf.constant(input_word_ids),
        'input_mask': tf.constant(input_mask),
        'segment_ids': tf.constant(segment_ids),
        'start_positions': tf.constant(start_positions),
        'end_positions': tf.constant(end_positions)
    }

# 构建模型
def build_model(max_seq_length=384):
    input_word_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name='input_word_ids')
    input_mask = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name='input_mask')
    segment_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name='segment_ids')

    bert_encoder = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/3", trainable=True)
    sequence_output = bert_encoder([input_word_ids, input_mask, segment_ids])

    start_logits = tf.keras.layers.Dense(1, name='start_logit')(sequence_output)
    start_logits = tf.keras.layers.Flatten()(start_logits)

    end_logits = tf.keras.layers.Dense(1, name='end_logit')(sequence_output)
    end_logits = tf.keras.layers.Flatten()(end_logits)

    start_probs = tf.keras.layers.Activation('softmax', name='start_probs')(start_logits)
    end_probs = tf.keras.layers.Activation('softmax', name='end_probs')(end_logits)

    model = tf.keras.Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=[start_probs, end_probs])
    return model

# 训练模型
def train_model(model, train_data, batch_size=16, epochs=3):
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5),
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    train_dataset = tf.data.Dataset.from_tensor_slices((
        {
            'input_word_ids': train_data['input_word_ids'],
            'input_mask': train_data['input_mask'],
            'segment_ids': train_data['segment_ids']
        },
        {
            'start_probs': train_data['start_positions'],
            'end_probs': train_data['end_positions']
        }
    )).batch(batch_size)

    model.fit(train_dataset, epochs=epochs)

# 加载数据
print("Loading data from JSON...")
data = load_data_from_json('qa_dataset.json')

# 加载 BERT 分词器
print("Loading BERT tokenizer...")
bert_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")

# 数据预处理
print("Preprocessing data...")
processed_data = preprocess_data(data, bert_preprocess)

# 构建模型
print("Building model...")
model = build_model()

# 训练模型
print("Training model...")
train_model(model, processed_data)

print("Training complete!")
