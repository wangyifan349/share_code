import os
import hashlib
import struct

def quarter_round(state, a, b, c, d):
    state[a] = (state[a] + state[b]) & 0xFFFFFFFF
    state[d] ^= state[a]
    state[d] = ((state[d] << 16) | (state[d] >> 16)) & 0xFFFFFFFF

    state[c] = (state[c] + state[d]) & 0xFFFFFFFF
    state[b] ^= state[c]
    state[b] = ((state[b] << 12) | (state[b] >> 20)) & 0xFFFFFFFF

    state[a] = (state[a] + state[b]) & 0xFFFFFFFF
    state[d] ^= state[a]
    state[d] = ((state[d] << 8) | (state[d] >> 24)) & 0xFFFFFFFF

    state[c] = (state[c] + state[d]) & 0xFFFFFFFF
    state[b] ^= state[c]
    state[b] = ((state[b] << 7) | (state[b] >> 25)) & 0xFFFFFFFF

def chacha20_block(key, counter, nonce):
    constants = b"expand 32-byte k"
    state = []
    for i in range(0, 16, 4):
        state.append(int.from_bytes(constants[i:i+4], 'little'))
    for i in range(0, 32, 4):
        state.append(int.from_bytes(key[i:i+4], 'little'))
    state.append(counter)
    for i in range(0, 12, 4):
        state.append(int.from_bytes(nonce[i:i+4], 'little'))

    working_state = state[:]

    for _ in range(10):
        quarter_round(working_state, 0, 4, 8, 12)
        quarter_round(working_state, 1, 5, 9, 13)
        quarter_round(working_state, 2, 6, 10, 14)
        quarter_round(working_state, 3, 7, 11, 15)
        quarter_round(working_state, 0, 5, 10, 15)
        quarter_round(working_state, 1, 6, 11, 12)
        quarter_round(working_state, 2, 7, 8, 13)
        quarter_round(working_state, 3, 4, 9, 14)

    for i in range(16):
        working_state[i] = (working_state[i] + state[i]) & 0xFFFFFFFF

    result = bytearray()
    for i in range(16):
        result.extend(working_state[i].to_bytes(4, 'little'))
    return bytes(result)

def chacha20_encrypt(key, counter, nonce, data):
    ciphertext = bytearray()
    for i in range(0, len(data), 64):
        block = chacha20_block(key, counter + i // 64, nonce)
        chunk = data[i:i+64]
        for a, b in zip(chunk, block):
            ciphertext.append(a ^ b)

    return bytes(ciphertext)

def poly1305_mac(key, data):
    r = int.from_bytes(key[:16], 'little') & 0x0ffffffc0ffffffc0ffffffc0fffffff
    s = int.from_bytes(key[16:], 'little')

    accumulator = 0
    p = (1 << 130) - 5

    for i in range(0, len(data), 16):
        n = int.from_bytes(data[i:i+16] + b'\x01', 'little')
        accumulator = (accumulator + n) % p
        accumulator = (accumulator * r) % p

    accumulator = (accumulator + s) % (1 << 128)
    return accumulator.to_bytes(16, 'little')

def chacha20_aead_encrypt(key, nonce, plaintext):
    counter = 1
    auth_key = chacha20_block(key, 0, nonce)[:32]
    ciphertext = chacha20_encrypt(key, counter, nonce, plaintext)

    mac_data = struct.pack('<Q', len(ciphertext))
    tag = poly1305_mac(auth_key, ciphertext + mac_data)

    return nonce + tag + ciphertext

def chacha20_aead_decrypt(key, data):
    if len(data) < 28:
        raise ValueError("Data too short")

    nonce = data[:12]
    tag = data[12:28]
    ciphertext = data[28:]

    counter = 1
    auth_key = chacha20_block(key, 0, nonce)[:32]
    mac_data = struct.pack('<Q', len(ciphertext))
    expected_tag = poly1305_mac(auth_key, ciphertext + mac_data)

    if not expected_tag == tag:
        raise ValueError("Invalid tag")

    plaintext = chacha20_encrypt(key, counter, nonce, ciphertext)
    return plaintext

def process_files_in_place(password, directory, operation):
    key = hashlib.sha256(password.encode()).digest()

    for root, dirs, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)

            with open(file_path, 'rb') as f:
                data = f.read()

            nonce = os.urandom(12)

            if operation == 'encrypt':
                processed_data = chacha20_aead_encrypt(key, nonce, data)
            elif operation == 'decrypt':
                processed_data = chacha20_aead_decrypt(key, data)
            else:
                raise ValueError("Operation must be 'encrypt' or 'decrypt'")

            with open(file_path, 'wb') as f:
                f.write(processed_data)

            print(f"{operation.capitalize()}ed {file_path}")

# 示例用法
password = "your_password"
directory = "your_directory_path"

# 批量加密文件
process_files_in_place(password, directory, 'encrypt')

# 批量解密文件
process_files_in_place(password, directory, 'decrypt')
