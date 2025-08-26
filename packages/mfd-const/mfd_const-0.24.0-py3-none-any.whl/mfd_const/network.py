# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Network module."""

import re
from enum import Enum, auto
from ipaddress import IPv4Network
from typing import Any

from mfd_typing import DeviceID

from mfd_const._internal_data_structures import InternalDict


class Family(Enum):
    """Family Enum."""

    FVL = auto()
    NNT = auto()
    TVL = auto()
    SGVL = auto()
    AVOTON = auto()
    LKV = auto()
    PVL = auto()
    SPVL = auto()
    FPK = auto()
    CPK = auto()
    CPK_SMBM = auto()
    CVL = auto()
    CNV = auto()
    GNRD = auto()
    MEV = auto()
    NNTQ = auto()
    HVL = auto()
    MPK = auto()
    VF = auto()
    HTWL = auto()
    I350 = auto()
    I225 = auto()
    I710 = auto()
    RRC = auto()


family_to_full_name = InternalDict(
    {
        Family.CVL: "Columbiaville",
        Family.CPK: "Columbiapark",
        Family.FVL: "Fortville",
        Family.FPK: "Fortpark",
        Family.CNV: "Connorsville",
        Family.LKV: "Linkville",
        Family.GNRD: "Granite Rapids",
    }
)


class Speed(Enum):
    """Speed Enum."""

    VF_G1 = "1G_VF"
    VF_G10 = "10G_VF"
    VF_G40 = "40G_VF"
    VF_G100 = "100G_VF"

    G1 = "@1G"
    G2 = "@2G"
    G10 = "@10G"
    G40 = "@40G"
    G100 = "@100G"
    G200 = "@200G"

    def __hash__(self) -> int:
        """Return hash representation."""
        return hash(self._name_)

    def __eq__(self, other: Any):
        """Equal."""
        if not isinstance(other, type(self)):
            raise TypeError("Compared values need to be both members of Speed Enum class.")

        return self is other

    def __gt__(self, other: Any):
        """Greater than."""
        if not isinstance(other, type(self)):
            raise TypeError("Compared values need to be both members of Speed Enum class.")

        speed_pattern = r"\D*(?P<speed>\d+)\D*"
        self_speed_match = re.match(speed_pattern, self.value)
        other_speed_match = re.match(speed_pattern, other.value)
        if not self_speed_match or not other_speed_match:
            raise ValueError(
                f"Compared value was not matched to pattern.\nself={self}, other={other}, pattern={speed_pattern}"
            )

        return int(self_speed_match.group("speed")) > int(other_speed_match.group("speed"))

    def __ge__(self, other: Any):
        """Greater or equal."""
        return (self == other) or (self > other)


MEV_SIMICS_IDs = ["0xF002", "0xF003", "0xF00C"]
MEV_NRB_IDs = ["0x1452"]
MEV_IDs = MEV_NRB_IDs + MEV_SIMICS_IDs + ["0x145C"]

