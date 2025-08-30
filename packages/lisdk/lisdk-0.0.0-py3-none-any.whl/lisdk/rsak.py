import os
import time
import json
import base64
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

    
class RSAK:
    @staticmethod
    def readRSAKey(key_file) -> bytes:
        """
        获取rsa密钥
        @param key_file: RSA密钥文件路径
        @return: rsa密钥字节内容
        """
        with open(key_file, mode='rb') as f:
            return RSA.import_key(f.read())

    @staticmethod
    def getSignature(rsaKey: bytes, data: dict, ensure_ascii=False) -> str:
        """
        根据RSA私钥获取签名值
        """
        pkcs = PKCS1_v1_5.new(rsaKey)
        data_bytes = json.dumps(data, separators=(',', ':'), ensure_ascii=ensure_ascii).encode('utf-8')
        sha256 = SHA256.new(data_bytes)
        signature = base64.b64encode(pkcs.sign(sha256)).decode('utf-8')
        return signature

    @staticmethod
    def verifySignature(rsaKey: bytes, data: dict, signature: str, ensure_ascii=False) -> bool:
        """
        根据RSA公钥获取签名验证结果
        """
        pkcs = PKCS1_v1_5.new(rsaKey)
        signature_hash = base64.b64decode(signature)
        data_bytes = json.dumps(data, separators=(',', ':'), ensure_ascii=ensure_ascii).encode('utf-8')
        sha256 = SHA256.new(data_bytes)
        result = pkcs.verify(sha256, signature_hash)
        return result
    
    @staticmethod
    def genRSAKey(dir: str, key_size: int = 2048, pkcs=8, prefix: str = None):
        """
        生成RSA密钥
        @return: 返回生成的密钥内容
        """
        dir = dir if dir.endswith("/") else dir + "/"
        dir = dir + f"{int(time.time())}/" if prefix is None else dir + f"{prefix}-{int(time.time())}/"
        try:
            os.makedirs(dir, exist_ok=True)
            key = RSA.generate(key_size)
            private_key = key.export_key(format="PEM", pkcs=pkcs)
            public_key = key.publickey().export_key(format="PEM")

            with open(f"{dir}/private_pkcs{pkcs}.pem", "wb") as f:
                f.write(private_key)
            with open(f"{dir}/public.pem", "wb") as f:
                f.write(public_key)

            return {
                "private_key": private_key,
                "public_key": public_key
            }
        except Exception as e:
            raise RuntimeError(f"生成RSA密钥失败: {e}")