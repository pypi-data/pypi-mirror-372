from ul_unipipeline.message.uni_message import UniMessage

from data_gateway_sdk.protocols.nero_bs_packet.http_nero_bs_packet import HttpV0NeroBsPacket


class InputBsHttpNeroV0Message(UniMessage):
    data: HttpV0NeroBsPacket
