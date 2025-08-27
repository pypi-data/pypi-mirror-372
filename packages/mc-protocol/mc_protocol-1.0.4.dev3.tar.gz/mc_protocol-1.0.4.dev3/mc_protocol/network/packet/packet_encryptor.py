from Crypto.Cipher import AES
class PacketEncryptor:
    def __init__(self, sharedSecret):
        self.sharedSecret = sharedSecret
        self.cipher = AES.new(key=self.sharedSecret, mode=AES.MODE_CFB, iv=self.sharedSecret, segment_size=8)
    def deEncryptPacket(self, p: bytes) -> bytes:
        return self.cipher.decrypt(p)
    def EncryptPacket(self, p: bytes) -> bytes:
        return self.cipher.encrypt(p)
    def deEncryptPackets(self, *args: list[bytes]) -> list[bytes]:
        result = []
        for p in args:
            result.append(self.cipher.decrypt(p))
        return result