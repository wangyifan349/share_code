import os
import json
import shutil
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

def is_image_file(filename):
    """检查文件是否为图片文件"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    extension = os.path.splitext(filename)[1].lower()
    return extension in image_extensions

def is_video_file(filename):
    """检查文件是否为视频文件"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'}
    extension = os.path.splitext(filename)[1].lower()
    return extension in video_extensions

def format_size(size):
    """格式化文件大小为更易读的格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def should_exclude_folder(folder_name, exclude_keywords):
    """检查文件夹名称是否包含排除关键词"""
    for keyword in exclude_keywords:
        if keyword.lower() in folder_name.lower():
            return True
    return False

def scan_directory(disk_path, exclude_keywords):
    """扫描指定目录，返回符合条件的文件信息"""
    file_info_list = []

    for root, dirs, files in os.walk(disk_path):
        # 排除包含关键词的文件夹
        dirs_to_remove = []
        for d in dirs:
            if should_exclude_folder(d, exclude_keywords):
                dirs_to_remove.append(d)
        
        for d in dirs_to_remove:
            dirs.remove(d)

        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)

            if is_image_file(file) or is_video_file(file):
                file_info_list.append({
                    'name': file,
                    'path': file_path,
                    'size': format_size(file_size),
                })

    return file_info_list

def save_to_json(file_info_list, json_path):
    """将文件信息保存到 JSON 文件"""
    try:
        with open(json_path, 'w') as json_file:
            json.dump(file_info_list, json_file, indent=4)
    except Exception as e:
        print(f"保存 JSON 文件时出错: {e}")

def get_new_file_name(target_directory, file_name):
    """生成新的文件名以避免重命名冲突"""
    base_name, extension = os.path.splitext(file_name)
    counter = 1
    new_file_name = file_name

    # 检查目标目录中是否存在同名文件
    while os.path.exists(os.path.join(target_directory, new_file_name)):
        new_file_name = f"{base_name} ({counter}){extension}"
        counter += 1

    return new_file_name

def move_files(file_info_list, target_directory):
    """将文件移动到目标目录"""
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for file_info in file_info_list:
        # 生成新的文件名以避免冲突
        new_file_name = get_new_file_name(target_directory, file_info['name'])
        target_path = os.path.join(target_directory, new_file_name)

        try:
            shutil.move(file_info['path'], target_path)  # 移动文件
        except Exception as e:
            print(f"移动文件时出错: {e}")
            messagebox.showerror("错误", f"移动文件 {file_info['name']} 时出错: {e}")

def scan_and_move(disk_path, exclude_keyword, target_directory):
    """在独立线程中执行扫描和移动操作"""
    exclude_keywords = exclude_keyword.strip().split()
    
    # 验证输入路径
    if not os.path.exists(disk_path):
        messagebox.showerror("错误", "指定的扫描路径不存在，请检查后重试。")
        return

    if not os.path.exists(target_directory):
        try:
            os.makedirs(target_directory)
        except Exception as e:
            messagebox.showerror("错误", f"创建目标目录时出错: {e}")
            return

    file_info_list = scan_directory(disk_path, exclude_keywords)

    # 保存文件信息到 JSON
    json_path = os.path.join(target_directory, 'file_info.json')
    save_to_json(file_info_list, json_path)

    if file_info_list:
        move_files(file_info_list, target_directory)
        messagebox.showinfo("完成", f"已移动 {len(file_info_list)} 个文件到 {target_directory}\n文件信息已保存到 {json_path}")
    else:
        messagebox.showinfo("完成", "未找到任何文件。")

def start_thread():
    """启动线程执行扫描和移动操作"""
    disk_path = disk_path_entry.get()
    exclude_keyword = exclude_keyword_entry.get()
    target_directory = target_directory_entry.get()

    thread = threading.Thread(target=scan_and_move, args=(disk_path, exclude_keyword, target_directory))
    thread.start()

def select_target_directory():
    """选择目标目录"""
    directory = filedialog.askdirectory()
    if directory:
        target_directory_entry.delete(0, tk.END)
        target_directory_entry.insert(0, directory)

# 创建主窗口
root = tk.Tk()
root.title("文件扫描和移动工具")
root.geometry("600x400")  # 设置窗口大小
root.configure(bg="#f0f0f0")  # 设置背景颜色

# 创建输入框和标签
frame = tk.Frame(root, bg="#f0f0f0")
frame.pack(pady=20)

# 标签和输入框
tk.Label(frame, text="扫描路径:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky='e')
disk_path_entry = tk.Entry(frame, width=50)
disk_path_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="排除文件夹关键词:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky='e')
exclude_keyword_entry = tk.Entry(frame, width=50)
exclude_keyword_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="目标路径:", bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=5, sticky='e')
target_directory_entry = tk.Entry(frame, width=50)
target_directory_entry.grid(row=2, column=1, padx=5, pady=5)

# 选择目标目录按钮
select_button = tk.Button(frame, text="选择目标目录", command=select_target_directory, bg="#4CAF50", fg="white")
select_button.grid(row=2, column=2, padx=5, pady=5)

# 创建按钮
scan_button = tk.Button(root, text="开始扫描和移动", command=start_thread, bg="#2196F3", fg="white")
scan_button.pack(pady=20)

# 运行主循环
root.mainloop()