DEVICE_IDS = {
    Family.FVL.name: [
        "0x154B",
        "0x154C",
        "0x1571",
        "0x1572",
        "0x1573",
        "0x1580",
        "0x1581",
        "0x1582",
        "0x1583",
        "0x1584",
        "0x1585",
        "0x1586",
        "0x1587",
        "0x1588",
        "0x1589",
        "0x158A",
        "0x158B",
        "0x15FF",
        "0x0DD2",
    ],
    Family.NNT.name: [
        "0x10B6",
        "0x10C6",
        "0x10C7",
        "0x10C8",
        "0x10D8",
        "0x10DB",
        "0x10DD",
        "0x10EC",
        "0x10F1",
        "0x10F4",
        "0x10F7",
        "0x10FB",
        "0x10F9",
        "0x10E1",
        "0x1514",
        "0x1507",
        "0x10F8",
        "0x10FC",
        "0x1517",
        "0x151C",
        "0x10FA",
        "0x1529",
        "0x152A",
        "0x10ED",
        "0x152E",
        "0x154F",
        "0x1551",
        "0x154D",
        "0x1558",
        "0x154A",
        "0x155F",
        "0x155D",
        "0x1557",
    ],
    Family.TVL.name: [
        "0x1512",
        "0x1515",
        "0x1530",
        "0x1528",
        "0x155C",
        "0x155E",
        "0x1560",
    ],
    Family.SGVL.name: ["0x1562", "0x1563", "0x15D1"],
    Family.AVOTON.name: ["0x1F41"],
    Family.LKV.name: [
        "0x57AF",
        "0x57B0",
        "0x57B1",
    ],
    Family.PVL.name: [
        "0x151F",
        "0x1522",
        "0x1523",
        "0x1521",
        "0x1524",
        "0x1520",
        "0x152F",
    ],
    Family.SPVL.name: [
        "0x1533",
        "0x1534",
        "0x1536",
        "0x1537",
        "0x1538",
        "0x1531",
        "0x157B",
        "0x157C",
    ],
    Family.FPK.name: [
        "0x0DDA",
        "0x374C",
        "0x37D0",
        "0x37D1",
        "0x37D2",
        "0x37D3",
        "0x37CC",
        "0x37CE",
        "0x37CF",
    ],
    Family.CPK.name: [
        "0xF0A5",
        "0xF0A6",
        "0x18E4",
        "0x18ED",
        "0x1890",
        "0x1891",
        "0x1892",
        "0x1897",
        "0x1898",
        "0x189A",
        "0x151D",
        "0x124C",
        "0x124D",
        "0x188A",
        "0x188B",
        "0x188C",
        "0x579C",
        "0x579D",
        "0x579E",
        "0x579F",
        "0x0DBD",
    ],
    Family.CPK_SMBM.name: [
        "0x188F",
        "0x1895",
        "0x0DCD",
    ],
    Family.CVL.name: [
        "0x1590",
        "0x1591",
        "0x1592",
        "0x1593",
        "0x1599",
        "0x159B",
    ],
    Family.CNV.name: [
        "0x12D0",
        "0x12D1",
        "0x12D2",
        "0x12D3",
        "0x12D4",
        "0x12D9",
        "0xF0A8",
    ],
    Family.GNRD.name: [
        "0x579C",
        "0x579D",
    ],
    Family.MEV.name: MEV_IDs,
    Family.NNTQ.name: ["0x1558"],
    Family.HVL.name: [
        "0x15C2",
        "0x15C3",
        "0x15C4",
        "0x15C6",
        "0x15C7",
        "0x15C8",
        "0x15CA",
        "0x15CC",
        "0x15CE",
        "0x15E4",
        "0x15E5",
    ],
    Family.MPK.name: [
        "0x15A7",
        "0x15AA",
        "0x15AB",
        "0x15AC",
        "0x15AD",
        "0x15AE",
    ],
    Family.HTWL.name: ["0x10D3", "0x10F6"],
    Family.I350.name: ["0x1521", "0x1522", "0x1523", "0x1524"],
    Family.I225.name: ["0x15F2", "0x15F3"],
    Family.I710.name: ["0x0DD2"],
    Family.RRC.name: ["0x15A4"],
    Family.VF.name: [
        "0x10ED",
        "0x152E",
        "0x1515",
        "0x1530",
        "0x1564",
        "0x1565",
        "0x15C5",
        "0x15B4",
        "0x15A8",
        "0x15A9",
        "0x154C",
        "0x1571",
        "0x374D",
        "0x37CD",
        "0x3759",
        "0x37D9",
        "0xF0A3",
        "0xF0A4",
        "0x1889",
        "0x0DD5",
    ],
    Speed.VF_G1.value: ["0x10CA", "0x1520"],
    Speed.VF_G10.value: [
        "0x10ED",
        "0x1515",
        "0x1530",
        "0x1564",
        "0x1565",
        "0x152E",
        "0x15A8",
        "0x15C5",
        "0x15A9",
        "0x15B4",
        "0x57AD",
    ],
    Speed.VF_G40.value: [
        "0x154C",
        "0x1571",
        "0x374D",
        "0x3759",
        "0x37CD",
        "0x37D9",
        "0xF0A3",
        "0xF0A4",
        "0xF0FB",
        "0xFAFB",
        "0x1889",
    ],
    Speed.VF_G100.value: ["0x1889", "0x0DD5"],
    "8254X": ["0x100F"],
    "8256X": [
        "0x1049",
        "0x104A",
        "0x104B",
        "0x104D",
        "0x10BD",
        "0x294C",
        "0x10BF",
        "0x10CB",
        "0x10CC",
        "0x10CD",
        "0x10CE",
        "0x10DE",
        "0x10DF",
        "0x10E5",
        "0x10F5",
        "0x1501",
        "0x1525",
    ],
    "8257X": [
        "0x105E",
        "0x105F",
        "0x1060",
        "0x10A0",
        "0x10A1",
        "0x10A4",
        "0x10A5",
        "0x10BC",
        "0x10D5",
        "0x10D9",
        "0x10DA",
        "0x107D",
        "0x107E",
        "0x107F",
        "0x10B9",
        "0x108B",
        "0x108C",
        "0x108E",
        "0x109A",
        "0x10B0",
        "0x10B2",
        "0x10B3",
        "0x10B4",
        "0x10D3",
        "0x10D4",
        "0x10F6",
        "0x10EA",
        "0x10EB",
        "0x10EF",
        "0x10F0",
        "0x1502",
        "0x1503",
        "0x10A7",
        "0x10A9",
        "0x10D6",
        "0x10E2",
        "0x10C9",
        "0x10E6",
        "0x10E7",
        "0x10E8",
        "0x150A",
        "0x150D",
        "0x1518",
        "0x1526",
    ],
    "82580": [
        "0x150E",
        "0x150F",
        "0x1510",
        "0x1511",
        "0x1516",
        "0x1527",
    ],
}

