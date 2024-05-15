# Payload helpers
# Payload helpers
import attrs
from attrs import field
import cattrs
from enum import IntEnum, Enum
from typing import List, Union, Any, NewType, Dict


__all__ = [
    "DataClass",
    "ErrorCodes",
    "ThrillsStatusMessage",
    "ThrillsSetConfigMessage",
    "ThrillsCommand",
    "ThrillsCommandResponse",
    "ThrillsPingResponse",
    "ThrillsTimeResponse",
    "ThrillsVersionResponse",
    "ThrillsUpdateFileResponse",
]


class MsgType(IntEnum):
    RADIO_LIST = 1
    LOG = 2
    LINK_MAP = 3
    MULTIPATH = 4
    CHANNEL_SELECTION = 5
    DERIVED_DATA = 6


DataClass = NewType("DataClass", Any)


def restoreEnumClass(data, type):
    name = data[0]
    val = data[1]
    if name in globals():
        inst = globals()[name](val)
    return inst


thrills_msg_serializer = cattrs.Converter()

thrills_msg_serializer.register_unstructure_hook(IntEnum, lambda x: (x.__class__.__name__, x))
thrills_msg_serializer.register_structure_hook(IntEnum, restoreEnumClass)
thrills_msg_serializer.register_unstructure_hook(Enum, lambda x: (x.__class__.__name__, x))
thrills_msg_serializer.register_structure_hook(Enum, restoreEnumClass)


class MissingMACException(Exception):
    def __init__(self, mac, *args, **kwargs):
        self.mac = mac
        super().__init__(*args, **kwargs)


class ErrorCodes(IntEnum):
    NO_ERROR = 0
    UNKNOWN_COMMAND = 1
    UNKNOWN_FAILURE = 2
    BAD_PARAMETERS = 3
    NOT_IMPLEMENTED = 4
    CFG_SET_FAILED = 5
    ERR_BAD_ROLE = 6
    ERR_COMMAND_FAILED = 7
    ERR_CMD_BUSY = 8


class MeshFaceMode(IntEnum):
    UNKNOWN = 0
    AP = 1
    STA = 2

    def __repr__(self):
        return str(self.name)


class SubChannel(str, Enum):
    sub_unk = ""
    quarter = "q"
    half = "h"
    full = "f"

    def __repr__(self):
        return str(self.name)


class Channel(IntEnum):
    ch_unk = -1
    ch1 = 1
    ch2 = 2
    ch3 = 3
    ch4 = 4
    ch5 = 5
    ch6 = 6

    def __repr__(self):
        return str(self.name)


class Power(IntEnum):
    pwr_unk = -1
    auto_0 = 0
    auto_1 = 1
    auto_2 = 2
    auto_3 = 3

    def __repr__(self):
        return str(self.name)


