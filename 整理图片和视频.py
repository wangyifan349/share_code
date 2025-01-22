import os
import cv2
import shutil
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *


def calculate_file_hash(file_path):
    """
    计算文件的 MD5 哈希值，用于判断文件是否重复。
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        print(f"无法计算文件哈希值: {file_path}, 错误: {e}")
        return None
    return hash_md5.hexdigest()


def detect_face(image_path):
    """检测图片中是否有人脸"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(image_path)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return len(faces) > 0


def get_unique_file_path(directory, filename):
    """
    获取一个唯一的文件路径，避免文件覆盖。
    如果文件已存在，则自动在文件名后添加编号。
    """
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    unique_path = os.path.join(directory, unique_filename)

    # 循环检查是否存在同名文件，若存在则修改文件名
    while os.path.exists(unique_path):
        unique_filename = f"{base}_{counter}{extension}"
        unique_path = os.path.join(directory, unique_filename)
        counter += 1

    return unique_path


def move_or_copy_images(source_dir, target_dir, operation, status_label, log_text):
    """
    整理图片并分类，支持移动或拷贝操作，并通过哈希值检测文件重复。
    """
    if not os.path.exists(source_dir):
        messagebox.showerror("错误", "源目录不存在！")
        return
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    face_dir = os.path.join(target_dir, 'with_faces')
    no_face_dir = os.path.join(target_dir, 'without_faces')

    os.makedirs(face_dir, exist_ok=True)
    os.makedirs(no_face_dir, exist_ok=True)

    # 初始化计数
    total_files = 0
    face_count = 0
    no_face_count = 0
    processed_hashes = set()  # 已处理文件的哈希值

    # 更新状态
    status_label.config(text="正在处理，请稍候...")
    log_text.delete("1.0", tk.END)  # 清空日志框
    log_text.insert(tk.END, "开始整理图片...\n")

    try:
        for filename in os.listdir(source_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                total_files += 1
                file_path = os.path.join(source_dir, filename)

                # 计算文件哈希值
                file_hash = calculate_file_hash(file_path)
                if file_hash in processed_hashes:
                    log_text.insert(tk.END, f"跳过重复文件: {filename}\n")
                    continue

                # 检测人脸并决定目标目录
                if detect_face(file_path):
                    target_dir_path = face_dir
                    face_count += 1
                else:
                    target_dir_path = no_face_dir
                    no_face_count += 1

                # 获取唯一的目标文件路径
                unique_target_path = get_unique_file_path(target_dir_path, filename)

                # 执行移动或拷贝操作
                if operation == "move":
                    shutil.move(file_path, unique_target_path)
                elif operation == "copy":
                    shutil.copy(file_path, unique_target_path)

                # 将文件哈希值加入已处理集合
                processed_hashes.add(file_hash)

        # 更新状态
        status_label.config(text="整理完成！")
        log_text.insert(tk.END, f"总文件数: {total_files}\n")
        log_text.insert(tk.END, f"检测到人脸的图片数: {face_count}\n")
        log_text.insert(tk.END, f"未检测到人脸的图片数: {no_face_count}\n")
        log_text.insert(tk.END, "整理完成！\n")
        messagebox.showinfo("完成", "图片整理完成！")
        print(f"总文件数: {total_files}")
        print(f"检测到人脸的图片数: {face_count}")
        print(f"未检测到人脸的图片数: {no_face_count}")
    except Exception as e:
        status_label.config(text="处理失败！")
        log_text.insert(tk.END, f"处理失败: {e}\n")
        messagebox.showerror("错误", f"处理过程中出现错误：{e}")


def start_processing(source_dir, target_dir, operation, status_label, log_text):
    """在独立线程中处理图片整理"""
    threading.Thread(target=move_or_copy_images, args=(source_dir, target_dir, operation, status_label, log_text)).start()


def select_source_directory(entry):
    """选择源目录"""
    directory = filedialog.askdirectory(title="选择源目录")
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)


def select_target_directory(entry):
    """选择目标目录"""
    directory = filedialog.askdirectory(title="选择目标目录")
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)


def main():
    # 创建主窗口
    style = Style(theme="cosmo")  # 使用 ttkbootstrap 美化界面
    root = style.master
    root.title("图片整理工具")
    root.geometry("700x550")

    # 界面布局
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    # 源目录选择
    tk.Label(frame, text="源目录：").grid(row=0, column=0, sticky=tk.W, pady=5)
    source_entry = tk.Entry(frame, width=50)
    source_entry.grid(row=0, column=1, pady=5)
    tk.Button(frame, text="选择", command=lambda: select_source_directory(source_entry)).grid(row=0, column=2, padx=5)

    # 目标目录选择
    tk.Label(frame, text="目标目录：").grid(row=1, column=0, sticky=tk.W, pady=5)
    target_entry = tk.Entry(frame, width=50)
    target_entry.grid(row=1, column=1, pady=5)
    tk.Button(frame, text="选择", command=lambda: select_target_directory(target_entry)).grid(row=1, column=2, padx=5)

    # 操作选择（移动或拷贝）
    operation_var = tk.StringVar(value="move")
    tk.Label(frame, text="操作类型：").grid(row=2, column=0, sticky=tk.W, pady=5)
    tk.Radiobutton(frame, text="移动", variable=operation_var, value="move").grid(row=2, column=1, sticky=tk.W)
    tk.Radiobutton(frame, text="拷贝", variable=operation_var, value="copy").grid(row=2, column=2, sticky=tk.W)

    # 状态标签
    status_label = tk.Label(frame, text="等待操作...", fg="blue")
    status_label.grid(row=3, column=0, columnspan=3, pady=10)

    # 日志框
    log_label = tk.Label(frame, text="日志输出：")
    log_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    log_text = tk.Text(frame, height=15, width=70)
    log_text.grid(row=5, column=0, columnspan=3, pady=5)

    # 开始按钮
    start_button = tk.Button(frame, text="开始整理", command=lambda: start_processing(source_entry.get(), target_entry.get(), operation_var.get(), status_label, log_text))
    start_button.grid(row=6, column=0, columnspan=3, pady=10)

    # 运行主循环
    root.mainloop()


if __name__ == "__main__":
    main()
