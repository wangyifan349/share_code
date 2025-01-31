import os
import hashlib
import ecdsa
import bech32

# 椭圆曲线 secp256k1 标准参数
p = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1  # 椭圆曲线质数 p
n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141  # 椭圆曲线阶 n

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

def generate_bitcoin_address(public_key):  # 生成普通比特币地址 (Base58 P2PKH)
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

def generate_bip84_address(public_key):  # 生成BIP-84地址 (Bech32原生SegWit P2WPKH地址)
    sha256 = hashlib.sha256(bytes.fromhex(public_key)).digest()  # SHA256哈希
    ripemd160 = hashlib.new('ripemd160', sha256).digest()  # RIPEMD-160哈希
    address = bech32.encode('bc', 0, ripemd160)  # Bech32编码，'bc'代表主网前缀，使用版本号 0
    return address

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

def serialize_transaction(transaction):  # 将交易序列化为16进制字符串形式
    import json
    return json.dumps(transaction, indent=4)  # 简单用JSON方式序列化，方便显示

# 生成私钥、公钥
private_key = generate_private_key()  # 生成私钥
public_key = generate_public_key(private_key)  # 生成公钥

# 生成比特币地址
bitcoin_address = generate_bitcoin_address(public_key)  # 生成普通的Base58地址 (P2PKH)
bip84_address = generate_bip84_address(public_key)  # 生成BIP-84原生SegWit地址 (Bech32)

print('私钥：', private_key)
print('公钥：', public_key)
print('普通比特币地址 (Base58 P2PKH)：', bitcoin_address)
print('BIP-84地址 (Bech32 P2WPKH)：', bip84_address)

# 签名与验证
message = 'Hello, Bitcoin!'  # 待签名的消息
signature = sign_message(private_key, message)  # 对消息签名
is_valid = verify_signature(public_key, message, signature)  # 验证签名

print('签名：', signature)
print('签名验证结果：', is_valid)

# 创建虚拟交易示例
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






import os, hashlib, ecdsa, bech32, base58

def generate_private_key():  # 生成一个有效的比特币私钥，范围限制在 [1, n-1]
    n = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
    private_key = int.from_bytes(os.urandom(32), 'big')
    while private_key == 0 or private_key >= n:
        private_key = int.from_bytes(os.urandom(32), 'big')
    return private_key

def generate_public_key(private_key):  # 根据私钥生成未压缩格式的公钥 (以 '04' 开头)
    sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return '04' + vk.to_string().hex()

def generate_bitcoin_address(public_key):  # 基于 P2PKH 标准生成比特币地址 (Base58 格式)
    public_key_hash = hashlib.sha256(bytes.fromhex(public_key)).digest()
    public_key_hash = hashlib.new('ripemd160', public_key_hash).digest()
    version = b'\x00'
    payload = version + public_key_hash
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    bitcoin_address_bytes = payload + checksum
    return base58.b58encode(bitcoin_address_bytes).decode()

def generate_bip84_address(public_key):  # 基于原生 SegWit P2WPKH 地址 (BIP-84，Bech32 格式)
    sha256 = hashlib.sha256(bytes.fromhex(public_key)).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    return bech32.encode('bc', 0, ripemd160)

def private_key_to_wif(private_key):  # 将私钥转为 WIF 格式，方便导入钱包
    private_key_bytes = private_key.to_bytes(32, 'big')
    extended_key = b'\x80' + private_key_bytes
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    return base58.b58encode(extended_key + checksum).decode()

def validate_bitcoin_address(address):  # 验证比特币 P2PKH 地址是否有效
    try:
        decoded = base58.b58decode(address)
        payload, checksum = decoded[:-4], decoded[-4:]
        calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        return checksum == calculated_checksum
    except Exception:
        return False

def sign_message(private_key, message):  # 使用私钥对消息签名
    sk = ecdsa.SigningKey.from_secret_exponent(private_key, curve=ecdsa.SECP256k1)
    return sk.sign(message.encode()).hex()

def verify_signature(public_key, message, signature):  # 验证消息签名的有效性
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key[2:]), curve=ecdsa.SECP256k1)
    try:
        return vk.verify(bytes.fromhex(signature), message.encode())
    except ecdsa.BadSignatureError:
        return False

def serialize_transaction(transaction):  # 将交易对象序列化为 JSON 字符串
    import json
    return json.dumps(transaction, indent=4)

def calculate_txid(transaction_hex):  # 计算交易的 TXID (双 SHA256，字节反转)
    tx_bytes = bytes.fromhex(transaction_hex)
    tx_hash = hashlib.sha256(hashlib.sha256(tx_bytes).digest()).digest()
    return tx_hash[::-1].hex()

# 测试代码
if __name__ == "__main__":
    private_key = generate_private_key()  # 生成私钥
    public_key = generate_public_key(private_key)  # 生成公钥
    bitcoin_address = generate_bitcoin_address(public_key)  # 生成P2PKH地址(Base58)
    bip84_address = generate_bip84_address(public_key)  # 生成P2WPKH地址(Bech32)
    wif = private_key_to_wif(private_key)  # 私钥转 WIF 格式

    print("生成的私钥：", private_key)
    print("WIF 格式私钥：", wif)
    print("生成的公钥：", public_key)
    print("Base58 比特币地址 (P2PKH)：", bitcoin_address)
    print("Bech32 比特币地址 (BIP-84 P2WPKH)：", bip84_address)
    print("P2PKH 地址验证结果：", validate_bitcoin_address(bitcoin_address))

    message = "Hello Bitcoin!"  # 签名与验证签名
    signature = sign_message(private_key, message)
    print("签名：", signature)
    print("签名验证结果：", verify_signature(public_key, message, signature))

    transaction = {  # 模拟伪交易
        'version': 1,
        'locktime': 0,
        'inputs': [{'txid': "0000", 'vout': 0, 'scriptSig': '', 'sequence': 0xffffffff}],
        'outputs': [{'value': 0.001, 'scriptPubKey': "76a914" + hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(public_key)).digest()).hexdigest() + "88ac"}],
    }
    transaction_hex = serialize_transaction(transaction)
    print("序列化交易：", transaction_hex)
    print("交易 TXID：", calculate_txid(transaction_hex.encode().hex()))




