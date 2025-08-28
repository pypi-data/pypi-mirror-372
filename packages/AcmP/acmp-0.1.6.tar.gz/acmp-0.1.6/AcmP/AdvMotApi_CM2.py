from ctypes import *

CALLBACK_FUNC = CFUNCTYPE(c_uint32, c_uint32, c_void_p)

class DEVLIST(Structure):
    # _pack_ = 1
    _fields_ = [
        ("dwDeviceNum", c_uint32),
        ("szDeviceName", c_char*50),
        ("nNumOfSubdevices", c_int16)
    ]

class ADVAPI_MDEVICE_INFO(Structure):
    # _pack_ = 1
    _fields_ = [
        ('totalTxLen', c_uint32),
        ('totalRxLen', c_uint32),
        ('cyclicTimeNS', c_uint32),
        ('slave_count', c_uint32),
        ('link_up', c_uint32),
        ('phase', c_uint8),
        ('active', c_uint8),
        ('scan_busy', c_uint8),
        ('ring_type', c_uint8),
        ('num_devices', c_uint32),
        ('tx_count', c_uint64),
        ('rx_count', c_uint64),
        ('tx_bytes', c_uint64),
        ('rx_bytes', c_uint64),
        ('dc_ref_time', c_uint64),
        ('app_time', c_uint64),
        ('ref_clock', c_uint16),
        ('reserved2', c_uint16)
    ]

class DEV_IO_MAP_INFO(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Name', c_char*50),
        ('Index', c_uint32),
        ('Offset', c_uint32),
        ('ByteLength', c_uint32),
        ('SlotID', c_uint32),
        ('PortChanID', c_uint32),
        ('ModuleID', c_uint32),
        ('ModuleName', c_char*16),
        ('Description', c_char*100),
    ]

class LINK_PORT_INFO(Structure):
    # _pack_ = 1
    _fields_ = [
        ('desc', c_uint32),
        ('link_up', c_ubyte),
        ('loop_closed', c_ubyte),
        ('signal_detected', c_ubyte),
        ('receive_time', c_uint32),
        ('next_slave', c_uint16),
        ('delay_to_next_dc', c_uint32)
    ]

class ADVAPI_SUBDEVICE_INFO_CM2(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Position', c_uint16),
        ('VendorID', c_uint32),
        ('ProductID', c_uint32),
        ('RevisionNo', c_uint32),
        ('SerialNo', c_uint32),
        ('SubDeviceID', c_uint16),
        ('current_on_ebus', c_int16),
        ('ports', LINK_PORT_INFO*4),
        ('al_state', c_ubyte),
        ('error_flag', c_ubyte),
        ('sync_count', c_ubyte),
        ('Reserved', c_ubyte),
        ('transmission_delay', c_uint32),
        ('dc_configure', c_uint16),
        ('DeviceName', c_char*64)
    ]

ADV_USER_CALLBACK_FUNC = CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def ADVUSERCALLBACKFUNC(EvtValue, UserParameter):
    pass
PADV_USER_CALLBACK_FUNC = ADV_USER_CALLBACK_FUNC(ADVUSERCALLBACKFUNC)

class PHASE_AXIS_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Acc', c_double),
        ('Dec', c_double),
        ('PhaseVel', c_double),
        ('PhaseDistance', c_double)
    ]

class SPEED_PROFILE_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('FH', c_double),
        ('FL', c_double),
        ('Acc', c_double),
        ('Dec', c_double),
        ('JerkFac', c_double)
    ]

class MOTION_IO(Structure):
    # _pack_ = 1
    _fields_ = [
        ('RDY', c_uint8),
        ('ALM', c_uint8),
        ('LMT_P', c_uint8),
        ('LMT_N', c_uint8),
        ('ORG', c_uint8),
        ('DIR', c_uint8),
        ('EMG', c_uint8),
        ('PCS', c_uint8),
        ('ERC', c_uint8),
        ('EZ', c_uint8),
        ('CLR', c_uint8),
        ('LTC', c_uint8),
        ('SD', c_uint8),
        ('INP', c_uint8),
        ('SVON', c_uint8),
        ('ALRM', c_uint8),
        ('SLMT_P', c_uint8),
        ('SLMT_N', c_uint8),
        ('CMP', c_uint8),
        ('CAMDO', c_uint8),
        ('RESETREADY', c_uint8)
    ]

class PATH_STATUS(Structure):
    # _pack_ = 1
    _fields_ = [
        ('CurIndex', c_uint32),
        ('CurCmdFunc', c_uint32),
        ('RemainCount', c_uint32),
        ('FreeSpaceCount', c_uint32)
    ]

class CAM_IN_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('PrimaryOffset', c_double),
        ('FollowingOffset', c_double),
        ('PrimaryScaling', c_double),
        ('FollowingScaling', c_double),
        ('CamTableID', c_uint32),
        ('RefSrc', c_uint32)
    ]

