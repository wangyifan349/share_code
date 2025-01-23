import torch
from transformers import BigGAN, BigGANConfig
from transformers import BigGANImageProcessor
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# 1. 加载预训练的 BigGAN 模型
model_name = 'biggan-deep-256'  # 或者选择 'biggan-deep-128', 'biggan-deep-512'
model = BigGAN.from_pretrained(model_name)

# 2. 创建一个输入噪声向量
# 通常 BigGAN 需要输入一个随机噪声向量（latent vector）和类别标签
truncation = 0.4  # 控制生成多样性的截断系数
latents = torch.randn(1, 128)  # BigGAN 默认使用 128 维 latent vector

# 3. 设置目标类别的标签（ImageNet 类别）
# 用以下数字代表各个类别：0-999 为 ImageNet 类别标签
target_class = 207  # 207 是 "Golden retriever" 金毛犬

# 将类别标签转化为 one-hot
class_vector = torch.zeros(1, 1000)  # ImageNet 有 1000 个类别
class_vector[0, target_class] = 1

# 4. 前向传递，生成图像
with torch.no_grad():
    outputs = model(latents, class_vector, truncation)

# 5. 使用管理工具将输出转换为图像格式
# 使用输出处理器进行图像的后处理
processor = BigGANImageProcessor()
image = processor(outputs)[0]

# 6. 显示生成的图像
plt.imshow(np.asarray(image))
plt.title("Generated Image of class {}".format(target_class))
plt.axis("off")
plt.show()

# 7. 保存生成的图像
image.save("biggan_generated_image.png")

"""
pip install tensorflow tensorflow-hub numpy pillow
"""
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# 1. 加载 BigGAN 模型
# 注意，TensorFlow Hub URL 可能会更新；确保使用最新的 URL
biggan_model_url = "https://tfhub.dev/deepmind/biggan-256/2"
model = hub.load(biggan_model_url)

# 2. 函数：生成潜在向量和标签
def generate_latent_vectors(batch_size, truncation, seed):
    rnd = np.random.RandomState(seed)
    return truncation * rnd.standard_normal([batch_size, 128])

def generate_class_vectors(batch_size, class_label):
    return tf.one_hot([class_label] * batch_size, 1000)

# 3. 设置参数
truncation = 0.4  # 截断参数
batch_size = 1    # 生成一张图片
seed = 42         # 随机种子
class_label = 207  # 207 是 "Golden retriever" 金毛犬

# 4. 生成输入向量
latent_vector = generate_latent_vectors(batch_size, truncation, seed)
class_vector = generate_class_vectors(batch_size, class_label)

# 5. 使用模型生成图像
output = model([latent_vector, class_vector, truncation])
# 输出的图像张量在范围 [-1, 1], 需调整到 [0, 255]
image_np = (output.numpy() * 127.5 + 127.5).astype(np.uint8)

# 6. 转换为 PIL 图像并展示
image = Image.fromarray(image_np[0])
plt.imshow(image)
plt.title("Generated Image of class {}".format(class_label))
plt.axis("off")
plt.show()

# 7. 保存图像
image.save("tensorflow_hub_biggan_generated_image.png")