SPEED_IDS = {
    Speed.G1.value: DEVICE_IDS[Family.PVL.name]
    + DEVICE_IDS["8256X"]
    + DEVICE_IDS["8257X"]
    + DEVICE_IDS["82580"]
    + DEVICE_IDS[Family.SPVL.name]
    + DEVICE_IDS[Family.I350.name]
    + DEVICE_IDS[Family.AVOTON.name]
    + DEVICE_IDS[Speed.VF_G1.value],
    Speed.G2.value: DEVICE_IDS[Family.I225.name],
    Speed.G10.value: DEVICE_IDS[Family.NNT.name]
    + DEVICE_IDS[Family.TVL.name]
    + DEVICE_IDS[Family.SGVL.name]
    + DEVICE_IDS[Family.HVL.name]
    + DEVICE_IDS[Family.MPK.name]
    + DEVICE_IDS[Family.NNTQ.name]
    + DEVICE_IDS[Family.LKV.name]
    + DEVICE_IDS[Speed.VF_G10.value],
    Speed.G40.value: DEVICE_IDS[Family.FVL.name]
    + DEVICE_IDS[Family.FPK.name]
    + DEVICE_IDS[Family.RRC.name]
    + DEVICE_IDS[Family.I710.name]
    + DEVICE_IDS[Speed.VF_G40.value],
    Speed.G100.value: DEVICE_IDS[Family.CPK.name]
    + DEVICE_IDS[Family.CVL.name]
    + DEVICE_IDS[Family.CNV.name]
    + DEVICE_IDS[Speed.VF_G100.value],
    Speed.G200.value: DEVICE_IDS[Family.MEV.name] + DEVICE_IDS[Family.GNRD.name],
}

FREEBSD_ADVERTISE_SPEED = {
    "10Mb": {"ice": 0x1, "ix": 0x8},
    "100Mb": {"ice": 0x2, "ixl": 0x1, "ix": 0x1},
    "1G": {"ice": 0x4, "ixl": 0x2, "ix": 0x2},
    "2.5G": {"ice": 0x8, "ixl": 0x40, "ix": 0x10},
    "5G": {"ice": 0x10, "ixl": 0x80, "ix": 0x20},
    "10G": {"ice": 0x20, "ixl": 0x4, "ix": 0x4},
    "20G": {"ice": 0x40, "ixl": 0x8},
    "25G": {"ice": 0x80, "ixl": 0x10},
    "40G": {"ice": 0x100, "ixl": 0x20},
    "50G": {"ice": 0x200},
    "100G": {"ice": 0x400},
    "Unknown": {"ice": 0x8000},
}

