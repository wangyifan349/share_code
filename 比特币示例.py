import os
import hashlib
import ecdsa

# 椭圆曲线 secp256k1标准参数
p = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1  # 椭圆曲线质数 p
a = 0  # 椭圆曲线参数 a
b = 7  # 椭圆曲线参数 b
G = (0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798, 
     0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)  # 椭圆曲线基点 G
n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141  # 曲线的阶 n

def generate_private_key():  # 生成私钥
    private_key = int.from_bytes(os.urandom(32), 'big')  # 生成32字节随机数并转为整数
    while private_key >= n or private_key == 0:  # 确保私钥在 [1, n-1] 范围内
        private_key = int.from_bytes(os.urandom(32), 'big')
    return private_key

def generate_public_key(private_key):  # 根据私钥生成公钥
    sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)  # 初始化签名对象
    vk = sk.get_verifying_key()  # 抽取公钥
    public_key = vk.to_string().hex()  # 转换为16进制字符串（未压缩格式）
    return public_key

def generate_bitcoin_address(public_key):  # 生成比特币地址
    public_key_hash = hashlib.sha256(bytes.fromhex(public_key)).digest()  # SHA-256哈希
    public_key_hash = hashlib.new('ripemd160', public_key_hash).digest()  # RIPEMD-160哈希
    version = b'\x00'  # 添加版本字节（主网为0x00）
    vh160 = version + public_key_hash  # 拼接版本和公钥哈希
    checksum = hashlib.sha256(vh160).digest()  # 两次SHA-256，计算校验和
    checksum = hashlib.sha256(checksum).digest()[:4]  # 校验和取前4字节
    bitcoin_address = vh160 + checksum  # 拼接地址主体和校验值
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'  # Base58字母表
    base58_address, num = '', int.from_bytes(bitcoin_address, 'big')  # 转为整数
    while num > 0:  # Base58编码
        num, remainder = divmod(num, 58)
        base58_address = alphabet[remainder] + base58_address
    num_leading_zeros = len([b for b in bitcoin_address if b == 0])  # 数0字节
    return '1' * num_leading_zeros + base58_address  # 0字节对应 Base58 中的 '1'

private_key = generate_private_key()  # 生成私钥
public_key = generate_public_key(private_key)  # 生成公钥
bitcoin_address = generate_bitcoin_address(public_key)  # 生成比特币地址

print('私钥：', private_key)
print('公钥：', public_key)
print('比特币地址：', bitcoin_address)

def sign_message(private_key, message):  # 使用私钥签名消息
    sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)  # 创建签名密钥
    signature = sk.sign(message.encode())  # 对消息签名
    return signature.hex()  # 返回16进制表示的签名

def verify_signature(public_key, message, signature):  # 验证签名是否有效
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)  # 创建验证公钥
    try:
        vk.verify(bytes.fromhex(signature), message.encode())  # 验证签名
        return True
    except ecdsa.BadSignatureError:  # 验证失败则返回 False
        return False

message = 'Hello, Bitcoin!'  # 待签名的消息
signature = sign_message(private_key, message)  # 对消息签名
is_valid = verify_signature(public_key, message, signature)  # 验证签名

print('签名：', signature)
print('签名验证结果：', is_valid)

def serialize_transaction(transaction):  # 将交易序列化为16进制字符串形式
    import json
    return json.dumps(transaction, indent=4)  # 简单用JSON方式序列化，方便显示

transaction = {  # 创建虚拟交易（伪交易）
    'version': 1,
    'locktime': 0,
    'inputs': [
        {
            'txid': '0000000000000000000000000000000000000000000000000000000000000000',  # 空输入交易ID
            'vout': 0,
            'scriptSig': '',  # 签名字段（将填充签名）
            'sequence': 4294967295
        }
    ],
    'outputs': [
        {
            'value': 0.01,  # 发送金额 (单位BTC)
            'scriptPubKey': '76a914' + hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(public_key)).digest()).hexdigest() + '88ac'  # P2PKH输出脚本
        }
    ]
}

signature = sign_message(private_key, str(transaction))  # 对交易串进行签名
transaction['inputs'][0]['scriptSig'] = signature  # 添加签名到 input 的 scriptSig 字段
transaction_hex = serialize_transaction(transaction)  # 序列化交易

print('交易 (序列化结果)：', transaction_hex)
