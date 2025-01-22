import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text  # 必须安装 tensorflow-text
import tensorflow_datasets as tfds

# 加载 SQuAD 数据集
squad_data = tfds.load('squad', split='train', as_supervised=False)

# 加载 BERT 分词器和预处理模型
bert_preprocess = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3")
bert_encoder = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/3", trainable=True)

# 数据预处理函数
def preprocess_data(example):
    question = example['question']
    context = example['context']
    answer = example['answers']['text'][0]
    answer_start = example['answers']['answer_start'][0]

    # 使用 BERT 分词器对问题和上下文进行编码
    inputs = bert_preprocess([question, context])

    # 计算答案的起始和结束位置
    tokenized_context = inputs['input_word_ids'][0].numpy()
    answer_tokens = bert_preprocess([answer, ""])['input_word_ids'][0].numpy()[1:-1]  # 去掉 [CLS] 和 [SEP]
    start_position = tf.where(tf.reduce_all(tf.equal(tokenized_context, answer_tokens[0]), axis=-1))[0][0]
    end_position = start_position + len(answer_tokens) - 1

    return {
        'input_word_ids': inputs['input_word_ids'],
        'input_mask': inputs['input_mask'],
        'segment_ids': inputs['segment_ids'],
        'start_positions': start_position,
        'end_positions': end_position
    }

# 对数据集进行预处理
processed_data = squad_data.map(preprocess_data)

# 构建模型
def build_model():
    input_word_ids = tf.keras.layers.Input(shape=(None,), dtype=tf.int32, name='input_word_ids')
    input_mask = tf.keras.layers.Input(shape=(None,), dtype=tf.int32, name='input_mask')
    segment_ids = tf.keras.layers.Input(shape=(None,), dtype=tf.int32, name='segment_ids')

    # BERT 编码器
    sequence_output = bert_encoder([input_word_ids, input_mask, segment_ids])

    # 输出层，用于预测答案的起始和结束位置
    start_logits = tf.keras.layers.Dense(1, name='start_logit')(sequence_output)
    start_logits = tf.keras.layers.Flatten()(start_logits)

    end_logits = tf.keras.layers.Dense(1, name='end_logit')(sequence_output)
    end_logits = tf.keras.layers.Flatten()(end_logits)

    start_probs = tf.keras.layers.Activation('softmax', name='start_probs')(start_logits)
    end_probs = tf.keras.layers.Activation('softmax', name='end_probs')(end_logits)

    model = tf.keras.Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=[start_probs, end_probs])
    return model

# 构建模型
model = build_model()

# 编译模型
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 准备训练数据
def generator():
    for example in processed_data:
        yield (
            {
                'input_word_ids': example['input_word_ids'],
                'input_mask': example['input_mask'],
                'segment_ids': example['segment_ids']
            },
            {
                'start_probs': example['start_positions'],
                'end_probs': example['end_positions']
            }
        )

train_dataset = tf.data.Dataset.from_generator(generator,
                                               output_signature=(
                                                   {
                                                       'input_word_ids': tf.TensorSpec(shape=(None,), dtype=tf.int32),
                                                       'input_mask': tf.TensorSpec(shape=(None,), dtype=tf.int32),
                                                       'segment_ids': tf.TensorSpec(shape=(None,), dtype=tf.int32)
                                                   },
                                                   {
                                                       'start_probs': tf.TensorSpec(shape=(), dtype=tf.int32),
                                                       'end_probs': tf.TensorSpec(shape=(), dtype=tf.int32)
                                                   }
                                               )).batch(16)

# 训练模型
model.fit(train_dataset, epochs=3)