DEVID_CLASS_MAP_NICINSTALLER = {
    "1G_E1000": (
        "82566",
        "82567",
        "82571",
        "82572",
        "82573",
        "82574",
        "82577",
        "82578",
        "82579",
        DeviceID(0x100F),
    ),
    "1G": (
        "82575",
        "82576",
        "82580",
        "I350",
        DeviceID(0x1521),
        DeviceID(0x11BC),
        DeviceID(0x1533),
        DeviceID(0x1F41),
    ),
    "1G_VF": (DeviceID(0x152F), DeviceID(0x1520)),
    "2G": (DeviceID(0x15F2), DeviceID(0x15F3)),
    "10G": (
        DeviceID(0x10B6),
        DeviceID(0x10C6),
        DeviceID(0x10C7),
        DeviceID(0x10C8),
        DeviceID(0x10D8),
        DeviceID(0x10DB),
        DeviceID(0x10DD),
        DeviceID(0x10E1),
        DeviceID(0x10EC),
        DeviceID(0x10F1),
        DeviceID(0x10F4),
        DeviceID(0x10F7),
        DeviceID(0x10F8),
        DeviceID(0x10F9),
        DeviceID(0x10FA),
        DeviceID(0x10FB),
        DeviceID(0x10FC),
        DeviceID(0x1306),
        DeviceID(0x1307),
        DeviceID(0x1507),
        DeviceID(0x1508),
        DeviceID(0x150B),
        DeviceID(0x1512),
        DeviceID(0x1514),
        DeviceID(0x1517),
        DeviceID(0x151C),
        DeviceID(0x152A),
        DeviceID(0x1529),
        DeviceID(0x154A),
        DeviceID(0x154D),
        DeviceID(0x1557),
        DeviceID(0x1558),
        DeviceID(0x154F),
        DeviceID(0x155D),
        DeviceID(0x1528),
        DeviceID(0x155C),
        DeviceID(0x1560),
        DeviceID(0x1562),
        DeviceID(0x1563),
        DeviceID(0x15A7),
        DeviceID(0x15AA),
        DeviceID(0x15AB),
        DeviceID(0x15AC),
        DeviceID(0x15AD),
        DeviceID(0x15AE),
        DeviceID(0x15C2),
        DeviceID(0x15C3),
        DeviceID(0x15C4),
        DeviceID(0x15C6),
        DeviceID(0x15C7),
        DeviceID(0x15C8),
        DeviceID(0x15CA),
        DeviceID(0x15CC),
        DeviceID(0x15CE),
        DeviceID(0x15D1),
        DeviceID(0x15E4),
        DeviceID(0x15E5),
        DeviceID(0xF0C2),
        DeviceID(0xF0C4),
        DeviceID(0xF0C6),
        DeviceID(0xF0C7),
        DeviceID(0xF0C9),
        DeviceID(0x57AF),
        DeviceID(0x57B0),
        DeviceID(0x57B1),
    ),
    "10G_VF": (
        DeviceID(0x10ED),
        DeviceID(0x1515),
        DeviceID(0x152E),
        DeviceID(0x1530),
        DeviceID(0x1564),
        DeviceID(0x1565),
        DeviceID(0x15A8),
        DeviceID(0x15A9),
        DeviceID(0x15B4),
        DeviceID(0x15C5),
        DeviceID(0x57AD),
    ),
    "40G": (
        DeviceID(0x0DD2),
        DeviceID(0x0DDA),
        DeviceID(0x1572),
        DeviceID(0x1573),
        DeviceID(0x1574),
        DeviceID(0x1580),
        DeviceID(0x1581),
        DeviceID(0x1582),
        DeviceID(0x1583),
        DeviceID(0x1584),
        DeviceID(0x1585),
        DeviceID(0x1586),
        DeviceID(0x1587),
        DeviceID(0x1588),
        DeviceID(0x1589),
        DeviceID(0x158A),
        DeviceID(0x158B),
        DeviceID(0x374C),
        DeviceID(0x37CC),
        DeviceID(0x37CE),
        DeviceID(0x37CF),
        DeviceID(0x37D0),
        DeviceID(0x37D1),
        DeviceID(0x37D2),
        DeviceID(0x37D3),
        DeviceID(0xF0A2),
        DeviceID(0xFAFA),
        DeviceID(0x154B),
        DeviceID(0x15FF),
    ),
    "40G_VF": (
        DeviceID(0x154C),
        DeviceID(0x1571),
        DeviceID(0x3759),
        DeviceID(0x374D),
        DeviceID(0x37CD),
        DeviceID(0x37D9),
        DeviceID(0xF0A3),
        DeviceID(0xF0A4),
        DeviceID(0xFAFB),
    ),
    "100G": (
        DeviceID(0x12D0),
        DeviceID(0x12D1),
        DeviceID(0x12D2),
        DeviceID(0x12D3),
        DeviceID(0x12D4),
        DeviceID(0x12D9),
        DeviceID(0x1590),
        DeviceID(0x1591),
        DeviceID(0x1592),
        DeviceID(0x1593),
        DeviceID(0x1599),
        DeviceID(0x159B),
        DeviceID(0x18E4),
        DeviceID(0x18ED),
        DeviceID(0x1891),
        DeviceID(0x1892),
        DeviceID(0xF0A5),
        DeviceID(0xF0A6),
        DeviceID(0xF0A8),
    ),
    "100G_CPK": (
        DeviceID(0xF0A5),
        DeviceID(0xF0A6),
        DeviceID(0x18E4),
        DeviceID(0x18ED),
        DeviceID(0x1890),
        DeviceID(0x1891),
        DeviceID(0x1892),
        DeviceID(0x1897),
        DeviceID(0x1898),
        DeviceID(0x189A),
        DeviceID(0x151D),
        DeviceID(0x124C),
        DeviceID(0x124D),
        DeviceID(0x188A),
        DeviceID(0x188B),
        DeviceID(0x188C),
        DeviceID(0x579C),
        DeviceID(0x579D),
        DeviceID(0x579E),
        DeviceID(0x579F),
    ),
    "100G_CPK_SMBM": (DeviceID(0x188F), DeviceID(0x1895), DeviceID(0x0DCD)),
    "100G_VF": (DeviceID(0x18ED), DeviceID(0x1889), DeviceID(0x0DBD)),
    "200G": (DeviceID(0xF002), DeviceID(0xF00C), DeviceID(0x1452), DeviceID(0x579C), DeviceID(0x579D)),
}

