import os
from PIL import Image
def convert_webp_to_jpg(source_folder):
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith('.webp'):
                webp_image_path = os.path.join(root, file)
                jpg_image_path = os.path.splitext(webp_image_path)[0] + '.jpg'
                
                # 打开webp图片文件
                with Image.open(webp_image_path) as webp_image:
                    # 转换为RGB模式以确保没有像素丢失
                    rgb_image = webp_image.convert('RGB')
                    # 保存为jpg格式
                    rgb_image.save(jpg_image_path, 'JPEG')
                print(f"Converted '{webp_image_path}' to '{jpg_image_path}'.")
source_folder = str(input("输入你的工作路径，将webp转换为jpg文件: "))
if not os.path.exists(source_folder):
    print("提供的路径不存在，请检查后重试。")
else:
    convert_webp_to_jpg(source_folder)
