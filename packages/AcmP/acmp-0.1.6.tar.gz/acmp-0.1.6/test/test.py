from ctypes import *
from AcmP.AdvCmnAPI_CM2 import AdvCmnAPI_CM2 as AdvMot
from AcmP.AdvMotApi_CM2 import DEVLIST
from AcmP.MotionInfo import DEVICEINFO
from AcmP.AdvMotDrv import POSITION_TYPE, ABS_MODE, AXIS_STATUS_TYPE
from AcmP.AdvMotPropID_CM2 import PropertyID2
# ---
# number_hex = '0x63000000'
# number_int = int(number_hex, 16)
# device_number = c_uint32(number_int)
# dev_list = (DEVLIST*10)()
# device_info = DEVICEINFO()
# out_ent = c_uint32(0)
# errCde = c_uint32(0)
# # Get Available
# errCde = AdvMot.Acm2_GetAvailableDevs(dev_list, 10, byref(out_ent))
# # Then open
# errCde = AdvMot.Acm2_DevOpen(device_number, byref(device_info))
# # Close device
# errCde = AdvMot.Acm2_DevAllClose()
# ---
# dev_list = (DEVLIST*10)()
# out_ent = c_uint32(0)
# errCde = c_uint32(0)
# # Get Available
# errCde = AdvMot.Acm2_GetAvailableDevs(dev_list, 10, byref(out_ent))
# # Initial device
# errCde = AdvMot.Acm2_DevInitialize()
# axid = c_uint32(0)
# pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
# pos = c_double(0)
# distance = c_double(1000)
# abs_mode = c_uint(ABS_MODE.MOVE_REL.value)
# state_type = c_uint(AXIS_STATUS_TYPE.AXIS_STATE.value)
# state = c_uint32(16)
# # Get axis 0 command position
# errCde = AdvMot.Acm2_AxGetPosition(axid, pos_type, byref(pos))
# # Move axis 0 to position 1000(command position)
# errCde = AdvMot.Acm2_AxPTP(axid, abs_mode, distance)
# # Check axis 0 status
# errCde = AdvMot.Acm2_AxGetState(axid, state_type, byref(state))
# ---
dev_list = (DEVLIST*10)()
out_ent = c_uint32(0)
errCde = c_uint32(0)
# Get Available
errCde = AdvMot.Acm2_GetAvailableDevs(dev_list, 10, byref(out_ent))
# Initial device
errCde = AdvMot.Acm2_DevInitialize()
do_ch = c_uint32(0)
property_id = c_uint(PropertyID2.CFG_CH_DaqDoFuncSelect.value)
val = c_double(1)
# Set local DO channel 0 as gerneral DO
errCde = AdvMot.Acm2_SetProperty(do_ch, property_id, val)
get_val = c_double(0)
# Get local DO channel 0 property value
errCde = AdvMot.Acm2_GetProperty(do_ch, property_id, byref(get_val))
# Set local DO channel 0 ON
data = c_uint32(1)
errCde = AdvMot.Acm2_ChSetDOBit(do_ch, data)
# Get local DO channel 0 value
get_data = c_uint32(0)
errCde = AdvMot.Acm2_ChGetDOBit(do_ch, byref(get_data))