class GEAR_RATIO_RATE(Structure):
    _pack_ = 1
    _fields_ = [
        ('Num', c_double),
        ('Den', c_double)
    ]

class GEAR_IN_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('RefSrc', c_uint32),
        ('GearRatioRate', GEAR_RATIO_RATE),
        ('Mode', c_uint32),
        ('GearPosition', c_double)
    ]

class TANGENT_IN_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('StartVectorArray', c_int32*3),
        ('Working_plane', c_uint32),
        ('Direction', c_uint)
    ]

class GANTRY_IN_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('RefSrc', c_int16),
        ('Direction', c_int16),
    ]

class BUFFER_STATUS(Structure):
    # _pack_ = 1
    _fields_ = [
        ('CurIndex', c_uint32),
        ('RemainCount', c_uint32),
        ('FreeSpaceCount', c_uint32)
    ]

class JOG_SPEED_PROFILE_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('FH', c_double),
        ('FL', c_double),
        ('Acc', c_double),
        ('Dec', c_double),
        ('VLTime', c_double)
    ]

class PATH_DO_MODE0(Structure):
    # _pack_ = 1
    _fields_ = [
        ('DOPort', c_uint32),
        ('DOEnable', c_uint32),
        ('DOValue', c_uint32)
    ]

class PATH_DO_MODE1(Structure):
    # _pack_ = 1
    _fields_ = [
        ('SubDeviceID', c_uint32),
        ('DOPort', c_uint32),
        ('DOEnable', c_uint32),
        ('DOValue', c_uint32)
    ]

class PATH_DO_MODE2(Structure):
    # _pack_ = 1
    _fields_ = [
        ('AxID', c_uint32),
        ('DOEnable', c_uint32),
        ('DOValue', c_uint32)
    ]

class PATH_DO_MODE(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Mode0', PATH_DO_MODE0),
        ('Mode1', PATH_DO_MODE1),
        ('Mode2', PATH_DO_MODE2)
    ]

class PATH_DO_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('MoveMode', c_uint32),
        ('PathDO_Prm', PATH_DO_MODE),
        ('DO_Output_Time', c_double)
    ]

class PATH_DI_WAIT_MODE0(Structure):
    # _pack_ = 1
    _fields_ = [
        ('DIPort', c_uint32),
        ('DIEnable', c_uint32),
        ('DIValue', c_uint32)
    ]

class PATH_DI_WAIT_MODE1(Structure):
    # _pack_ = 1
    _fields_ = [
        ('SubDeviceID', c_uint32),
        ('DIPort', c_uint32),
        ('DIEnable', c_uint32),
        ('DIValue', c_uint32)
    ]

class PATH_DI_WAIT_MODE2(Structure):
    # _pack_ = 1
    _fields_ = [
        ('AxID', c_uint32),
        ('DIEnable', c_uint32),
        ('DIValue', c_uint32)
    ]

class PATH_DI_WAIT_MODE(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Mode0', PATH_DI_WAIT_MODE0),
        ('Mode1', PATH_DI_WAIT_MODE1),
        ('Mode2', PATH_DI_WAIT_MODE2)
    ]

class PATH_DI_WAIT_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('MoveMode', c_uint32),
        ('PathDI_Prm', PATH_DI_WAIT_MODE),
        ('DI_Wait_Time', c_double),
    ]

class PATH_AX_WAIT_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('AxID', c_uint32),
        ('CmpMethod', c_uint32),
        ('CmpValue', c_double),
        ('ValueRange', c_double),
        ('CmpSrc', c_uint),
        ('Timeout', c_double),
    ]

class PWM_TABLE_STATUS(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Velocity', c_uint32),
        ('PWMValue', c_uint32)
    ]

class OSC_PROFILE_PRM(Structure):
    # _pack_ = 1
    _fields_ = [
        ('Enable', c_uint32),
        ('Period', c_uint32),
        ('AxidNo', c_uint32),
        ('ChanType', c_uint32),
        ('ChanProperty', c_uint32),
        ('TrigMode', c_uint32),
        ('TimeWidth', c_uint32)
    ]

class ADVAPI_IO_LINK_INFO(Structure):
    _fields_ = [
        ('DeviceName', c_char*48),
        ('SubDeviceID', c_uint32),
        ('Position', c_uint32),
        ('VendorID', c_uint32),
        ('ProductID', c_uint32),
        ('SubDeviceName', c_char*64),
        ('PhysicRingNo', c_uint32),
        ('PortType', c_int),
        ('PhysicNo', c_uint32),
        ('EntryName', c_char*64),
        ('EntryIndex', c_uint32),
        ('EntrySubIndex', c_uint32),
        ('BitLength', c_uint32)
    ]



