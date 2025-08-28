from ctypes import *

class DevInfoMap(Structure):
    _fields_ = [
        ("DevLogicID", c_uint32),
        ("DeviceNumber", c_uint32),
        ("DeviceHandle", c_int64),
        ("DeviceName", c_char*48),
    ]

class RingNoInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class DiGenInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("PhysicPortID", c_uint32),
        ("LogicPortID", c_uint32),
        ("SubDeviceID", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class DoGenInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("PhysicPortID", c_uint32),
        ("LogicPortID", c_uint32),
        ("SubDeviceID", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class AiGenInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("PhysicChannelID", c_uint32),
        ("LogicChannelID", c_uint32),
        ("SubDeviceID", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class AoGenInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("PhysicChannelID", c_uint32),
        ("LogicChannelID", c_uint32),
        ("SubDeviceID", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class CntGenInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("PhysicChannelID", c_uint32),
        ("LogicChannelID", c_uint32),
        ("SubDeviceID", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class MPGInfoMap(Structure):
    _fields_ = [
        ("PhysicRingNo", c_uint32),
        ("LogicRingNo", c_uint32),
        ("PhysicChannelID", c_uint32),
        ("LogicChannelID", c_uint32),
        ("SubDeviceID", c_uint32),
        ("DeviceInfo", DevInfoMap),
    ]

class DEVICEINFO(Structure):
    _fields_ = [
        ("AxisCnt", c_uint32),
        ("GroupCnt", c_uint32),
        ("DIEXCnt", c_uint32),
        ("DOEXCnt", c_uint32),
        ("RingCnt", c_uint32),
        ("DIGenPortCnt", c_uint32),
        ("DOGenPortCnt", c_uint32),
        ("AIGenChannelCnt", c_uint32),
        ("AOGenChannelCnt", c_uint32),
        ("CounterChannelCnt", c_uint32),
        ("MDAQCHCnt", c_uint32),
        ("MPGChannelCnt", c_uint32),
        ("DeviceName", c_char*48),
        ("DevNumber", c_uint32),
        ("DeviceHandle", c_uint64),
        ("AxisHandle", POINTER(c_uint64)),
        ("GroupHandle", POINTER(c_uint64)),
        ("LatchCHHandle", POINTER(c_uint64)),
        ("RingInfo", POINTER(RingNoInfoMap)),
        ("GenDIInfo", POINTER(DiGenInfoMap)),
        ("GenDOInfo", POINTER(DoGenInfoMap)),
        ("GenAIInfo", POINTER(AiGenInfoMap)),
        ("GenAOInfo", POINTER(AoGenInfoMap)),
        ("GenCounterInfo", POINTER(CntGenInfoMap)),
        ("MPGInfo", POINTER(MPGInfoMap)),
    ]

class DEV_PRE_SCAN_DATA(Structure):
    # _pack_ = 1
    _fields_ = [
        ("XScanData", c_double),
        ("YScanData", c_double),
        ("ZScanData", c_double)
    ]