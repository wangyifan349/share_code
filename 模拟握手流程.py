from Crypto.PublicKey import ECC
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF

# 1. 公私钥生成与交换
# 用户 A 生成 ECC 密钥对
private_key_A = ECC.generate(curve="P-256")
public_key_A = private_key_A.public_key()

# 用户 B 生成 ECC 密钥对
private_key_B = ECC.generate(curve="P-256")
public_key_B = private_key_B.public_key()

# 用户 A 和 用户 B 通过对方的公钥和自己的私钥计算共享密钥 (ECDH)
shared_secret_A = private_key_A.exchange(ECC.ECDH(), public_key_B)
shared_secret_B = private_key_B.exchange(ECC.ECDH(), public_key_A)

# 验证共享密钥相同
assert shared_secret_A == shared_secret_B

# 将共享密钥通过 HKDF 派生为对称密钥
shared_secret = shared_secret_A  # 或 shared_secret_B，结果相同
key = HKDF(shared_secret, 32, b"", SHA256)  # 32 字节对称密钥，适合 AES-256

# 2. 用户 A 使用对称密钥加密消息 (AES-GCM)
def aes_gcm_encrypt(plaintext, key):
    """
    加密函数: 使用 AES-GCM
    """
    nonce = get_random_bytes(12)  # 12 字节随机数
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return nonce, tag, ciphertext

def aes_gcm_decrypt(nonce, tag, ciphertext, key):
    """
    解密函数: 使用 AES-GCM
    """
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

message = "Hello, this is a secret message from A to B!"

# 用户 A 加密消息
nonce, tag, ciphertext = aes_gcm_encrypt(message, key)
print(f"密文: {ciphertext.hex()}")
print(f"Nonce: {nonce.hex()}")
print(f"Tag: {tag.hex()}")

# 3. 用户 B 使用对称密钥解密消息
decrypted_message = aes_gcm_decrypt(nonce, tag, ciphertext, key)
print(f"解密后的消息: {decrypted_message}")

# 4. 验证解密的消息和原始消息相同
assert message == decrypted_message








from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom
# 1. 公私钥生成与交换
# 用户 A 生成 ECC 密钥对
private_key_A = ec.generate_private_key(ec.SECP256R1())
public_key_A = private_key_A.public_key()
# 用户 B 生成 ECC 密钥对
private_key_B = ec.generate_private_key(ec.SECP256R1())
public_key_B = private_key_B.public_key()
# 用户 A 和 用户 B 通过对方的公钥和自己的私钥计算共享密钥 (ECDH)
shared_secret_A = private_key_A.exchange(ec.ECDH(), public_key_B)
shared_secret_B = private_key_B.exchange(ec.ECDH(), public_key_A)
# 验证共享密钥相同
assert shared_secret_A == shared_secret_B
# 将共享密钥通过 HKDF 派生为对称密钥
shared_secret = shared_secret_A  # 或 shared_secret_B，结果相同
hkdf = HKDF(
    algorithm=hashes.SHA256(),
    length=32,  # 32 字节对称密钥，适合 AES-256
    salt=None,
    info=b"",
)
key = hkdf.derive(shared_secret)
# 2. 用户 A 使用对称密钥加密消息 (AES-GCM)
def aes_gcm_encrypt(plaintext, key):
    nonce = urandom(12)  # 12 字节随机数
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return nonce, encryptor.tag, ciphertext
def aes_gcm_decrypt(nonce, tag, ciphertext, key):
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()
message = "Hello, this is a secret message from A to B!"
# 用户 A 加密消息
nonce, tag, ciphertext = aes_gcm_encrypt(message, key)
print(f"密文: {ciphertext.hex()}")
print(f"Nonce: {nonce.hex()}")
print(f"Tag: {tag.hex()}")
# 3. 用户 B 使用对称密钥解密消息
decrypted_message = aes_gcm_decrypt(nonce, tag, ciphertext, key)
print(f"解密后的消息: {decrypted_message}")
# 4. 验证解密的消息和原始消息相同
assert message == decrypted_message