@attrs.define()
class LinkData:
    mac: str = field(factory=str)
    mcs_tx_iw: str = field(factory=str)
    mcs_rx_iw: str = field(factory=str)
    mcs_tx: int = field(factory=int)
    mcs_rx: int = field(factory=int)
    beam_rx: int = field(factory=int)
    beam_tx: int = field(factory=int)
    bytes_tx: int = field(factory=int)
    bytes_rx: int = field(factory=int)
    bytes_tx_mac: int = field(factory=int)
    rcpi: int = field(factory=int)
    snr: int = field(factory=int)
    timestamp: int = field(factory=int)
    ctime: int = field(factory=int)

    def setData(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


@attrs.define()
class ThrillsFaceInfo:
    """Connection information that is face specific"""

    links: List[LinkData] = field(factory=list)
    mode: MeshFaceMode = field(default=MeshFaceMode(0))
    antcfg: str = field(factory=str)

    def get_link_by_mac(self, mac: str) -> LinkData | None:
        for link in self.links:
            if link.mac == mac:
                return link
        return None

    def set_link_by_mac(self, mac, **data: Dict[str, Any]) -> None:
        for link in self.links:
            if link.mac == mac:
                link.setData(**data)
                return None
        raise MissingMACException(mac)


@attrs.define()
class ThrillsMeshIfConnData:
    """Connection Data for a single NPU with face by face Information"""

    if0: ThrillsFaceInfo = field(factory=ThrillsFaceInfo)
    if1: ThrillsFaceInfo = field(factory=ThrillsFaceInfo)

    def get_if(self, num: int) -> ThrillsFaceInfo:
        if num == 0:
            return self.if0
        elif num == 1:
            return self.if1
        else:
            raise ValueError("IF can only be a value of 0 or 1")


@attrs.define()
class ThrillsStatusMessage:
    """Periodic Outgoing Status Packet for Live Data"""

    # [N, S], or [W, E] for PCP [N, S, W, E] for STA  "full_1", "half_l", etc
    subchannel: List[str] = field(factory=list)
    # [N, S], or [W, E] for PCP [N, S, W, E] for STA "1", "5" etc
    channel: List[str] = field(factory=list)
    # [N, S], or [W, E] for both STA and PCP STA isBridged, PCP = num of associated faces
    if_data: ThrillsMeshIfConnData = field(factory=ThrillsMeshIfConnData)
    # GPS data in form of {'lat': float, 'lon': float, 'timestamp': int (ns)}
    gps_data: dict = field(factory=dict)
    # temperature information from NPU/Radios
    temperatures: dict = field(factory=dict)
    #  NPU configuration
    beacon_interval: str = "NA"
    scan_duration: str = "NA"
    powersetting: str = "NA"
    min_rssi_connect: str = "NA"
    npu: str = "SNXXZ"  # Name (SN01A, SN02B, etc)
    version: str = "vZ.Z.Z"  # Version of listener software
    macs: List[str] = field(factory=list)  # [f0 mac, f1 mac]
    role: str = field(factory=str)

    def getLinkStats(self, if_val: int, macs: List[str] | None, stat: str, default: Any = "") -> Dict[str, Any]:
        l_data = {}
        if_data = self.if_data.get_if(if_val)
        if macs is None:
            macs = [link.mac for link in if_data.links]
            for mac in macs:
                try:
                    l_data[mac] = if_data.get_link_by_mac(mac).__getattribute__(stat)
                except AttributeError:
                    l_data[mac] = default
        return l_data


@attrs.define()
class ThrillsSetConfigMessage:
    """Incoming SetCfg Packet info"""

    subch: SubChannel = field(default=SubChannel(""))
    ch0: Channel = field(default=Channel(-1))
    ch1: Channel = field(default=Channel(-1))
    antcfg: List[str] = field(factory=list)  # [N, S, W, E]. Comma separated list of allowed beams, default is "odd"
    powersetting: Power = field(default=Power(-1))

    def generate_param_list(self):
        param_list = []
        param_list.append(str(self.ch0.value))
        param_list.append(str(self.ch1.value))
        param_list.append(str(self.subch.value))
        param_list.append(str(self.powersetting.value))
        return param_list


@attrs.define()
class ThrillsCommand:
    """General Incoming or Outgoing Command Format"""

    cmd: str = ""  # Name of command
    data: Union[dict, None] = None  # Data for that command can be None or Dict


@attrs.define()
class ThrillsCommandResponse:
    """General Fields for Command Response"""

    error: ErrorCodes = 0
    npu: str = "SNXXZ"


@attrs.define()
class ThrillsPingResponse(ThrillsCommandResponse):
    """Response to Ping"""

    msg: str = "PONG"


@attrs.define()
class ThrillsTimeResponse(ThrillsCommandResponse):
    """Response to Time command"""

    time: str = "UNKNOWN"


@attrs.define()
class ThrillsVersionResponse(ThrillsCommandResponse):
    """Response to Version command"""

    version: str = "UNKNOWN"


@attrs.define()
class ThrillsUpdateFileResponse(ThrillsCommandResponse):
    """Response to Update File Command"""

    filename: str = "UNKNOWN"  # filename of response
    restarted: bool = False  # Was services restarted?


if __name__ == "__main__":
    from pprint import pprint
    import json

    status_msg = ThrillsStatusMessage()
    print("\nSTRUCT:")
    pprint(status_msg)
    mesh_sts = ThrillsMeshIfConnData()
    status_msg.if_data = mesh_sts
    unstruct_status_msg = thrills_msg_serializer.unstructure(status_msg)
    print("\nUNSTRUCT:")
    pprint(unstruct_status_msg)
    test_str = json.dumps(unstruct_status_msg)
    print("\nJSON:")
    print(test_str)
    test_dict = json.loads(test_str)
    restruct = thrills_msg_serializer.structure(test_dict, ThrillsStatusMessage)
    print(restruct)

    print("\n\nSet Config\n\n")
    config = ThrillsSetConfigMessage()
    config.ch0 = Channel(2)
    config.ch1 = Channel(3)
    config.subch = SubChannel("q")
    config.powersetting = Power(3)
    config.antcfg = ["odd", "odd", "odd", "odd"]
    print(config)
    cfg_unstructured = thrills_msg_serializer.unstructure(config)
    print(f"\nUnstructured: {cfg_unstructured}")
    config = thrills_msg_serializer.structure(cfg_unstructured, ThrillsSetConfigMessage)
    print(f"\nRe-structured: {config}")
    print(config.generate_param_list())

    print("\n\nResponse:")
    cmd_resp = ThrillsCommandResponse()
    cmd_resp.error = ErrorCodes(5)
    cmd_resp.npu = "SN00A"
    print(cmd_resp)
    unstructured_cmd_resp = thrills_msg_serializer.unstructure(cmd_resp)
    print(unstruct_status_msg)
    print(thrills_msg_serializer.structure(unstructured_cmd_resp, ThrillsCommandResponse))
    # bad_data = {"error": ["int", 5], "npu": "SN10A"}
    # print(thrills_msg_serializer.structure(bad_data, ThrillsCommandResponse))
