from base64 import b64decode

from common.util.encrypt_util import encrypt_aes, decrypt_aes


class TestSqlUtil:
    def test_encrypt_aes(self):
        # 示例
        key = b'Sixteen byte key'
        plaintext = b'This is a secret message'

        # 加密
        ciphertext = encrypt_aes(key, plaintext)
        print(ciphertext)

        # 解密
        decrypted_text = decrypt_aes(key, b64decode(ciphertext))
        assert decrypted_text.decode() == 'This is a secret message'




