import os
import hashlib
import random
import struct
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def generate_random_bytes(n):
    """生成 n 字节的随机字节"""
    return bytes(random.getrandbits(8) for _ in range(n))

def sha256_hash(data):
    """计算 SHA-256 哈希"""
    return hashlib.sha256(data).digest()

def chacha20_block(key, nonce, counter):
    """生成 ChaCha20 加密块"""
    constants = b"expand 32-byte k"
    state = bytearray(64)  # 初始化状态数组，大小为 64 字节
    
    # 初始化状态
    for i in range(16):
        if i < 4:
            state[i * 4:i * 4 + 4] = constants[i * 4:i * 4 + 4]
        elif i < 12:
            state[i * 4:i * 4 + 4] = key[(i - 4) * 4:(i - 4) * 4 + 4]
        elif i == 12:
            state[i * 4:i * 4 + 4] = struct.pack('<I', counter)
        else:
            state[i * 4:i * 4 + 4] = nonce[i - 13:i - 9]

    def quarter_round(a, b, c, d):
        """执行 ChaCha20 的四分之一轮操作"""
        a += b
        d ^= a
        d = ((d << 16) | (d >> (32 - 16))) & 0xFFFFFFFF
        c += d
        b ^= c
        b = ((b << 12) | (b >> (32 - 12))) & 0xFFFFFFFF
        a += b
        d ^= a
        d = ((d << 8) | (d >> (32 - 8))) & 0xFFFFFFFF
        c += d
        b ^= c
        b = ((b << 7) | (b >> (32 - 7))) & 0xFFFFFFFF
        return a, b, c, d

    # 进行 10 轮 ChaCha20 操作
    for _ in range(10):
        state[0:4], state[4:8], state[8:12], state[12:16] = quarter_round(
            int.from_bytes(state[0:4], 'little'),
            int.from_bytes(state[4:8], 'little'),
            int.from_bytes(state[8:12], 'little'),
            int.from_bytes(state[12:16], 'little')
        )
        state[1:5], state[5:9], state[9:13], state[13:17] = quarter_round(
            int.from_bytes(state[1:5], 'little'),
            int.from_bytes(state[5:9], 'little'),
            int.from_bytes(state[9:13], 'little'),
            int.from_bytes(state[13:17], 'little')
        )
        state[2:6], state[6:10], state[10:14], state[14:18] = quarter_round(
            int.from_bytes(state[2:6], 'little'),
            int.from_bytes(state[6:10], 'little'),
            int.from_bytes(state[10:14], 'little'),
            int.from_bytes(state[14:18], 'little')
        )
        state[3:7], state[7:11], state[11:15], state[15:19] = quarter_round(
            int.from_bytes(state[3:7], 'little'),
            int.from_bytes(state[7:11], 'little'),
            int.from_bytes(state[11:15], 'little'),
            int.from_bytes(state[15:19], 'little')
        )

    # 将状态数组的前 16 个字节与初始状态相加
    for i in range(16):
        state[i * 4:i * 4 + 4] = (int.from_bytes(state[i * 4:i * 4 + 4], 'little') + 
                                   int.from_bytes(state[i + 16 * 4:i + 16 * 4 + 4], 'little')).to_bytes(4, 'little')

    return bytes(state[:64])  # 返回生成的加密块

def chacha20_encrypt(key, nonce, plaintext):
    """使用 ChaCha20 算法加密明文"""
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes long.")
    if len(nonce) != 12:
        raise ValueError("Nonce must be 12 bytes long.")

    ciphertext = bytearray()
    counter = 0  # 初始化计数器
    for i in range(len(plaintext)):
        if i % 64 == 0:  # 每 64 字节生成一个新的加密块
            block = chacha20_block(key, nonce, counter)
            counter += 1
        ciphertext.append(plaintext[i] ^ block[i % 64])  # 使用 XOR 操作生成密文
    return bytes(ciphertext)

def poly1305(key, message):
    """计算 Poly1305 MAC"""
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes long.")

    r = int.from_bytes(key[:16], 'little') & 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFC0
    s = int.from_bytes(key[16:], 'little')
    h = 0  # 初始化哈希值

    def process_block(block):
        """处理 16 字节的块"""
        nonlocal h
        block_int = int.from_bytes(block, 'little')
        h += block_int
        h = (h & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) % (1 << 130)
        h = (h * r) % (1 << 130)

    # 处理消息中的每个 16 字节块
    for i in range(0, len(message), 16):
        block = message[i:i + 16]
        if len(block) < 16:
            block += b'\x00' * (16 - len(block))  # 填充不足的块
        process_block(block)

    h = (h + s) % (1 << 130)  # 添加 s 值
    return h  # 返回计算得到的 MAC

def poly1305_verify(key, message, mac):
    """验证 Poly1305 MAC"""
    computed_mac = poly1305(key, message)
    return computed_mac == mac  # 返回计算的 MAC 是否与给定的 MAC 相等

