from mc_protocol.network.game.packets.login.C2SLoginStartPacket import C2SLoginStartPacket
from mc_protocol.network.game.packets.login.S2CEncryptionRequest import S2CEncryptionRequest
from mc_protocol.network.game.packets.login.C2SEncryptionResponse import C2SEncryptionResponse
from mc_protocol.network.game.packets.login.S2CLoginSuccess import S2CLoginSuccess
from mc_protocol.network.game.packets.login.S2CSetCompression import S2CSetCompression
from mc_protocol.network.ping.modern_pinger import ModernPinger
from mc_protocol.network.ping.old_pinger import OldPinger
from utils.player_utils import PlayerUtils
from mc_protocol.network.packet.varint_processor import VarIntProcessor
from mc_protocol.network.packet.packet_encryptor import PacketEncryptor
from mc_protocol.network.packet.packet_compresser import PacketCompresser
from mc_protocol.network.oauth.oauth import oauth
from mc_protocol.network.game.packets.login.C2MojangSession import authWithMojang
import socket
from utils.version.version import MinecraftVersion
'''u = PlayerUtils.getOnlinePlayerUUIDFromMojangRest("pwp_ZYN")
pinger = ModernPinger(765)
pinger.setHost("cn-js-sq.wolfx.jp")
pinger.setPort(25566)
pinger.ping()
protocol = pinger.getServerProtocol()
with socket.create_connection(("cn-js-sq.wolfx.jp", 25566,), 5.0) as sock:
    lsp = C2SLoginStartPacket("pwp_ZYN", u, protocol, 25566)
    sock.send(lsp.getHandshake())
    sock.send(lsp.getPacket())
    er = sock.recv(4096)
    s2cer = S2CEncryptionRequest(er)
    c2ser= C2SEncryptionResponse(s2cer.getPublicKey(), s2cer.getVerifyToken())
    at = None
    with open("./tests/accesstoken.txt", 'r') as f:
        at = f.read()
    print(authWithMojang(at, u, '', c2ser.sharedSecret, s2cer.getPublicKey()))
    sock.send(c2ser.getPacket())
    print(c2ser.getEncryptor().deEncryptPacket(sock.recv(4096)))'''

# ⚠️ UUID 要用不带 "-" 的
USERNAME = "wyh_"

HOST = "cn-js-sq.wolfx.jp"
PORT = 25566

p = oauth()
ACCESSTOKEN = p['access_token']

UUID = p['uuid']
PINGER = ModernPinger(765)
PINGER.setHost(HOST)
PINGER.setPort(PORT)
PINGER.timeout = 5.0
PINGER.ping()
V = PINGER.getServerProtocol()
print(f"[INFO] Server protocol version = {V}")

with socket.create_connection((HOST, PORT)) as sock:
    # 1. Login Start
    C2SLSP = C2SLoginStartPacket(USERNAME, UUID, V, PORT)
    sock.send(C2SLSP.getHandshake())
    sock.send(C2SLSP.getPacket())
    print("[SEND] C2SLoginStartPacket")
    
    # 2. Encryption Request
    S2CER = S2CEncryptionRequest(VarIntProcessor.readPacket(sock))
    print("[RECV] S2CEncryptionRequest")

    # 3. Encryption Response
    C2SER = C2SEncryptionResponse(S2CER.getPublicKey(), S2CER.getVerifyToken())

    RESULT = authWithMojang(ACCESSTOKEN, UUID, S2CER.getServerId(), C2SER.sharedSecret, S2CER.getPublicKey())
    print(f"[AUTH] Mojang session result = {RESULT}")

    sock.send(C2SER.getPacket())
    print("[SEND] C2SEncryptionResponse")

    # 4. 开启加密
    ENCRYPTOR = PacketEncryptor(C2SER.sharedSecret)

    # 5. Set Compression
    PACKET = VarIntProcessor.readEncryptedPacket(sock, ENCRYPTOR)
    S2CSC = S2CSetCompression(PACKET)
    THRESHOLD = S2CSC.getThreshold()
    print(f"[RECV] S2CSetCompression, threshold = {THRESHOLD}")

    COMPRESSER = PacketCompresser(THRESHOLD)

    # 6. Login Success
    P = VarIntProcessor.readEncryptedPacket(sock, ENCRYPTOR)
    P = COMPRESSER.uncompressPacket(P)
    print(f"[RECV] S2CLoginSuccess, raw = {P}")