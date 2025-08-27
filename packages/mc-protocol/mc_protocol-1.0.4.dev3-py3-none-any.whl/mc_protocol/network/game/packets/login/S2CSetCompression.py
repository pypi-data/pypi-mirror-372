from mc_protocol.network.game.packet import Packet, ProtocolDirection, ProtocolState
from mc_protocol.network.packet.varint_processor import VarIntProcessor
from mc_protocol.network.packet.packet_encryptor import PacketEncryptor

class S2CSetCompression(Packet):
    PACKET_ID = 0x03
    PROTOCOL_STATE = ProtocolState.LOGIN
    PROTOCOL_DIRECTION = ProtocolDirection.S2C
    def __init__(self, packet: bytes):
        packet_length, packet_id, content = VarIntProcessor.unpackPacket(packet)
        assert packet_id == 0x03, f"Expected packet_id=0x03, got {packet_id}"

        threshold, _ = VarIntProcessor.readVarInt(content, 0)
        self.threshold = threshold

    def getThreshold(self) -> int:
        return self.threshold