class FileEncryptorApp:
    def __init__(self, master):
        """初始化文件加密解密应用"""
        self.master = master
        master.title("文件加密/解密工具")
        master.geometry("600x400")
        master.configure(bg="#f0f0f0")

        # 创建选项卡
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, expand=True, fill='both')

        self.password_tab = ttk.Frame(self.notebook)
        self.encrypt_tab = ttk.Frame(self.notebook)
        self.decrypt_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.password_tab, text='输入密码')
        self.notebook.add(self.encrypt_tab, text='加密文件')
        self.notebook.add(self.decrypt_tab, text='解密文件')

        # 密码输入选项卡
        self.password_label = tk.Label(self.password_tab, text="输入密码:", bg="#f0f0f0", font=("Arial", 12))
        self.password_label.grid(row=0, column=0, padx=20, pady=10)

        self.password_entry = tk.Entry(self.password_tab, show='*', font=("Arial", 12))
        self.password_entry.grid(row=1, column=0, padx=20, pady=10)

        self.set_password_button = tk.Button(self.password_tab, text="设置密码", command=self.set_password, font=("Arial", 12))
        self.set_password_button.grid(row=2, column=0, padx=20, pady=10)

        # 加密文件选项卡
        self.label = tk.Label(self.encrypt_tab, text="选择文件夹进行批量加密", bg="#f0f0f0", font=("Arial", 14))
        self.label.grid(row=0, column=0, padx=20, pady=10)

        self.select_button = tk.Button(self.encrypt_tab, text="选择文件夹", command=self.select_folder, font=("Arial", 12))
        self.select_button.grid(row=1, column=0, padx=20, pady=10)

        self.encrypt_button = tk.Button(self.encrypt_tab, text="加密文件", command=self.start_encrypt_thread, font=("Arial", 12))
        self.encrypt_button.grid(row=2, column=0, padx=20, pady=10)

        # 解密文件选项卡
        self.label_decrypt = tk.Label(self.decrypt_tab, text="选择文件夹进行批量解密", bg="#f0f0f0", font=("Arial", 14))
        self.label_decrypt.grid(row=0, column=0, padx=20, pady=10)

        self.select_button_decrypt = tk.Button(self.decrypt_tab, text="选择文件夹", command=self.select_folder_decrypt, font=("Arial", 12))
        self.select_button_decrypt.grid(row=1, column=0, padx=20, pady=10)

        self.decrypt_button = tk.Button(self.decrypt_tab, text="解密文件", command=self.start_decrypt_thread, font=("Arial", 12))
        self.decrypt_button.grid(row=2, column=0, padx=20, pady=10)

        # 字符串加密解密选项卡
        self.string_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.string_tab, text='加密/解密字符串')

        self.label_string = tk.Label(self.string_tab, text="输入字符串进行加密:", bg="#f0f0f0", font=("Arial", 14))
        self.label_string.grid(row=0, column=0, padx=20, pady=10)

        self.input_string = tk.Entry(self.string_tab, width=50, font=("Arial", 12))
        self.input_string.grid(row=1, column=0, padx=20, pady=10)

        self.encrypt_string_button = tk.Button(self.string_tab, text="加密字符串", command=self.encrypt_string, font=("Arial", 12))
        self.encrypt_string_button.grid(row=2, column=0, padx=20, pady=10)

        self.result_label = tk.Label(self.string_tab, text="", bg="#f0f0f0", font=("Arial", 12))
        self.result_label.grid(row=3, column=0, padx=20, pady=10)

        self.label_string_decrypt = tk.Label(self.string_tab, text="输入密文进行解密:", bg="#f0f0f0", font=("Arial", 14))
        self.label_string_decrypt.grid(row=4, column=0, padx=20, pady=10)

        self.input_string_decrypt = tk.Entry(self.string_tab, width=50, font=("Arial", 12))
        self.input_string_decrypt.grid(row=5, column=0, padx=20, pady=10)

        self.decrypt_string_button = tk.Button(self.string_tab, text="解密字符串", command=self.decrypt_string, font=("Arial", 12))
        self.decrypt_string_button.grid(row=6, column=0, padx=20, pady=10)

        self.password = None  # 用于存储用户输入的密码

    def set_password(self):
        """设置用户输入的密码"""
        self.password = self.password_entry.get()
        if not self.password:
            messagebox.showwarning("警告", "请输入密码")
            return
        messagebox.showinfo("信息", "密码已设置")

    def generate_key(self):
        """根据用户输入的密码生成 32 字节的密钥"""
        if not self.password:
            raise ValueError("密码未设置")
        return sha256_hash(self.password.encode('utf-8'))

    def select_folder(self):
        """选择文件夹进行加密"""
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            messagebox.showinfo("选择文件夹", f"选择的文件夹: {self.folder_path}")

    def select_folder_decrypt(self):
        """选择文件夹进行解密"""
        self.folder_path_decrypt = filedialog.askdirectory()
        if self.folder_path_decrypt:
            messagebox.showinfo("选择文件夹", f"选择的文件夹: {self.folder_path_decrypt}")

    def start_encrypt_thread(self):
        """启动加密线程"""
        threading.Thread(target=self.encrypt_files).start()

    def start_decrypt_thread(self):
        """启动解密线程"""
        threading.Thread(target=self.decrypt_files).start()

    def encrypt_files(self):
        """加密指定文件夹中的所有文件"""
        if not self.password:
            messagebox.showwarning("警告", "请先设置密码")
            return

        key = self.generate_key()  # 生成密钥

        if not hasattr(self, 'folder_path'):
            messagebox.showwarning("警告", "请先选择文件夹")
            return

        # 使用 os.walk 遍历文件夹及其子文件夹中的所有文件
        for root, dirs, files in os.walk(self.folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                # 记录原文件的时间戳
                original_times = os.stat(file_path)
                original_mtime = original_times.st_mtime
                original_atime = original_times.st_atime

                with open(file_path, 'rb') as f:
                    plaintext = f.read()  # 读取明文
                nonce = generate_random_bytes(12)  # 随机生成 nonce
                ciphertext = chacha20_encrypt(key, nonce, plaintext)  # 加密明文
                mac = poly1305(key, ciphertext)  # 计算 MAC

                # 直接覆盖原文件
                with open(file_path, 'wb') as f:
                    f.write(nonce + mac.to_bytes(16, 'little') + ciphertext)  # 将 nonce、MAC 和密文一起保存

                # 恢复文件的时间戳
                os.utime(file_path, (original_atime, original_mtime))

        messagebox.showinfo("完成", "所有文件已加密")

    def decrypt_files(self):
        """解密指定文件夹中的所有文件"""
        if not self.password:
            messagebox.showwarning("警告", "请先设置密码")
            return

        key = self.generate_key()  # 生成密钥

        if not hasattr(self, 'folder_path_decrypt'):
            messagebox.showwarning("警告", "请先选择文件夹")
            return

        # 使用 os.walk 遍历文件夹及其子文件夹中的所有加密文件
        for root, dirs, files in os.walk(self.folder_path_decrypt):
            for filename in files:
                enc_file_path = os.path.join(root, filename)
                if os.path.isfile(enc_file_path):
                    with open(enc_file_path, 'rb') as f:
                        nonce = f.read(12)  # 读取 nonce
                        mac = int.from_bytes(f.read(16), 'little')  # 读取 MAC
                        ciphertext = f.read()  # 读取密文

                    if poly1305_verify(key, ciphertext, mac):  # 验证 MAC
                        decrypted_text = chacha20_encrypt(key, nonce, ciphertext)  # 解密
                        with open(enc_file_path, 'wb') as f:
                            f.write(decrypted_text)  # 保存解密后的文件
                    else:
                        messagebox.showwarning("警告", f"MAC 验证失败: {filename}")

        messagebox.showinfo("完成", "所有文件已解密")

    def encrypt_string(self):
        """加密用户输入的字符串"""
        if not self.password:
            messagebox.showwarning("警告", "请先设置密码")
            return

        key = self.generate_key()  # 生成密钥
        plaintext = self.input_string.get().encode('utf-8')  # 获取明文
        nonce = generate_random_bytes(12)  # 随机生成 nonce
        ciphertext = chacha20_encrypt(key, nonce, plaintext)  # 加密明文
        tag = poly1305(key, ciphertext)  # 计算 MAC
        result = f"Nonce: {nonce.hex()}\nTag: {tag}\nCiphertext: {ciphertext.hex()}"
        self.result_label.config(text=result)  # 显示结果

    def decrypt_string(self):
        """解密用户输入的密文"""
        if not self.password:
            messagebox.showwarning("警告", "请先设置密码")
            return

        key = self.generate_key()  # 生成密钥
        input_data = self.input_string_decrypt.get()  # 获取输入数据
        try:
            # 解析输入数据
            nonce_str, tag_str, ciphertext_str = input_data.split(',')
            nonce = bytes.fromhex(nonce_str.split(':')[1].strip())  # 解析 nonce
            tag = int(tag_str.split(':')[1].strip())  # 解析 MAC
            ciphertext = bytes.fromhex(ciphertext_str.split(':')[1].strip())  # 解析密文
            if poly1305_verify(key, ciphertext, tag):  # 验证 MAC
                decrypted_text = chacha20_encrypt(key, nonce, ciphertext)  # 解密
                self.result_label.config(text=f"解密结果: {decrypted_text.decode('utf-8')}")
            else:
                self.result_label.config(text="MAC 验证失败")
        except Exception as e:
            self.result_label.config(text=f"解密失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileEncryptorApp(root)  # 创建应用实例
    root.mainloop()  # 启动主循环