DRIVER_DIRECTORY_MAP = {
    "e1000e": "PRO1000",
    "e2f": "PRO2500",
    "em": "PRO1000",
    "fm10k": "PRO40GB",
    "i40e": "PRO40GB",
    "iavf": "PROAVF",
    "ice": "PROCGB",
    "ice_sw": "PROCGB",
    "ice_swx": "PROCGB",
    "idpf": "PROCCGB",
    "igb": "PRO1000",
    "igbvf": "PRO1000",
    "igc": "PRO2500",
    "ix": "PROXGB",
    "ixgbe": "PROXGB",
    "ixgbevf": "PROXGB",
    "ixl": "PRO40GB",
    "ixv": "PROXGB",
    "scea": "PROCCGB",
    "sceb": "PROCCGB",
    "v1q": "PRO1000",
    "vx": "PROXGB",
}

DRIVER_DEVICE_ID_MAP = {
    "e1000e": {
        DeviceID(0x1049),
        DeviceID(0x104A),
        DeviceID(0x104B),
        DeviceID(0x104D),
        DeviceID(0x10BD),
        DeviceID(0x294C),
        DeviceID(0x10BF),
        DeviceID(0x10CB),
        DeviceID(0x10CC),
        DeviceID(0x10CD),
        DeviceID(0x10CE),
        DeviceID(0x10DE),
        DeviceID(0x10DF),
        DeviceID(0x10E5),
        DeviceID(0x10F5),
        DeviceID(0x1501),
        DeviceID(0x1525),
        DeviceID(0x105E),
        DeviceID(0x105F),
        DeviceID(0x1060),
        DeviceID(0x10A0),
        DeviceID(0x10A1),
        DeviceID(0x10A4),
        DeviceID(0x10A5),
        DeviceID(0x10BC),
        DeviceID(0x10D5),
        DeviceID(0x10D9),
        DeviceID(0x10DA),
        DeviceID(0x107D),
        DeviceID(0x107E),
        DeviceID(0x107F),
        DeviceID(0x10B9),
        DeviceID(0x108B),
        DeviceID(0x108C),
        DeviceID(0x108E),
        DeviceID(0x109A),
        DeviceID(0x10B0),
        DeviceID(0x10B2),
        DeviceID(0x10B3),
        DeviceID(0x10B4),
        DeviceID(0x10D3),
        DeviceID(0x10D4),
        DeviceID(0x10F6),
        DeviceID(0x10EA),
        DeviceID(0x10EB),
        DeviceID(0x10EF),
        DeviceID(0x10F0),
        DeviceID(0x100F),
        DeviceID(0x1502),
        DeviceID(0x1503),
    },  # on BSD em
    "igb": {
        DeviceID(0x10A7),
        DeviceID(0x10A9),
        DeviceID(0x10D6),
        DeviceID(0x10E2),
        DeviceID(0x10C9),
        DeviceID(0x10E6),
        DeviceID(0x10E7),
        DeviceID(0x10E8),
        DeviceID(0x150A),
        DeviceID(0x150D),
        DeviceID(0x1518),
        DeviceID(0x1526),
        DeviceID(0x150E),
        DeviceID(0x150F),
        DeviceID(0x1510),
        DeviceID(0x1511),
        DeviceID(0x1516),
        DeviceID(0x1527),
        DeviceID(0x1521),
        DeviceID(0x1522),
        DeviceID(0x1523),
        DeviceID(0x1524),
        DeviceID(0x11BC),
        DeviceID(0x1533),
        DeviceID(0x1F41),
    },
    "igbvf": {DeviceID(0x10CA), DeviceID(0x1520), DeviceID(0x152F)},  # on Windows v1q
    "igc": {DeviceID(0x15F2), DeviceID(0x15F3)},  # on Windows e2f
    "ixgbe": {
        DeviceID(0x10B6),
        DeviceID(0x10C6),
        DeviceID(0x10C7),
        DeviceID(0x10C8),
        DeviceID(0x10D8),
        DeviceID(0x10DB),
        DeviceID(0x10DD),
        DeviceID(0x10E1),
        DeviceID(0x10EC),
        DeviceID(0x10F1),
        DeviceID(0x10F4),
        DeviceID(0x10F7),
        DeviceID(0x10F8),
        DeviceID(0x10F9),
        DeviceID(0x10FA),
        DeviceID(0x10FB),
        DeviceID(0x10FC),
        DeviceID(0x1306),
        DeviceID(0x1307),
        DeviceID(0x1507),
        DeviceID(0x1508),
        DeviceID(0x150B),
        DeviceID(0x1512),
        DeviceID(0x1514),
        DeviceID(0x1517),
        DeviceID(0x151C),
        DeviceID(0x1528),
        DeviceID(0x1529),
        DeviceID(0x152A),
        DeviceID(0x154A),
        DeviceID(0x154D),
        DeviceID(0x154F),
        DeviceID(0x1557),
        DeviceID(0x1558),
        DeviceID(0x155C),
        DeviceID(0x155D),
        DeviceID(0x1560),
        DeviceID(0x1562),
        DeviceID(0x1563),
        DeviceID(0x15A7),
        DeviceID(0x15AA),
        DeviceID(0x15AB),
        DeviceID(0x15AC),
        DeviceID(0x15AD),
        DeviceID(0x15AE),
        DeviceID(0x15C2),
        DeviceID(0x15C3),
        DeviceID(0x15C4),
        DeviceID(0x15C6),
        DeviceID(0x15C7),
        DeviceID(0x15C8),
        DeviceID(0x15CA),
        DeviceID(0x15CC),
        DeviceID(0x15CE),
        DeviceID(0x15D1),
        DeviceID(0x15E4),
        DeviceID(0x15E5),
        DeviceID(0x57AF),
        DeviceID(0x57B0),
        DeviceID(0x57B1),
        DeviceID(0xF0C2),
        DeviceID(0xF0C4),
        DeviceID(0xF0C6),
        DeviceID(0xF0C7),
        DeviceID(0xF0C9),
    },  # on BSD ix, on Windows ix
    "ixgbevf": {
        DeviceID(0x10ED),
        DeviceID(0x1515),
        DeviceID(0x152E),
        DeviceID(0x1530),
        DeviceID(0x1564),
        DeviceID(0x1565),
        DeviceID(0x15A8),
        DeviceID(0x15A9),
        DeviceID(0x15B4),
        DeviceID(0x15C5),
        DeviceID(0x57AD),
    },  # on BSD ixv, on Windows vx
    "i40e": {
        DeviceID(0x0DD2),
        DeviceID(0x0DDA),
        DeviceID(0x154B),
        DeviceID(0x1572),
        DeviceID(0x1573),
        DeviceID(0x1574),
        DeviceID(0x1580),
        DeviceID(0x1581),
        DeviceID(0x1582),
        DeviceID(0x1583),
        DeviceID(0x1584),
        DeviceID(0x1585),
        DeviceID(0x1586),
        DeviceID(0x1587),
        DeviceID(0x1588),
        DeviceID(0x1589),
        DeviceID(0x158A),
        DeviceID(0x158B),
        DeviceID(0x15FF),
        DeviceID(0x374C),
        DeviceID(0x37CC),
        DeviceID(0x37CE),
        DeviceID(0x37CF),
        DeviceID(0x37D0),
        DeviceID(0x37D1),
        DeviceID(0x37D2),
        DeviceID(0x37D3),
        DeviceID(0xF0A2),
        DeviceID(0xFAFA),
    },  # on BSD ixl
    "fm10k": {DeviceID(0x15A4)},
    "ice_sw": {
        DeviceID(0x18ED),
    },
    "ice_swx": {
        DeviceID(0x188F),
        DeviceID(0x1895),
        DeviceID(0x0DCD),
    },
    "ice": {
        DeviceID(0x124C),
        DeviceID(0x124D),
        DeviceID(0x124E),
        DeviceID(0x124F),
        DeviceID(0x12D0),
        DeviceID(0x12D1),
        DeviceID(0x12D2),
        DeviceID(0x12D3),
        DeviceID(0x12D4),
        DeviceID(0x12D9),
        DeviceID(0x151D),
        DeviceID(0x1590),
        DeviceID(0x1591),
        DeviceID(0x1592),
        DeviceID(0x1593),
        DeviceID(0x1599),
        DeviceID(0x159B),
        DeviceID(0x188A),
        DeviceID(0x188B),
        DeviceID(0x188C),
        DeviceID(0x188D),
        DeviceID(0x188E),
        DeviceID(0x1890),
        DeviceID(0x1891),
        DeviceID(0x1892),
        DeviceID(0x1893),
        DeviceID(0x1894),
        DeviceID(0x1897),
        DeviceID(0x1898),
        DeviceID(0x1899),
        DeviceID(0x189A),
        DeviceID(0x18E4),
        DeviceID(0x18ED),
        DeviceID(0x579C),
        DeviceID(0x579D),
        DeviceID(0x579E),
        DeviceID(0x579F),
        DeviceID(0xF0A5),
        DeviceID(0xF0A6),
        DeviceID(0xF0A8),
    },  # CPK part on Windows scea
    "idpf": {DeviceID(0xF002), DeviceID(0xF00C), DeviceID(0x1452), DeviceID(0x145C)},
    "iavf": {
        DeviceID(0x154C),
        DeviceID(0x1571),
        DeviceID(0x374D),
        DeviceID(0x3759),
        DeviceID(0x37CD),
        DeviceID(0x37D9),
        DeviceID(0xF0A3),
        DeviceID(0xF0A4),
        DeviceID(0xF0FB),
        DeviceID(0x1889),
    },
}

