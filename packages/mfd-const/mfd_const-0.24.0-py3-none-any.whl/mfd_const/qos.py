# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: MIT
"""Main module for QoS Consts."""

# for QoS mapping
LOCAL_ETS = "ETS"
LOCAL_PFC = "PFC"
LOCAL_APP = "APP"
REMOTE_ETS = "Remote_ETS"
REMOTE_PFC = "Remote_PFC"
REMOTE_APP = "Remote_APP"

# temporary path for copying tools from SUT/Controller to any host under test
DCB_TOOL_PATH_LNX = r"/tmp/tools/dcb"

# adapters features names
NIC_REGISTRY_BASE_PATH_DCB = r"HKLM:\SYSTEM\ControlSet001\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\%s"

LOCAL_DEFAULT_MAP = {
    LOCAL_ETS: {"0": {"TSA": "ETS", "Bandwidth": 100, "Priorities": [0, 1, 2, 3, 4, 5, 6, 7]}},
    LOCAL_PFC: [False, False, False, False, False, False, False, False],
}

LOCAL_ISCSI_MAP = {
    LOCAL_ETS: {
        "0": {"TSA": "ETS", "Bandwidth": 20, "Priorities": [0, 1, 2, 5, 6, 7]},
        "1": {"TSA": "ETS", "Bandwidth": 20, "Priorities": [3]},
        "2": {"TSA": "ETS", "Bandwidth": 60, "Priorities": [4]},
    },
    LOCAL_PFC: [False, False, False, True, True, False, False, False],
}

SAN_DCB_MAP = {
    LOCAL_ETS: {
        "0": {"TSA": "ETS", "Bandwidth": 40, "Priorities": [0, 1, 2, 5, 6, 7]},
        "1": {"TSA": "ETS", "Bandwidth": 30, "Priorities": [3]},
        "2": {"TSA": "ETS", "Bandwidth": 30, "Priorities": [4]},
    },
    LOCAL_PFC: [False, False, False, True, True, False, False, False],
    LOCAL_APP: {"3260": {"Priority": 4, "Protocol": "TCP"}},
}

ALT_SAN_DCB = {
    LOCAL_ETS: {
        "0": {"TSA": "ETS", "Bandwidth": 10, "Priorities": [0, 1, 2, 5, 6, 7]},
        "1": {"TSA": "ETS", "Bandwidth": 30, "Priorities": [3]},
        "2": {"TSA": "ETS", "Bandwidth": 60, "Priorities": [4]},
    },
    LOCAL_PFC: [False, False, False, True, True, False, False, False],
    LOCAL_APP: {"3260": {"Priority": 4, "Protocol": "TCP"}},
}

ISCSI_POLICY = {"UP4": {"Template": "iSCSI", "PriorityValue": "4"}}
