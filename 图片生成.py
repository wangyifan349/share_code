import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import PIL.Image
import random

# 加载 BigGAN 模型
module = hub.load('https://tfhub.dev/deepmind/biggan-deep-256/1')

# 准备输入向量
def truncated_z_sample(batch_size, dimension_z, truncation=1.0):
    # 生成截断的潜在向量
    values = truncation * np.random.randn(batch_size, dimension_z)
    return values

def one_hot(index, num_classes):
    # 生成 one-hot 编码
    return np.eye(num_classes)[index]

# 设置参数
batch_size = 1  # 生成图像的数量
dimension_z = 128  # 潜在空间的维度
num_classes = 1000  # 类别总数
truncation = 0.5  # 截断参数，控制生成图像的多样性

# 生成随机潜在向量和类别
z = truncated_z_sample(batch_size, dimension_z, truncation)
random_indices = [random.randint(0, num_classes - 1) for _ in range(batch_size)]
y = one_hot(random_indices, num_classes)

# 生成图像
def generate_image(latent_vector, class_vector, truncation_value):
    inputs = {'z': latent_vector, 'y': class_vector, 'truncation': truncation_value}
    images = module(inputs)
    return images

images = generate_image(z, y, truncation)

# 显示图像
def show_image(image_tensor):
    image_array = np.array(image_tensor * 255, dtype=np.uint8)
    pil_image = PIL.Image.fromarray(image_array[0])
    pil_image.show()

show_image(images)


    batch_size: 指定要生成的图像数量。
    dimension_z: 潜在空间的维度，控制生成图像的特征复杂度。
    num_classes: 模型支持的类别总数。
    truncation: 截断参数，值越低，生成图像越接近训练数据的平均特征；值越高，生成图像的多样性越大。
    latent_vector (z): 随机生成的潜在向量，用于生成图像。
    class_vector (y): 类别向量，指定生成图像的类别。