以上是有缺陷的，它采取了有缺陷的椭圆曲线


from nacl.public import PrivateKey, PublicKey
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF

# 1. 公私钥生成与密钥交换 (使用 NaCl 库和 Curve25519)
# 用户 A 和 用户 B 生成各自的私钥和公钥
private_key_A = PrivateKey.generate()
public_key_A = private_key_A.public_key

private_key_B = PrivateKey.generate()
public_key_B = private_key_B.public_key

# 用户 A 和 用户 B 计算共享密钥 (Curve25519 的 ECDH 机制)
shared_secret_A = private_key_A.exchange(public_key_B)
shared_secret_B = private_key_B.exchange(public_key_A)

# 验证共享密钥相同
assert shared_secret_A == shared_secret_B

# 派生对称密钥 (使用 HKDF 和 SHA-256)
shared_secret = shared_secret_A  # 公共共享密钥
key = HKDF(
    master=shared_secret,
    key_len=32,  # 32 字节对称密钥，适合 AES-256
    salt=None,
    hashmod=SHA256
)

# 2. 实现 AES-GCM 加密和解密 (使用 pycryptodome)
def aes_gcm_encrypt(plaintext, key):
    nonce = get_random_bytes(12)  # 生成随机 12 字节 nonce
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
    return nonce, tag, ciphertext

def aes_gcm_decrypt(nonce, tag, ciphertext, key):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext.decode()

# 加密消息
message = "Hello, this is a secure message!"
nonce, tag, ciphertext = aes_gcm_encrypt(message, key)
print(f"密文: {ciphertext.hex()}")
print(f"Nonce: {nonce.hex()}")
print(f"Tag: {tag.hex()}")
# 解密消息
decrypted_message = aes_gcm_decrypt(nonce, tag, ciphertext, key)
print(f"解密后的消息: {decrypted_message}")
# 验证解密后的消息是否正确
assert message == decrypted_message




from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from os import urandom

# 1. 用户 A 和 用户 B 生成各自的 X25519 密钥对
private_key_A = X25519PrivateKey.generate()  # 用户 A 的私钥
public_key_A = private_key_A.public_key()    # 用户 A 的公钥

private_key_B = X25519PrivateKey.generate()  # 用户 B 的私钥
public_key_B = private_key_B.public_key()    # 用户 B 的公钥

# 2. 用户 A 和 用户 B 通过私钥和对方公钥计算共享密钥
shared_secret_A = private_key_A.exchange(public_key_B)  # 用户 A 计算共享密钥
shared_secret_B = private_key_B.exchange(public_key_A)  # 用户 B 计算共享密钥

# 验证共享密钥相同
assert shared_secret_A == shared_secret_B

# 3. 用 HKDF 派生对称密钥（32 字节 AES-256）
derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"",  # 额外参数，这里可以为空
).derive(shared_secret_A)

# 4. 使用 AES-GCM 模式加密和解密
def aes_gcm_encrypt(plaintext, key):
    nonce = urandom(12)  # 12 字节随机数
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return nonce, encryptor.tag, ciphertext

def aes_gcm_decrypt(nonce, tag, ciphertext, key):
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()

# 加密消息
message = "Hello, this is a secure message!"
nonce, tag, ciphertext = aes_gcm_encrypt(message, derived_key)
print(f"密文: {ciphertext.hex()}")
print(f"Nonce: {nonce.hex()}")
print(f"Tag: {tag.hex()}")

# 解密消息
decrypted_message = aes_gcm_decrypt(nonce, tag, ciphertext, derived_key)
print(f"解密后的消息: {decrypted_message}")

# 验证解密后的消息是否正确
assert message == decrypted_message



实际编写这种软件还需要GUI，网部分。不只是加密