WINDOWS_DRIVER_DEVICE_ID_MAP = {
    "scea": {
        DeviceID(0x124C),
        DeviceID(0x124D),
        DeviceID(0x151D),
        DeviceID(0x188A),
        DeviceID(0x188B),
        DeviceID(0x188C),
        DeviceID(0x1890),
        DeviceID(0x1891),
        DeviceID(0x1892),
        DeviceID(0x1897),
        DeviceID(0x1898),
        DeviceID(0x189A),
        DeviceID(0x18E4),
        DeviceID(0x18ED),
        DeviceID(0x579C),
        DeviceID(0x579D),
        DeviceID(0x579E),
        DeviceID(0x579F),
        DeviceID(0xF0A5),
        DeviceID(0xF0A6),
    },
    "sceb": {
        DeviceID(0x579C),
        DeviceID(0x579D),
    },
}

MANAGEMENT_NETWORK = [
    IPv4Network("10.166.28.0/23"),
    IPv4Network("10.102.0.0/16"),
    IPv4Network("10.12.0.0/16"),
    IPv4Network("172.31.0.0/16"),
]


class FreeBSDDriverNames(Enum):
    """FreeBSD Driver Name Enum."""

    IXV = "ixv"
    IGB = "igb"
    IX = "ix"
    IXL = "ixl"
    IAVF = "iavf"
    ICE = "ice"


DESIGNED_NUMBER_VFS_BY_SPEED = {
    Speed.G1: 28,
    Speed.G10: 126,
    Speed.G40: 128,
    Speed.G100: 256,
    Speed.G200: 1024,
}

# Supported Reset types
SUPPORTED_ADAPTER_RESET_TYPES = {"global": "GLOBR", "core": "CORER", "pf": "PFR"}
