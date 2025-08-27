from mc_protocol.network.game.packet import ProtocolDirection, ProtocolState, Packet
from mc_protocol.network.packet.varint_processor import VarIntProcessor
from uuid import UUID
import struct
class C2SLoginStartPacket(Packet):
    PACKET_ID = 0x00
    PROTOCOL_STATE = ProtocolState.LOGIN
    PROTOCOL_DIRECTION = ProtocolDirection.C2S
    def __init__(self, username: str, uuid: str, protocolNumber: int, serverPort:int = 25565):
        self.username = username.encode()
        self.uuid = UUID(uuid).bytes
        self.protocolNumber = protocolNumber
        self.serverPort = serverPort
    def getField(self):
        field = (
            VarIntProcessor.packVarInt(len(self.username)) + 
            self.username +
            self.uuid
        )
        return field
    def getPacket(self):
        _ = VarIntProcessor.packVarInt(0x00) + self.getField()
        return VarIntProcessor.packVarInt(len(_)) + _
    def getHandshake(self):
        handshake = (
            b"\x00"
            + VarIntProcessor.packVarInt(self.protocolNumber)
            + VarIntProcessor.packVarInt(len(self.username)) + self.username
            + struct.pack(">H", self.serverPort)
            + b"\x02"  # 2 login
        )
        return VarIntProcessor.packVarInt(len(handshake)) + handshake