# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2024-10-29 10:49:21
:LastEditors: ChenXiaolei
:Description: 加密帮助类
"""
import base64
import os
from seven_framework.coding import *
import hashlib
import re

class CryptoHelper:
    """
    :Description: 加密帮助类
    """

    @classmethod
    def md5_encrypt(cls, source, salt="", encoding="utf-8"):
        """
        :Description: md5加密，支持加盐算法
        :param source: 需加密的字符串
        :param salt: 加盐算法参数值
        :param encoding: 字符串编码
        :return: md5加密后的字符串
        :last_editors: ChenXiaolei
        """
        if not isinstance(source, str) or not isinstance(salt, str):
            return ""
        return cls.md5_encrypt_bytes((source + salt).encode(encoding))

    @classmethod
    def md5_encrypt_bytes(cls, source):
        """
        :Description: md5字节流加密
        :param source: 字节流
        :return: md5加密后的字符串
        :last_editors: ChenXiaolei
        """
        if not isinstance(source, bytes):
            return ""
        encrypt = hashlib.md5()
        encrypt.update(source)
        md5value = encrypt.hexdigest()
        return md5value

    @classmethod
    def md5_encrypt_int(cls, source, salt="", encoding="utf-8"):
        """
        :Description: md5加密，返回数值
        :param source: 需加密的字符串
        :param salt: 加盐算法参数值
        :return: md5加密后的数值
        :last_editors: ChenXiaolei
        """
        md5_16 = cls._convert_md5(cls.md5_encrypt(source, salt, encoding))
        hash_code_start = int.from_bytes(md5_16[0:8],
                                         byteorder='little',
                                         signed=True)
        hash_code_end = int.from_bytes(md5_16[8:16],
                                       byteorder='little',
                                       signed=True)
        return hash_code_start ^ hash_code_end

    @classmethod
    def md5_file(cls, file_path):
        """
        :description: 计算文件MD5值
        :param file_path: 文件路径
        :return 文件MD5值
        :last_editors: ChenXiaolei
        """
        with open(file_path, 'rb') as f:
            data = f.read()
        return hashlib.md5(data).hexdigest()

    @classmethod
    def _convert_md5(cls, origin):
        """
        :Description: md5字符串转16进制数组
        :param origin: 原md5字符串
        :return: 16进制数组
        :last_editors: ChenXiaolei
        """
        result = []
        s = ""
        for i in range(len(origin)):
            s += origin[i]
            if i % 2 != 0:
                int_hex = int(s, 16)
                result.append(int_hex)
                s = ""

        return result

    @classmethod
    def sha1_encrypt(cls, source, encoding="utf-8"):
        """
        :Description: sha1加密
        :param source: 需加密的字符串
        :return: sha1加密后的字符串
        :last_editors: ChenXiaolei
        """
        from hashlib import sha1
        sha1_sign = sha1()
        if isinstance(source, str):
            sha1_sign.update(source.encode(encoding))
        elif isinstance(source, bytes):
            sha1_sign.update(source)
        return sha1_sign.hexdigest()

    @classmethod
    def sha256_encrypt(cls, source, encoding="utf-8"):
        """
        :Description: sha256加密
        :param source: 需加密的字符串
        :return: sha256加密后的字符串
        :last_editors: ChenXiaolei
        """
        sha256 = hashlib.sha256()
        if isinstance(source, str):
            sha256.update(source.encode(encoding))
        elif isinstance(source, bytes):
            sha256.update(source)
        result = sha256.hexdigest()
        return result

    @classmethod
    def base64_encode(cls, source, encoding="utf-8"):
        """
        :Description: base64加密
        :param source: 需加密的字符串
        :return: 加密后的bytes
        :last_editors: ChenXiaolei
        """
        if not source.strip():
            return ""
        import base64
        encode_string = base64.b64encode(source.encode(encoding=encoding))
        return encode_string.decode(encoding=encoding)

    @classmethod
    def base64_decode(cls, source, encoding="utf-8"):
        """
        :Description: base64解密
        :param source: 需加密的字符串
        :return: 解密后的字符串
        :last_editors: ChenXiaolei
        """
        if not source.strip():
            return ""
        import base64
        decode_string = base64.b64decode(source)
        return decode_string.decode(encoding=encoding)

    @classmethod
    def _aes_pad(cls, text, encoding="utf-8"):
        """
        :Description: 填充函数，使被加密数据的字节码长度是block_size的整数倍
        :param text: 填充字符串
        :return: 填充后的字符串
        :last_editors: ChenXiaolei
        """
        from Crypto.Cipher import AES
        length = AES.block_size
        count = len(text.encode(encoding))
        add = length - (count % length)
        entext = text + (chr(add) * add)
        return entext

    @classmethod
    def aes_encrypt(cls, source, password, encoding="utf-8"):
        """
        :Description: AES加密,ECB & PKCS7
        :param source: 待加密字符串
        :param password: 密钥 必须为16位或32位
        :return: 加密后的字符串
        :last_editors: ChenXiaolei
        """
        from Crypto.Cipher import AES
        if isinstance(password, str):
            password = password.encode(encoding)

        aes = AES.new(password, AES.MODE_ECB)  # 初始化AES,ECB模式的实例

        resource = aes.encrypt(
            cls._aes_pad(source, encoding).encode(encoding))
        result = str(base64.b64encode(resource), encoding=encoding)
        return result

    @classmethod
    def aes_decrypt(cls, source, password, encoding="utf-8"):
        """
        :Description: AES解密,ECB & PKCS7
        :param source: 待解密字符串
        :param password: 密钥 必须为16位或32位
        :return: 解密后的明文
        :last_editors: ChenXiaolei
        """
        from Crypto.Cipher import AES
        if isinstance(password, str):
            password = password.encode(encoding)

        aes = AES.new(password, AES.MODE_ECB)  # 初始化AES,ECB模式的实例

        # 截断函数，去除填充的字符
        def unpad(date):
            return date[0:-ord(date[-1])]

        resource = base64.decodebytes(source.encode(encoding))
        result = aes.decrypt(resource).decode(encoding)
        return unpad(result)

    @classmethod
    def rsa_signature(cls, private_key, source):
        """
        :description: RSA签名(SHA)
        :param private_key: RSA私钥
        :param source: 签名字符串
        :return 签名摘要
        :last_editors: ChenXiaolei
        """
        from Crypto.Hash import SHA
        from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
        if os.path.isfile(private_key):
            private_key = cls.get_rsa_key_from_file(private_key)

        if not private_key:
            return None

        signer = PKCS1_signature.new(private_key)  # 设置签名的类
        digest = SHA.new()  # 创建sha加密的类
        digest.update(source.encode())  # 将要加密的数据进行sha加密
        sign = signer.sign(digest)  # 对数据进行签名
        # 对签名进行处理
        sign = base64.b64encode(sign)  # 对数据进行base64加密
        sign = sign.decode()  # 再进行编码

        return sign

    @classmethod
    def get_rsa_key_from_file(cls, key_file):
        """
        :description: 从文件中获取 rsa 密钥
        :param key_file: rsa密钥文件
        :return rsa密钥内容
        :last_editors: ChenXiaolei
        """
        from Crypto.PublicKey import RSA
        with open(key_file) as f:
            key_file_content = f.read()
            rsa_key = RSA.importKey(key_file_content)
        return rsa_key

    @classmethod
    def create_rsa_keys(cls, bits=1024):
        """
        :description: 生成rsa密钥
        :param bits: 密钥长度(bit)
        :return 元组(public_key, private_key)
        :last_editors: ChenXiaolei
        """
        import Crypto.PublicKey.RSA
        key_pair = Crypto.PublicKey.RSA.generate(bits,
                                                 Crypto.Random.new().read)

        public_key = key_pair.publickey().exportKey()
        private_key = key_pair.exportKey()
        return (public_key, private_key)

    @classmethod
    def create_rsa_keys_certificate(cls,
                                    format='PEM',
                                    public_pem_save_path='./public_key.pem',
                                    private_pem_save_path='./private_key.pem',
                                    bits=1024):
        """
        :description: 生成rsa密钥证书(pem格式)
        :param public_pem_save_path: rsa公钥保存的路径
        :param private_pem_save_path: rsa公钥保存的路径
        :param bits: 密钥长度(bit)
        :return 无
        :last_editors: ChenXiaolei
        """
        import Crypto.PublicKey.RSA
        key_pair = Crypto.PublicKey.RSA.generate(bits,
                                                 Crypto.Random.new().read)

        public_key = key_pair.publickey().exportKey(format)
        with open(public_pem_save_path, 'wb+') as f:
            f.write(public_key)
        private_key = key_pair.exportKey()
        with open(private_pem_save_path, 'wb+') as f:
            f.write(private_key)

    @classmethod
    def rsa_encrypt(cls, source, public_key):
        """
        :description: rsa加密
        :param source: 明文字符串
        :param private_key: rsa公钥
        :return 密文
        :last_editors: ChenXiaolei
        """
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_v1_5

        cipher_public_obj = PKCS1_v1_5.new(RSA.import_key(public_key))

        if type(source) == str:
            source = source.encode('utf-8')

        encrypt = cipher_public_obj.encrypt(source)

        # base64编码，并转为字符串
        text_encrypted_base64 = base64.b64encode(encrypt).decode()

        return text_encrypted_base64

    @classmethod
    def rsa_decrypt(cls, source, private_key):
        """
        :description: rsa解密
        :param source: 密文
        :param private_key: rsa私钥
        :return 明文字符串
        :last_editors: ChenXiaolei
        """
        from Crypto.PublicKey import RSA
        from Crypto.Cipher import PKCS1_v1_5
        import Crypto.Random
        cipher_private_obj = PKCS1_v1_5.new(RSA.importKey(private_key))
        decrypt = cipher_private_obj.decrypt(
            base64.b64decode(source.encode('utf-8')),
            Crypto.Random.new().read)

        if decrypt and type(decrypt) == bytes:
            decrypt = decrypt.decode()

        return decrypt

    HASH_FUNCS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}
    @classmethod
    def get_dir_hash(cls, dir_path,hashfunc="md5",excluded_files=None,ignore_hidden=True,followlinks=False,excluded_extensions=None,include_paths=False,only_dirs=None):
        """
        :description: 计算目录哈希值
        :param path
        :return 目录哈希值
        :last_editors: ChenXiaolei
        """
        hash_func = cls.HASH_FUNCS.get(hashfunc)
        if not hash_func:
            raise NotImplementedError("{} not implemented.".format(hashfunc))

        if not excluded_files:
            excluded_files = []

        if not excluded_extensions:
            excluded_extensions = []

        if not os.path.isdir(dir_path):
            raise TypeError(f"{dir_path} is not a directory.")

        if only_dirs:
            for i in range(len(only_dirs)):
                only_dirs[i] = f"{dir_path}/{only_dirs[i]}"
                    
        hashvalues = []
        for root, dirs, files in os.walk(dir_path, topdown=True, followlinks=followlinks):
            if root!=dir_path and only_dirs:
                if not any(root.startswith(d) for d in only_dirs):
                    continue

            if ignore_hidden and (re.search(r"/\.", root) or root.find("__pycache__")>-1):
                continue

            dirs.sort()
            files.sort()

            for fname in files:
                if ignore_hidden and fname.startswith("."):
                    continue

                if fname.split(".")[-1:][0] in excluded_extensions:
                    continue

                if fname in excluded_files:
                    continue
                # print(f"{fname} : {cls._file_hash(os.path.join(root, fname), hash_func)}")
                hashvalues.append(cls._file_hash(os.path.join(root, fname), hash_func))

                if include_paths:
                    hasher = hash_func()
                    # get the resulting relative path into array of elements
                    path_list = os.path.relpath(os.path.join(root, fname)).split(os.sep)
                    # compute the hash on joined list, removes all os specific separators
                    hasher.update(''.join(path_list).encode('utf-8'))
                    hashvalues.append(hasher.hexdigest())

        return cls._reduce_hash(hashvalues, hash_func)
    
    def _file_hash(file_path, hashfunc):
        hasher = hashfunc()
        blocksize = 64 * 1024

        if not os.path.exists(file_path):
            return hasher.hexdigest()

        with open(file_path, "rb") as fp:
            while True:
                data = fp.read(blocksize)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    
    def _reduce_hash(hash_list, hashfunc):
        hasher = hashfunc()
        for hashvalue in sorted(hash_list):
            hasher.update(hashvalue.encode("utf-8"))
        return hasher.hexdigest()
