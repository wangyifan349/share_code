def chacha20_block(key, nonce, counter):
    # ChaCha20 的常量
    constants = b"expand 32-byte k"
    state = bytearray(64)  # 初始化状态数组，大小为 64 字节
    
    # 初始化状态
    for i in range(16):
        if i < 4:
            # 前 4 个字节为常量
            state[i * 4:i * 4 + 4] = constants[i * 4:i * 4 + 4]
        elif i < 12:
            # 接下来的 8 个字节为密钥
            state[i * 4:i * 4 + 4] = key[(i - 4) * 4:(i - 4) * 4 + 4]
        elif i == 12:
            # 第 12 个字节为计数器
            state[i * 4:i * 4 + 4] = counter.to_bytes(4, 'little')
        else:
            # 最后 4 个字节为 nonce
            state[i * 4:i * 4 + 4] = nonce[i - 13:i - 9]

    # ChaCha20 的四分之一轮函数
    def quarter_round(a, b, c, d):
        a += b
        d ^= a
        d = ((d << 16) | (d >> (32 - 16))) & 0xFFFFFFFF  # 循环左移
        c += d
        b ^= c
        b = ((b << 12) | (b >> (32 - 12))) & 0xFFFFFFFF  # 循环左移
        a += b
        d ^= a
        d = ((d << 8) | (d >> (32 - 8))) & 0xFFFFFFFF  # 循环左移
        c += d
        b ^= c
        b = ((b << 7) | (b >> (32 - 7))) & 0xFFFFFFFF  # 循环左移
        return a, b, c, d

    # 执行 10 轮 ChaCha20
    for _ in range(10):
        # 每轮调用四分之一轮函数
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

    # 将原始状态加到结果中
    for i in range(16):
        state[i * 4:i * 4 + 4] = (int.from_bytes(state[i * 4:i * 4 + 4], 'little') + 
                                   int.from_bytes(state[i + 16 * 4:i + 16 * 4 + 4], 'little')).to_bytes(4, 'little')

    return bytes(state[:64])  # 返回前 64 字节作为输出

def chacha20_encrypt(key, nonce, plaintext):
    # 检查密钥长度
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes long.")
    # 检查 nonce 长度
    if len(nonce) != 12:
        raise ValueError("Nonce must be 12 bytes long.")

    ciphertext = bytearray()  # 初始化密文数组
    counter = 0  # 初始化计数器
    for i in range(len(plaintext)):
        if i % 64 == 0:
            # 每 64 字节生成一个新的 ChaCha20 块
            block = chacha20_block(key, nonce, counter)
            counter += 1  # 计数器加 1
        ciphertext.append(plaintext[i] ^ block[i % 64])  # 进行异或操作
    return bytes(ciphertext)  # 返回密文

def poly1305(key, message):
    # 检查密钥长度
    if len(key) != 32:
        raise ValueError("Key must be 32 bytes long.")

    # 计算 r 和 s
    r = int.from_bytes(key[:16], 'little') & 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFC0
    s = int.from_bytes(key[16:], 'little')
    h = 0  # 初始化 h

    # 处理每个 16 字节的块
    def process_block(block):
        nonlocal h
        block_int = int.from_bytes(block, 'little')  # 将块转换为整数
        h += block_int  # 更新 h
        h = (h & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) % (1 << 130)  # 限制 h 的大小
        h = (h * r) % (1 << 130)  # 更新 h

    # 遍历消息，处理每个块
    for i in range(0, len(message), 16):
        block = message[i:i + 16]  # 获取当前块
        if len(block) < 16:
            block += b'\x00' * (16 - len(block))  # 如果块不足 16 字节，填充 0
        process_block(block)  # 处理块

    h = (h + s) % (1 << 130)  # 最后更新 h
    return h  # 返回计算出的 MAC

def poly1305_verify(key, message, mac):
    # 计算给定消息的 MAC 并与提供的 MAC 进行比较
    computed_mac = poly1305(key, message)
    return computed_mac == mac  # 返回验证结果

# 示例用法
key = b'0123456789abcdef0123456789abcdef'  # 32 字节的密钥
nonce = b'0123456789ab'  # 12 字节的 nonce
plaintext = b'Hello, World!'  # 明文

# 加密
ciphertext = chacha20_encrypt(key, nonce, plaintext)
print("Ciphertext:", ciphertext)

# 计算 MAC
mac = poly1305(key, ciphertext)
print("MAC:", mac)

# 验证 MAC
is_valid = poly1305_verify(key, ciphertext, mac)
print("MAC valid:", is_valid)

# 解密
decrypted_text = chacha20_encrypt(key, nonce, ciphertext)  # 重新使用加密函数进行解密
print("Decrypted text:", decrypted_text)

# 检查解密后的文本是否与原始明文匹配
print("Decryption successful:", decrypted_text == plaintext)
