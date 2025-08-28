# This unit test is for common motion 2.0
import unittest
import time
import os
import numpy as np
import xml.etree.ElementTree as xml
import threading
from AcmP.AdvCmnAPI_CM2 import AdvCmnAPI_CM2
from AcmP.AdvMotApi_CM2 import *
from AcmP.AdvMotDrv import *
from AcmP.MotionInfo import *
from AcmP.AdvMotPropID_CM2 import PropertyID2
from AcmP.AdvMotErr_CM2 import ErrorCode2

# if os.name == 'nt':
#     from colorama import init as colorama_init, Fore
#     colorama_init(autoreset=True, wrap=True, convert=True)
# else:
#     from AcmP.utils import Color
ax_motion_cnt = c_uint32(0)
ax_evt_cnt = [c_uint32(0), c_uint32(0), c_uint32(0), c_uint32(0), c_uint32(0)]

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EvtAxMotionDone(axid, reservedParam):
    ax_motion_cnt.value = ax_motion_cnt.value + 1;
    print('[EvtAxMotionDone] AX:{0}, counter:{1}'.format(axid, ax_motion_cnt.value))
    return 0;

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EvtAxMotionDone_multi_0(axid, reservedParam):
    ax_evt_cnt[axid].value = ax_evt_cnt[axid].value + 1;
    print('[EvtAxMotionDone_multi 0] AX:{0}, counter:{1}'.format(axid, ax_evt_cnt[axid].value))
    return 0;

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EvtAxMotionDone_multi_1(axid, reservedParam):
    ax_evt_cnt[axid].value = ax_evt_cnt[axid].value + 1;
    print('[EvtAxMotionDone_multi 1] AX:{0}, counter:{1}'.format(axid, ax_evt_cnt[axid].value))
    return 0;

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EvtAxMotionDone_multi_2(axid, reservedParam):
    ax_evt_cnt[axid].value = ax_evt_cnt[axid].value + 1;
    print('[EvtAxMotionDone_multi 2] AX:{0}, counter:{1}'.format(axid, ax_evt_cnt[axid].value))
    return 0;

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EvtAxMotionDone_multi_3(axid, reservedParam):
    ax_evt_cnt[axid].value = ax_evt_cnt[axid].value + 1;
    print('[EvtAxMotionDone_multi 3] AX:{0}, counter:{1}'.format(axid, ax_evt_cnt[axid].value))
    return 0;

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EvtAxMotionDone_multi_4(axid, reservedParam):
    ax_evt_cnt[axid].value = ax_evt_cnt[axid].value + 1;
    print('[EvtAxMotionDone_multi 4] AX:{0}, counter:{1}'.format(axid, ax_evt_cnt[axid].value))
    return 0;

@CFUNCTYPE(c_uint32, c_uint32, c_void_p)
def EmptyFunction(val, res):
    return 0;

class AdvCmnAPI_Test(unittest.TestCase):
    def setUp(self):
        self.maxEnt = 10
        self.devlist = (DEVLIST*self.maxEnt)()
        self.outEnt = c_uint32(0)
        self.errCde = 0
        self.state = c_uint32(16)
        self.AdvMot = AdvCmnAPI_CM2
        self.gpid = c_uint32(0)
        gp_arr = [c_uint32(0), c_uint32(1)]
        self.axis_array = (c_uint32 * len(gp_arr))(*gp_arr)
    
    def tearDown(self):
        self.errCde = 0
    
    def test_GetAvailableDevs(self):
        # your switch number on board as device number
        # excepted_dev_hex = '0x63003000'
        excepted_err = 0
        # excepted_dev = int(excepted_dev_hex, 16)
        self.errCde = self.AdvMot.Acm2_GetAvailableDevs(self.devlist, self.maxEnt, byref(self.outEnt))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        for i in range(self.outEnt.value):
            print('Dev number:{0:x}'.format(self.devlist[i].dwDeviceNum))
        # result_dev = self.devlist[0].dwDeviceNum
        # self.assertEqual(excepted_dev, result_dev, '{0} failed.'.format(self._testMethodName))

    def test_Initialize(self):
        self.errCde = self.AdvMot.Acm2_DevInitialize()
        excepted_err = 0
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_DevClose(self):
        excepted_err = 0
        self.errCde = self.AdvMot.Acm2_DevAllClose()
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_LoadENI(self):
        ring_no = c_uint32(0)
        # eni file name has device number prefix
        if os.name == 'nt':
            eni_path = b'test\\eni0.xml'
        else:
            eni_path = b'test/eni0.xml'
        self.errCde = self.AdvMot.Acm2_DevLoadENI(ring_no, eni_path)
        excepted_err = 0
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_GetMDevice(self):
        ring_no = c_uint32(0)
        MDeviceInfo = ADVAPI_MDEVICE_INFO()
        self.errCde = self.AdvMot.Acm2_DevGetMDeviceInfo(ring_no, byref(MDeviceInfo))
        excepted_err = 0
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    # def test_DevExportMappingTable(self):
    #     # test0.xml will saved under current folder
    #     if os.name == 'nt':
    #         file_path = b'test\\test0.xml'
    #     else:
    #         file_path = b'test/test0.xml'
    #     self.errCde = self.AdvMot.Acm2_DevExportMappingTable(file_path)
    #     excepted_err = 0
    #     self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    # def test_DevImportMappingTable(self):
    #     if os.name == 'nt':
    #         file_path = b'test\\test0.xml'
    #     else:
    #         file_path = b'test/test0.xml'        
    #     self.errCde = self.AdvMot.Acm2_DevImportMappingTable(file_path)
    #     excepted_err = 0
    #     self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_AxPTP(self):
        ax_id = c_uint32(0)
        abs_mode = c_uint(ABS_MODE.MOVE_REL.value)
        distance = c_double(1000)
        self.errCde = self.AdvMot.Acm2_AxPTP(ax_id, abs_mode, distance)
        excepted_err = 0
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GetAxState(self):
        ax_id = c_uint32(0)
        state_type = c_uint(AXIS_STATUS_TYPE.AXIS_STATE.value)
        self.AdvMot.Acm2_AxGetState(ax_id, state_type, byref(self.state))
        if (self.state.value != AXIS_STATE.STA_AX_READY.value):
            print('Not Ready')
    
    def test_ResetAll(self):
        ax_id_arr = [c_uint32(0), c_uint32(1), c_uint32(2), c_uint32(3), c_uint32(4), c_uint32(5)]
        excepted_err = 0
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        pos = c_double(0)
        state_type = c_uint(AXIS_STATUS_TYPE.AXIS_STATE.value)
        ax_motion_cnt = c_uint32(0)
        ax_evt_cnt = [c_uint32(0), c_uint32(0), c_uint32(0), c_uint32(0), c_uint32(0)]
        # Check axis status
        for i in range(len(ax_id_arr)):
            state = c_uint32(16)
            self.AdvMot.Acm2_AxGetState(ax_id_arr[i], state_type, byref(state))
            while state.value != AXIS_STATE.STA_AX_READY.value:
                time.sleep(0.5) # sleep for 0.5 second
                self.AdvMot.Acm2_AxGetState(ax_id_arr[i], state_type, byref(state))
        # Clear all
        # self.errCde = self.AdvMot.Acm2_DevResetAllError()
        # self.assertEqual(excepted_err, self.errCde)
        # Set axis command position as 0
        for j in range(len(ax_id_arr)):
            self.errCde = self.AdvMot.Acm2_AxSetPosition(ax_id_arr[j], pos_type, pos)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_AxGetPosition(self):
        ax_id = c_uint32(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        pos = c_double(0)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        self.errCde = self.AdvMot.Acm2_AxGetPosition(ax_id, pos_type, byref(pos))
        excepted_pos = c_double(1000)
        excepted_err = 0
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(excepted_pos.value, pos.value, '{0} failed.'.format(self._testMethodName))

    def test_MoveContinue(self):
        excepted_err = 0
        ax_id = c_uint32(0)
        move_dir = c_uint(MOTION_DIRECTION.DIRECTION_POS.value)
        self.errCde = self.AdvMot.Acm2_AxMoveContinue(ax_id, move_dir)
        self.assertEqual(excepted_err, self.errCde)
        time.sleep(2)
        ax_arr = [c_uint32(0)]
        axArr = (c_uint32 * len(ax_arr))(*ax_arr)
        stop_mode = c_uint(MOTION_STOP_MODE.MOTION_STOP_MODE_DEC.value)
        new_dec = c_double(3000)
        self.errCde = self.AdvMot.Acm2_AxMotionStop(axArr, len(ax_arr), stop_mode, new_dec)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis position
        starting_pos = c_double(0)
        pos = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        self.errCde = self.AdvMot.Acm2_AxGetPosition(ax_id, pos_type, byref(pos))
        self.assertEqual(excepted_err, self.errCde)
        self.assertNotEqual(starting_pos.value, pos.value, '{0} failed.'.format(self._testMethodName))        

    def test_SetDeviceDIOProperty(self):
        do_ch = [c_uint32(0), c_uint32(1)]
        property_id = c_uint(PropertyID2.CFG_CH_DaqDoFuncSelect.value)
        val = c_double(1)
        excepted_err = 0
        for i in range(len(do_ch)):
            self.errCde = self.AdvMot.Acm2_SetProperty(do_ch[i], property_id, val)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_GetDeviceDIOProperty(self):
        do_ch = [c_uint32(0), c_uint32(1)]
        property_id = c_uint(PropertyID2.CFG_CH_DaqDoFuncSelect.value)
        val = c_double(1)
        get_val = c_double(0)
        excepted_err = 0
        for i in range(len(do_ch)):
            self.errCde = self.AdvMot.Acm2_GetProperty(do_ch[i], property_id, byref(get_val))
            self.assertEqual(excepted_err, self.errCde)
            self.assertEqual(val.value, get_val.value)
    
    def test_SetDeviceDO_ON(self):
        do_ch = [c_uint32(0), c_uint32(1)]
        data_on = c_uint32(DO_ONOFF.DO_ON.value)
        data_off = c_uint32(DO_ONOFF.DO_OFF.value)
        get_data = c_uint32(0)
        excepted_err = 0
        for i in range(len(do_ch)):
            self.errCde = self.AdvMot.Acm2_ChSetDOBit(do_ch[i], data_on)
            self.assertEqual(excepted_err, self.errCde)
            self.errCde = self.AdvMot.Acm2_ChGetDOBit(do_ch[i], byref(get_data))
            self.assertEqual(excepted_err, self.errCde)      
            self.assertEqual(data_on.value, get_data.value)
            self.errCde = self.AdvMot.Acm2_ChSetDOBit(do_ch[i], data_off)
            self.assertEqual(excepted_err, self.errCde)
            self.errCde = self.AdvMot.Acm2_ChGetDOBit(do_ch[i], byref(get_data))
            self.assertEqual(excepted_err, self.errCde) 
        self.assertEqual(data_off.value, get_data.value, '{0} failed.'.format(self._testMethodName))

    def test_CreatGroup(self):
        # Set axis0, axis1 as group, 0 as group id.
        excepted_err = 0
        self.errCde = self.AdvMot.Acm2_GpCreate(self.gpid, self.axis_array, len(self.axis_array))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_CheckGroupAxes(self):
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        excepted_err = 0
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(self.gpid, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(self.axis_array[idx], get_axes[idx], '{0} failed.'.format(self._testMethodName))
    
    def test_RemoveGroup(self):
        remove_all_axes = c_uint32(0)
        excepted_err = 0
        self.errCde = self.AdvMot.Acm2_GpCreate(self.gpid, self.axis_array, remove_all_axes)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GetLastError_Device(self):
        excepted_err = 0
        obj_logicID = c_uint32(0)
        obj_type = c_uint(ADV_OBJ_TYPE.ADV_DEVICE.value)
        self.errCde = self.AdvMot.Acm2_GetLastError(obj_type, obj_logicID)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GetLastError_AXIS(self):
        excepted_err = 0
        for i in range(64):
            obj_logicID = c_uint32(i)
            obj_type = c_uint(ADV_OBJ_TYPE.ADV_AXIS.value)
            self.errCde = self.AdvMot.Acm2_GetLastError(obj_type, obj_logicID)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GetLastError_Group(self):
        excepted_err = 0
        for i in range(8):
            obj_logicID = c_uint32(i)
            obj_type = c_uint(ADV_OBJ_TYPE.ADV_GROUP.value)
            self.errCde = self.AdvMot.Acm2_GetLastError(obj_type, obj_logicID)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_SetMultiPropertyAndCheck_AxisSpeed(self):
        excepted_err = 0
        # Set axis 0 speed info at once
        ax_id = c_uint32(0)
        property_arr = [c_uint32(PropertyID2.PAR_AxVelLow.value), c_uint32(PropertyID2.PAR_AxVelHigh.value)]
        trans_ppt_arr = (c_uint32 * len(property_arr))(*property_arr)
        # Default value of velocity low is 2000, and velocity high is 8000.
        value_arr = [c_double(1000), c_double(2000)]
        trans_val_arr = (c_double * len(value_arr))(*value_arr)
        data_cnt = c_uint32(2)
        err_buffer = (c_uint32 * data_cnt.value)()
        # Set value
        self.errCde = self.AdvMot.Acm2_SetMultiProperty(ax_id, trans_ppt_arr, trans_val_arr, data_cnt, err_buffer)
        self.assertEqual(excepted_err, self.errCde)
        # Check value
        get_val = (c_double * data_cnt.value)()
        self.errCde = self.AdvMot.Acm2_GetMultiProperty(ax_id, trans_ppt_arr, get_val, data_cnt, err_buffer)
        self.assertEqual(excepted_err, self.errCde)
        for i in range(data_cnt.value):
            # print('set[{0}]:{1}, get:{2}'.format(i, value_arr[i].value, get_val[i]))
            self.assertEqual(value_arr[i].value, get_val[i], '{0} failed.'.format(self._testMethodName))
    
    def test_SetAxSpeedInfoAndCheck(self):
        excepted_err = 0
        ax_id = c_uint32(0)
        speed_info = SPEED_PROFILE_PRM()
        speed_info.FH = c_double(3000)
        speed_info.FL = c_double(1500)
        speed_info.Acc = c_double(11000)
        speed_info.Dec = c_double(9900)
        speed_info.JerkFac = c_double(0)
        # Set speed information
        self.errCde = self.AdvMot.Acm2_AxSetSpeedProfile(ax_id, speed_info)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_SetAxJogInfo(self):
        excepted_err = 0
        ax_id = c_uint32(0)
        jog_speed_info = JOG_SPEED_PROFILE_PRM()
        jog_speed_info.FH = c_double(8000)
        jog_speed_info.FL = c_double(1000)
        jog_speed_info.Acc = c_double(10000)
        jog_speed_info.Dec = c_double(5000)
        jog_speed_info.VLTime = c_double(2000)
        # Set axis 0 jog speed information
        self.errCde = self.AdvMot.Acm2_AxSetJogSpeedProfile(ax_id, jog_speed_info)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_GetCurrentVelocity(self):
        excepted_err = 0
        ax_id = c_uint32(0)
        get_vel = c_double(0)
        vel_Type = c_uint(VELOCITY_TYPE.VELOCITY_CMD.value)
        # Get axis 0 current velocity
        self.errCde = self.AdvMot.Acm2_AxGetVel(ax_id, vel_Type, byref(get_vel))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_PVTTable(self):
        excepted_err = 0
        ax_id = c_uint32(0)
        # Reset PVT table
        self.errCde = self.AdvMot.Acm2_AxResetPVTTable(ax_id)
        self.assertEqual(excepted_err, self.errCde)
        ''' PVT table
        |Position|Vel |Time|
        |--------|----|----|
        |0       |0   |0   |
        |5000    |4000|2000|
        |15000   |5000|3000|
        |30000   |8000|4000|
        '''
        pos_arr = [c_double(0), c_double(5000), c_double(15000), c_double(30000)]
        posArr = (c_double * len(pos_arr))(*pos_arr)
        vel_arr = [c_double(0), c_double(4000), c_double(5000), c_double(8000)]
        velArr = (c_double * len(vel_arr))(*vel_arr)
        time_arr = [c_double(0), c_double(2000), c_double(3000), c_double(4000)]
        timeArr = (c_double * len(time_arr))(*time_arr)
        # Set table of PVT
        self.errCde = self.AdvMot.Acm2_AxLoadPVTTable(ax_id, posArr, velArr, timeArr, len(pos_arr))
        self.assertEqual(excepted_err, self.errCde)
        # Set PVT
        self.errCde = self.AdvMot.Acm2_AxMovePVT(ax_id)
        self.assertEqual(excepted_err, self.errCde)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        get_pos = c_double(0)
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        self.errCde = self.AdvMot.Acm2_AxGetPosition(ax_id, pos_type, byref(get_pos))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(c_double(30000).value, get_pos.value, '{0} failed.'.format(self._testMethodName))

    def test_PTTable(self):
        excepted_err = 0
        ax_id = c_uint32(0)
        # Reset PT table
        self.errCde = self.AdvMot.Acm2_AxResetPTData(ax_id)
        self.assertEqual(excepted_err, self.errCde)
        ''' PT table
        |Position|Time|
        |--------|----|
        |0       |0   |
        |5000    |2000|
        |15000   |3000|
        |30000   |5000|
        '''
        pos_arr = [c_double(0), c_double(5000), c_double(15000), c_double(30000)]
        time_arr = [c_double(0), c_double(2000), c_double(3000), c_double(5000)]
        # Set PT table
        for i in range(len(pos_arr)):
            self.errCde = self.AdvMot.Acm2_AxAddPTData(ax_id, pos_arr[i], time_arr[i])
            self.assertEqual(excepted_err, self.errCde)
        # Start move PT table
        self.errCde = self.AdvMot.Acm2_AxMovePT(ax_id)
        self.assertEqual(excepted_err, self.errCde)

        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        get_pos = c_double(0)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(ax_id, pos_type, byref(get_pos))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(c_double(30000).value, get_pos.value, '{0} failed.'.format(self._testMethodName))

    def test_Gear(self):
        excepted_err = 0
        primary_ax = c_uint32(0)
        follow_ax = c_uint32(1)
        # Reset following axis
        self.errCde = self.AdvMot.Acm2_AxSyncOut(follow_ax)
        self.assertEqual(excepted_err, self.errCde)
        gear_param = GEAR_IN_PRM()
        # Position type as command position
        gear_param.RefSrc = c_uint32(POSITION_TYPE.POSITION_CMD.value)
        # Mode as relative mode
        gear_param.Mode = c_uint32(0)
        # Set gear ratio
        gear_param.GearPosition = c_double(0)
        gear_param.GearRatioRate.Num = c_double(1)
        gear_param.GearRatioRate.Den = c_double(1)
        # Set gear
        self.errCde = self.AdvMot.Acm2_AxGearIn(primary_ax, follow_ax, gear_param)
        self.assertEqual(excepted_err, self.errCde)
        # Move primary axis
        abs_mode = c_uint(ABS_MODE.MOVE_REL.value)
        distance = c_double(10000)
        self.errCde = self.AdvMot.Acm2_AxPTP(primary_ax, abs_mode, distance)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 (primary) position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(primary_ax, pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(distance.value, get_pos_0.value)
        # Get axis 1 (following) position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(follow_ax, pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(distance.value, get_pos_1.value)
        # Reset following axis
        self.errCde = self.AdvMot.Acm2_AxSyncOut(follow_ax)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Gantry(self):
        excepted_err = 0
        primary_ax = c_uint32(0)
        follow_ax = c_uint32(1)
        # Reset following axis
        self.errCde = self.AdvMot.Acm2_AxSyncOut(follow_ax)
        self.assertEqual(excepted_err, self.errCde)
        # Set gantry parameter
        gantry_param = GANTRY_IN_PRM()
        # Set gantry reference source as command position
        gantry_param.RefSrc = c_int16(POSITION_TYPE.POSITION_CMD.value)
        # Set gantry direction as positive
        gantry_param.Direction = c_int16(MOTION_DIRECTION.DIRECTION_POS.value)
        # Set gantry
        self.errCde = self.AdvMot.Acm2_AxGantryIn(primary_ax, follow_ax, gantry_param)
        self.assertEqual(excepted_err, self.errCde)
        # Move primary axis
        abs_mode = c_uint(ABS_MODE.MOVE_REL.value)
        distance = c_double(10000)
        self.errCde = self.AdvMot.Acm2_AxPTP(primary_ax, abs_mode, distance)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 (primary) position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(primary_ax, pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(distance.value, get_pos_0.value)
        # Get axis 1 (following) position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(follow_ax, pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(distance.value, get_pos_1.value)
        # Reset following axis
        self.errCde = self.AdvMot.Acm2_AxSyncOut(follow_ax)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GpLine(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set group move as relative
        gp_move_mode = c_uint(GP_LINE_MODE.LINE_REL.value)
        # Set group end position: axis(0) = 10000, axis(1) = 10000
        end_pos_arr = [c_double(10000), c_double(10000)]
        arr_element = c_uint32(len(end_pos_arr))
        end_arr = (c_double * len(end_pos_arr))(*end_pos_arr)
        # Group 0 move line
        self.errCde = self.AdvMot.Acm2_GpLine(gp_id, gp_move_mode, end_arr, byref(arr_element))
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 (primary) position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_pos_arr[0].value, get_pos_0.value)
        # Get axis 1 (following) position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_pos_arr[1].value, get_pos_1.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_2DArc(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set 2D Arc mode
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set 2D Arc CW center, end position
        '''
        | axis | Arc center | Arc end |
        |------|------------|---------|
        |   0  |    8000    |  16000  |
        |   1  |      0     |    0    |
        '''
        center_ax_arr = [c_double(8000), c_double(0)]
        center_arr = (c_double * len(center_ax_arr))(*center_ax_arr)
        end_ax_arr = [c_double(16000), c_double(0)]
        end_arr = (c_double * len(end_ax_arr))(*end_ax_arr)
        arr_element = c_uint32(len(end_ax_arr))
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        self.errCde = self.AdvMot.Acm2_GpArc_Center(gp_id, arc_mode, center_arr, end_arr, byref(arr_element), dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_ax_arr[0].value, get_pos_0.value)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_ax_arr[1].value, get_pos_1.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_2DArc3P(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set 2D Arc mode as relative, which the starting point of circular is (0, 0)
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set 2D Arc CW center, end position
        '''
        | axis | point 1 | end point |
        |------|---------|-----------|
        | 0(x) |   8000  |   16000   |
        | 1(y) |   8000  |     0     |
        '''
        ref_arr = [c_double(8000), c_double(8000)]
        refArr = (c_double * len(ref_arr))(*ref_arr)
        end_arr = [c_double(16000), c_double(0)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(ref_arr))
        # Set arc movement as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        self.errCde = self.AdvMot.Acm2_GpArc_3P(gp_id, arc_mode, refArr, endArr, byref(arr_element), dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_arr[0].value, get_pos_0.value)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_arr[1].value, get_pos_1.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_2DArcAngle(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set 2D Arc mode as relative, which the starting point of circular is (0, 0)
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set center as (20000, 20000)
        center_arr = [c_double(20000), c_double(20000)]
        centerArr = (c_double * len(center_arr))(*center_arr)
        arr_element = c_uint32(len(center_arr))
        # Set degree as 45
        degree = c_double(45)
        # Set arc movement as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        self.errCde = self.AdvMot.Acm2_GpArc_Angle(gp_id, arc_mode, centerArr, byref(arr_element), degree, dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual((round(center_arr[0].value - (center_arr[0].value * (2 ** 0.5)))), get_pos_0.value)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(center_arr[1].value, get_pos_1.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_3DArcCenter(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set 3D Arc mode
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set 3D Arc CW, with 120 degree
        '''
        | axis | Arc center | Arc end |
        |------|------------|---------|
        |   0  |    20000   |  20000  |
        |   1  |    20000   |  40000  |
        |   2  |      0     |  20000  |
        '''
        center_ax_arr = [c_double(20000), c_double(20000), c_double(0)]
        center_arr = (c_double * len(center_ax_arr))(*center_ax_arr)
        end_ax_arr = [c_double(20000), c_double(40000), c_double(20000)]
        end_arr = (c_double * len(end_ax_arr))(*end_ax_arr)
        arr_element = c_uint32(len(end_ax_arr))
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        self.errCde = self.AdvMot.Acm2_Gp3DArc_Center(gp_id, arc_mode, center_arr, end_arr, byref(arr_element), dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_ax_arr[0].value, get_pos_0.value)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_ax_arr[1].value, get_pos_1.value)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_ax_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_3DArcNormVec(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set 3D Arc mode
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        # Set 3D Arc CW, with 120 degree
        '''
        | axis | Arc center | Arc end |
        |------|------------|---------|
        |   0  |    20000   |  20000  |
        |   1  |    20000   |  40000  |
        |   2  |      0     |  20000  |
        '''
        center_arr = [c_double(20000), c_double(20000), c_double(0)]
        centerArr = (c_double * len(center_arr))(*center_arr)
        v1 = np.array([(0-center_arr[0].value), (0-center_arr[1].value), (0-center_arr[2].value)])
        arc_end_arr = [c_double(20000), c_double(40000), c_double(20000)]
        v2 = np.array([(arc_end_arr[0].value-center_arr[0].value), (arc_end_arr[1].value-center_arr[1].value), (arc_end_arr[2].value-center_arr[2].value)])
        cross_product = np.cross(v1, v2)
        normalize_cross = cross_product / (center_arr[0].value * center_arr[0].value)
        norm_vec_arr = [c_double(normalize_cross[0]), c_double(normalize_cross[1]), c_double(normalize_cross[2])]
        normVecArr = (c_double * len(norm_vec_arr))(*norm_vec_arr)
        arr_element = c_uint32(len(center_arr))
        angle = c_double(120)
        self.errCde = self.AdvMot.Acm2_Gp3DArc_NormVec(gp_id, arc_mode, centerArr, normVecArr, byref(arr_element), angle, dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(arc_end_arr[0].value, get_pos_0.value)
        self.assertEqual(arc_end_arr[1].value, get_pos_1.value)
        self.assertEqual(arc_end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Gp3DArc3P(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # # Set 3D Arc mode as relative, which the starting point of circular is (0, 0, 0)
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set 3D Arc CW, with 120 degree
        '''
        | axis | point 1 | end point |
        |------|---------|-----------|
        | 0(x) |  20000  |   20000   |
        | 1(y) |  20000  |   40000   |
        | 2(z) |    0    |   20000   |
        '''
        ref_arr = [c_double(20000), c_double(20000), c_double(0)]
        refArr = (c_double * len(ref_arr))(*ref_arr)
        end_arr = [c_double(20000), c_double(40000), c_double(20000)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(ref_arr))
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        cyc_cnt = c_uint32(0)
        # Set arc movement with 3 point of circular
        self.errCde = self.AdvMot.Acm2_Gp3DArc_3P(gp_id, arc_mode, refArr, endArr, byref(arr_element), dir_mode, cyc_cnt)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_arr[0].value, get_pos_0.value)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_arr[1].value, get_pos_1.value)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_3DArcAngle(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # # Set 3D Arc mode as relative, which the starting point of circular is (0, 0, 0)
        arc_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        # Set 3D Arc CW, with 120 degree
        '''
        | axis | point 1 | end point |
        |------|---------|-----------|
        | 0(x) |  20000  |   20000   |
        | 1(y) |  20000  |   40000   |
        | 2(z) |    0    |   20000   |
        '''
        ref_arr = [c_double(20000), c_double(20000), c_double(0)]
        refArr = (c_double * len(ref_arr))(*ref_arr)
        end_arr = [c_double(20000), c_double(40000), c_double(20000)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(ref_arr))
        degree = c_double(120)
        # Set arc movement with 3 point of circular
        self.errCde = self.AdvMot.Acm2_Gp3DArc_3PAngle(gp_id, arc_mode, refArr, endArr, byref(arr_element), degree, dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value
        self.assertEqual(end_arr[0].value, get_pos_0.value)
        self.assertEqual(end_arr[1].value, get_pos_1.value)
        self.assertEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def GpHelixCenter(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set mode as relative
        helix_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set center as (10000, 0, 0)
        center_arr = [c_double(8000), c_double(0), c_double(0)]
        centerArr = (c_double * len(center_arr))(*center_arr)
        # Set end position as (20000, 0, 20000)
        end_arr = [c_double(16000), c_double(0), c_double(10000)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(end_arr))
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        # Set Helix movement
        self.errCde = self.AdvMot.Acm2_GpHelix_Center(gp_id, helix_mode, centerArr, endArr, byref(arr_element), dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value
        self.assertEqual(end_arr[0].value, get_pos_0.value)
        self.assertEqual(end_arr[1].value, get_pos_1.value)
        self.assertEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Helix3P(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set mode as relative
        helix_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set center as (8000, 0, 0)
        center_arr = [c_double(8000), c_double(0), c_double(0)]
        centerArr = (c_double * len(center_arr))(*center_arr)
        # Set end position as (16000, 16000, 10000)
        end_arr = [c_double(16000), c_double(16000), c_double(10000)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(center_arr))
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        # Set Helix movement
        self.errCde = self.AdvMot.Acm2_GpHelix_3P(gp_id, helix_mode, centerArr, endArr, byref(arr_element), dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value
        self.assertEqual(end_arr[0].value, get_pos_0.value)
        self.assertEqual(end_arr[1].value, get_pos_1.value)
        self.assertEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_HelixAngle(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set mode as relative
        helix_mode = c_uint(ABS_MODE.MOVE_REL.value)
        # Set center as (200, 0)
        center_arr = [c_double(200), c_double(0), c_double(0)]
        centerArr = (c_double * len(center_arr))(*center_arr)
        # Set 120 as degree
        end_arr = [c_double(4000), c_double(4000), c_double(120)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(center_arr))
        # Set direction as CW
        dir_mode = c_uint(ARC_DIRECTION.ARC_CW.value)
        # Set Helix movement
        self.errCde = self.AdvMot.Acm2_GpHelix_Angle(gp_id, helix_mode, centerArr, endArr, byref(arr_element), dir_mode)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value
        self.assertEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GpLinePauseAndResume(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set mode as relative
        move_mode = c_uint(GP_LINE_MODE.LINE_REL.value)
        end_arr = [c_double(20000), c_double(20000), c_double(20000)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(end_arr))
        self.errCde = self.AdvMot.Acm2_GpLine(gp_id, move_mode, endArr, arr_element)
        self.assertEqual(excepted_err, self.errCde)
        # Pause movement
        self.errCde = self.AdvMot.Acm2_GpPause(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value: Not equal to target position
        self.assertNotEqual(end_arr[0].value, get_pos_0.value)
        self.assertNotEqual(end_arr[1].value, get_pos_1.value)
        self.assertNotEqual(end_arr[2].value, get_pos_2.value)
        # Resume movement
        self.errCde = self.AdvMot.Acm2_GpResume(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value: Equal to target position
        self.assertEqual(end_arr[0].value, get_pos_0.value)
        self.assertEqual(end_arr[1].value, get_pos_1.value)
        self.assertEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GpStop(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1), c_uint32(2)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1, 2 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Set mode as relative
        move_mode = c_uint(GP_LINE_MODE.LINE_REL.value)
        end_arr = [c_double(200000), c_double(200000), c_double(200000)]
        endArr = (c_double * len(end_arr))(*end_arr)
        arr_element = c_uint32(len(end_arr))
        self.errCde = self.AdvMot.Acm2_GpLine(gp_id, move_mode, endArr, arr_element)
        self.assertEqual(excepted_err, self.errCde)
        # Check group status
        time.sleep(2)
        gp_state = c_uint32(0)
        self.errCde = self.AdvMot.Acm2_GpGetState(gp_id, byref(gp_state))
        print('gp_state:0x{0:x}'.format(gp_state.value))
        # Change velocity
        new_vel = c_double(5000)
        new_acc = c_double(9000)
        new_dec = c_double(4000)
        self.errCde = self.AdvMot.Acm2_GpChangeVel(gp_id, new_vel, new_acc, new_dec)
        self.assertEqual(excepted_err, self.errCde)
        vel_type = c_uint(VELOCITY_TYPE.VELOCITY_CMD.value)
        get_gp_vel = c_double(0)
        time.sleep(2)
        self.errCde = self.AdvMot.Acm2_GpGetVel(gp_id, vel_type, byref(get_gp_vel))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(new_vel.value, get_gp_vel.value)
        print('gp vel:{0}'.format(get_gp_vel.value))
        # Set stop mode as deceleration to stop
        stop_mode = c_uint(MOTION_STOP_MODE.MOTION_STOP_MODE_DEC.value)
        self.errCde = self.AdvMot.Acm2_GpMotionStop(gp_id, stop_mode, new_dec)
        self.assertEqual(excepted_err, self.errCde)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        get_pos_2 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 2 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[2], pos_type, byref(get_pos_2))
        self.assertEqual(excepted_err, self.errCde)
        # Check value: Not equal to target position
        self.assertNotEqual(end_arr[0].value, get_pos_0.value)
        self.assertNotEqual(end_arr[1].value, get_pos_1.value)
        self.assertNotEqual(end_arr[2].value, get_pos_2.value)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GpAddPath(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Reset group path
        self.errCde = self.AdvMot.Acm2_GpResetPath(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        # Set 2D Arc CW center, end position
        '''
        | axis | Arc center | Arc end |
        |------|------------|---------|
        |   0  |    8000    |  16000  |
        |   1  |      0     |    0    |
        '''
        # Set path table
        '''
        | index | move command | move mode | Vel High | Vel Low | Acc | Dec |   End Point  | Center Point |
        |-------|--------------|-----------|----------|---------|-----|-----|--------------|--------------|
        |   0   |  Rel2DArcCCW |BUFFER_MODE|   8000   |   1000  |10000|10000|(16000, 16000)| (8000, 8000) |
        |   1   |    EndPath   |BUFFER_MODE|     0    |     0   |  0  |  0  |       0      |      0       |
        '''
        move_cmd_arr = [c_uint32(MOTION_PATH_CMD.Rel2DArcCCW.value), c_uint32(MOTION_PATH_CMD.EndPath.value)]
        move_mode = c_uint(PATH_MOVE_MODE_CM2.BUFFER_MODE.value)
        fh = [c_double(8000), c_double(0)]
        fl = [c_double(1000), c_double(0)]
        acc = [c_double(10000), c_double(0)]
        dec = [c_double(10000), c_double(0)]
        end_arr = [
            [c_double(16000), c_double(16000)], 
            [c_double(0), c_double(0)]
        ]
        center_arr = [
            [c_double(8000), c_double(8000)], 
            [c_double(0), c_double(0)]
        ]
        arr_element = c_uint32(len(end_arr[0]))
        for i in range(1):
            endArr = (c_double * len(end_arr[i]))(*end_arr[i])
            centerArr = (c_double * len(center_arr[i]))(*center_arr[i])
            self.errCde = self.AdvMot.Acm2_GpAddPath(gp_id, move_cmd_arr[i], move_mode, fh[i], fl[i], acc[i], dec[i], endArr, centerArr, arr_element)
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Start move path
        self.errCde = self.AdvMot.Acm2_GpMovePath(gp_id)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Check value: Equal to target position
        self.assertEqual(end_arr[0][0].value, get_pos_0.value)
        self.assertEqual(end_arr[0][1].value, get_pos_1.value)
        # Reset group path
        self.errCde = self.AdvMot.Acm2_GpResetPath(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GpLoadPath(self):
        excepted_err = 0
        gp_ax_arr = [c_uint32(0), c_uint32(1)]
        gp_id = c_uint32(0)
        gp_arr = (c_uint32 * len(gp_ax_arr))(*gp_ax_arr)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde)
        # Creat group 0, and set axis 0, 1 into group
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, len(gp_arr))
        self.assertEqual(excepted_err, self.errCde)
        # get_axes size must be same as len_get
        len_get = c_uint32(64)
        get_axes = (c_uint32 * len_get.value)()
        # Get axes in group 0 and check
        self.errCde = self.AdvMot.Acm2_GpGetAxesInGroup(gp_id, get_axes, len_get)
        self.assertEqual(excepted_err, self.errCde)
        for idx in range(len_get.value):
            self.assertEqual(gp_arr[idx], get_axes[idx])
        # Reset group path
        self.errCde = self.AdvMot.Acm2_GpResetPath(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        # Create path file by path editor inside the Utility
        if os.name == 'nt':
            path_bin_file = b'test\\testPath.bin'
        else:
            path_bin_file = b'test/testPath.bin'
        '''
        | index | move command | move mode | Vel High | Vel Low | Acc | Dec |   End Point  |
        |-------|--------------|-----------|----------|---------|-----|-----|--------------|
        |   0   |   Rel2DLine  |BUFFER_MODE|   8000   |   1000  |10000|10000|(10000, 10000)|
        |   1   |   Rel2DLine  |BUFFER_MODE|   8000   |   1000  |10000|10000|(10000, 10000)|
        |   2   |    EndPath   |BUFFER_MODE|     0    |     0   |  0  |  0  |       0      |
        '''
        cnt = c_uint32(0)
        self.errCde = self.AdvMot.Acm2_GpLoadPath(gp_id, path_bin_file, byref(cnt))
        self.assertEqual(excepted_err, self.errCde)
        # Start move path
        self.errCde = self.AdvMot.Acm2_GpMovePath(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        path_status = c_uint(0)
        self.errCde = self.AdvMot.Acm2_GpGetPathStatus(gp_id, byref(path_status))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(excepted_err, path_status.value)
        # Check status
        while self.state.value != AXIS_STATE.STA_AX_READY.value:
            time.sleep(1)
            self.test_GetAxState()
        # Get axis 0 position
        get_pos_0 = c_double(0)
        get_pos_1 = c_double(0)
        pos_type = c_uint(POSITION_TYPE.POSITION_CMD.value)
        # Get axis 0 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[0], pos_type, byref(get_pos_0))
        self.assertEqual(excepted_err, self.errCde)
        # Get axis 1 position
        self.errCde = self.AdvMot.Acm2_AxGetPosition(gp_ax_arr[1], pos_type, byref(get_pos_1))
        self.assertEqual(excepted_err, self.errCde)
        # Check value: Equal to target position
        self.assertEqual(20000, get_pos_0.value)
        self.assertEqual(20000, get_pos_1.value)
        # Reset group path
        self.errCde = self.AdvMot.Acm2_GpResetPath(gp_id)
        self.assertEqual(excepted_err, self.errCde)
        # Reset all axes from group 0
        self.errCde = self.AdvMot.Acm2_GpCreate(gp_id, gp_arr, 0)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_LoadConnect5074And5057SO(self):
        excepted_err = 0
        # eni file can be create by the Utility
        if os.name == 'nt':
            eni_path = b'test\\eni1.xml'
        else:
            eni_path = b'test/eni1.xml'
        # Motion ring number:0, IO Ring number:1, IORing is SM mode only
        ring_no = c_uint32(1)
        self.errCde = self.AdvMot.Acm2_DevLoadENI(ring_no, eni_path)
        self.assertEqual(excepted_err, self.errCde)
        # After load eni file, StartFieldbus/Connect to subdevices.
        self.errCde = self.AdvMot.Acm2_DevConnect(ring_no)
        self.assertEqual(excepted_err, self.errCde)
        # Set EtherCAT type as position
        ecat_type = c_uint(ECAT_ID_TYPE.SUBDEVICE_POS.value)
        # SubDevice position 0 is AMAX-5074
        sub_dev0 = c_uint32(0)
        # SubDevice position 1 is AMAX-5057SO
        sub_dev1 = c_uint32(1)
        # Sundevice position 2 is AMAX-4820
        sub_dev2 = c_uint32(2)
        # Sundevice position 3 is AMAX-4817
        sub_dev3 = c_uint32(3)
        get_sub_dev_state0 = c_uint32(0)
        get_sub_dev_state1 = c_uint32(0)
        get_sub_dev_state2 = c_uint32(0)
        get_sub_dev_state3 = c_uint32(0)
        while (get_sub_dev_state0.value != SUB_DEV_STATE.EC_SLAVE_STATE_OP.value) or (get_sub_dev_state1.value != SUB_DEV_STATE.EC_SLAVE_STATE_OP.value) or (get_sub_dev_state2.value != SUB_DEV_STATE.EC_SLAVE_STATE_OP.value) or (get_sub_dev_state3.value != SUB_DEV_STATE.EC_SLAVE_STATE_OP.value):
            # Get AMAX-5074 status
            self.errCde = self.AdvMot.Acm2_DevGetSubDeviceStates(ring_no, ecat_type, sub_dev0, byref(get_sub_dev_state0))
            self.assertEqual(excepted_err, self.errCde)
            # Get AMAX-5057SO status
            self.errCde = self.AdvMot.Acm2_DevGetSubDeviceStates(ring_no, ecat_type, sub_dev1, byref(get_sub_dev_state1))
            self.assertEqual(excepted_err, self.errCde)
            # Get AMAX-4820 status
            self.errCde = self.AdvMot.Acm2_DevGetSubDeviceStates(ring_no, ecat_type, sub_dev2, byref(get_sub_dev_state2))
            self.assertEqual(excepted_err, self.errCde)
            # Get AMAX-4817 status
            self.errCde = self.AdvMot.Acm2_DevGetSubDeviceStates(ring_no, ecat_type, sub_dev3, byref(get_sub_dev_state3))
            self.assertEqual(excepted_err, self.errCde)
            time.sleep(0.5)
    
    def test_DisConnectAll(self):
        # Motion ring number:0, IO Ring number:1, IORing is SM mode only
        ring_no0 = c_uint32(0)
        ring_no1 = c_uint32(1)
        excepted_err = 0
        # Disconnect devices
        self.errCde = self.AdvMot.Acm2_DevDisConnect(ring_no0)
        self.assertEqual(excepted_err, self.errCde)
        self.errCde = self.AdvMot.Acm2_DevDisConnect(ring_no1)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Set5057SODO(self):
        # Set DO channel, local DO on PCIE-1203 is 0~1, rest of device will set from channel 8~
        do_channel8 = c_uint32(8)
        do_channel14 = c_uint32(14)
        bit_data_on = c_uint32(DO_ONOFF.DO_ON.value)
        bit_data_off = c_uint32(DO_ONOFF.DO_OFF.value)
        excepted_err = 0
        # Set DO(8) on
        self.errCde = self.AdvMot.Acm2_ChSetDOBit(do_channel8, bit_data_on)
        self.assertEqual(excepted_err, self.errCde)
        # Set DO(14) on
        self.errCde = self.AdvMot.Acm2_ChSetDOBit(do_channel14, bit_data_on)
        self.assertEqual(excepted_err, self.errCde)
        time.sleep(0.5)
        get_data8 = c_uint32(0)
        get_data14 = c_uint32(0)
        # Get DO(8) value
        self.errCde = self.AdvMot.Acm2_ChGetDOBit(do_channel8, byref(get_data8))
        self.assertEqual(excepted_err, self.errCde)
        # Get DO(14) value
        self.errCde = self.AdvMot.Acm2_ChGetDOBit(do_channel8, byref(get_data14))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(DO_ONOFF.DO_ON.value, get_data8.value)
        self.assertEqual(DO_ONOFF.DO_ON.value, get_data14.value)
        time.sleep(0.5)
        # Set DO(8) off
        self.errCde = self.AdvMot.Acm2_ChSetDOBit(do_channel8, bit_data_off)
        self.assertEqual(excepted_err, self.errCde)
        # Set DO(14) off
        self.errCde = self.AdvMot.Acm2_ChSetDOBit(do_channel14, bit_data_off)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def Set5057DOByByte(self):
        excepted_err = 0
        port_num = c_uint32(2)
        start_ch = c_uint32(1)
        get_byte_value = (c_uint32 * 2)()
        time.sleep(1)
        # Get DO byte of 5057SO (0~7)
        self.errCde = self.AdvMot.Acm2_ChGetDOByte(start_ch, port_num, get_byte_value)
        self.assertEqual(excepted_err, self.errCde)
        for i in range(len(get_byte_value)):
            self.assertEqual(c_uint32(DO_ONOFF.DO_OFF.value).value, get_byte_value[i])
        # Port 1(AMAX-5057SO) bit 15~8
        set_byte_str_1 = '10101010'
        # Port 2(AMAX-5057SO) bit 23~16
        set_byte_str_2 = '11100011'
        set_byte_int_1 = int(set_byte_str_1, 2)
        set_byte_int_2 = int(set_byte_str_2, 2)
        set_byte_value_on = [c_uint32(set_byte_int_1), c_uint32(set_byte_int_2)]
        set_byte_value_off = [c_uint32(DO_ONOFF.DO_OFF.value)] * 2
        set_value_arr_on = (c_uint32 * len(set_byte_value_on))(*set_byte_value_on)
        set_value_arr_off = (c_uint32 * len(set_byte_value_off))(*set_byte_value_off)
        time.sleep(0.5)
        # Set DO byte of 5057SO (0~7)
        self.errCde = self.AdvMot.Acm2_ChSetDOByte(start_ch, port_num, set_value_arr_on)
        self.assertEqual(excepted_err, self.errCde)
        time.sleep(1)
        # Get DO byte of 5057SO (0~7)
        self.errCde = self.AdvMot.Acm2_ChGetDOByte(start_ch, port_num, get_byte_value)
        self.assertEqual(excepted_err, self.errCde)
        for i in range(len(get_byte_value)):
            self.assertEqual(set_byte_value_on[i].value, get_byte_value[i])
        time.sleep(0.5)
        # Set DO byte of 5057SO (0~7)
        self.errCde = self.AdvMot.Acm2_ChSetDOByte(start_ch, port_num, set_value_arr_off)
        self.assertEqual(excepted_err, self.errCde)
        # Get DO byte of 5057SO (0~7)
        self.errCde = self.AdvMot.Acm2_ChGetDOByte(start_ch, port_num, get_byte_value)
        self.assertEqual(excepted_err, self.errCde)
        for i in range(len(get_byte_value)):
            self.assertEqual(c_uint32(DO_ONOFF.DO_OFF.value).value, get_byte_value[i])
    
    def test_GetSubdeviceInfo(self):
        excepted_err = 0
        ring_no = c_uint32(1)
        # Get subdevice ID
        id_type = c_uint(ECAT_ID_TYPE.SUBDEVICE_ID.value)
        id_cnt = c_uint32(4)
        phys_addr_arr = [0] * id_cnt.value
        id_arr = (c_uint32 * id_cnt.value)()
        self.errCde = self.AdvMot.Acm2_DevGetSubDevicesID(ring_no, id_type, id_arr, byref(id_cnt))
        self.assertEqual(excepted_err, self.errCde)
        if os.name == 'nt':
            tree = xml.parse('test\\eni1.xml')
        else:
            tree = xml.parse('test/eni1.xml')
        idx = 0
        # Check value from xml
        for subdev in tree.findall('.//Slave'):
            phys_addr = int(subdev.find('Info/PhysAddr').text)
            phys_addr_arr[idx] = phys_addr
            idx += 1
        for i in range(id_cnt.value):
            self.assertEqual(phys_addr_arr[i], id_arr[i])
            sub_dev_info = ADVAPI_SUBDEVICE_INFO_CM2()
            # Get subdevice info by subdevice id
            self.errCde = self.AdvMot.Acm2_DevGetSubDeviceInfo(ring_no, c_uint(ECAT_ID_TYPE.SUBDEVICE_ID.value), id_arr[i], byref(sub_dev_info))
            self.assertEqual(id_arr[i], sub_dev_info.SubDeviceID)
            self.assertEqual(excepted_err, self.errCde)
            # Get subdevice info by subdevice position
            self.errCde = self.AdvMot.Acm2_DevGetSubDeviceInfo(ring_no, c_uint(ECAT_ID_TYPE.SUBDEVICE_POS.value), i, byref(sub_dev_info))
            self.assertEqual(id_arr[i], sub_dev_info.SubDeviceID)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_GetMainDeviceInfo(self):
        excepted_err = 0
        ring_no = c_uint32(1)
        main_dev_info = ADVAPI_MDEVICE_INFO()
        self.errCde = self.AdvMot.Acm2_DevGetMDeviceInfo(ring_no, byref(main_dev_info))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        print('slave_count:{0}'.format(main_dev_info.slave_count))

    def test_WriteAndReadByPDO(self):
        excepted_err = 0
        # Ring as IO Ring
        ring_no = c_uint32(1)
        # set by position
        id_type = c_uint(ECAT_ID_TYPE.SUBDEVICE_POS.value)
        sub_dev_pos = c_uint32(1)
        # AMAX-5057SO 0x3101:01 is DO(0)
        pdo_idx = c_uint32(0x3101)
        pdo_sub_idx = c_uint32(0x01)
        # DO(0) data type is boolean
        pdo_type = c_uint32(ECAT_TYPE.ECAT_TYPE_BOOL.value)
        pdo_data_size = c_uint32(sizeof(c_bool))
        val_on = c_bool(1)
        val_off = c_bool(0)
        get_value = c_bool(0)
        # Set DO(0) on by PDO
        self.errCde = self.AdvMot.Acm2_DevWritePDO(ring_no, id_type, sub_dev_pos, pdo_idx, pdo_sub_idx, pdo_type, pdo_data_size, byref(val_on))
        self.assertEqual(excepted_err, self.errCde)
        # Get DO(0) value by PDO
        self.errCde = self.AdvMot.Acm2_DevReadPDO(ring_no, id_type, sub_dev_pos, pdo_idx, pdo_sub_idx, pdo_type, pdo_data_size, byref(get_value))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(val_on.value, get_value.value)
        # Set DO(0) off by PDO
        self.errCde = self.AdvMot.Acm2_DevWritePDO(ring_no, id_type, sub_dev_pos, pdo_idx, pdo_sub_idx, pdo_type, pdo_data_size, byref(val_off))
        self.assertEqual(excepted_err, self.errCde)
        # Get DO(0) value by PDO
        self.errCde = self.AdvMot.Acm2_DevReadPDO(ring_no, id_type, sub_dev_pos, pdo_idx, pdo_sub_idx, pdo_type, pdo_data_size, byref(get_value))
        self.assertEqual(excepted_err, self.errCde)
        self.assertEqual(val_off.value, get_value.value, '{0} failed.'.format(self._testMethodName))

    def test_Set4820AOData(self):
        excepted_err = 0
        # Ring as IO Ring
        ring_no = c_uint32(1)
        # set by position
        id_type = c_uint(ECAT_ID_TYPE.SUBDEVICE_POS.value)
        # Sort AMAX-4820 in second posiotn
        sub_dev_pos = c_uint32(2)
        # Set AO(0) output range as -10V ~ 10V
        pdo_type = c_uint32(ECAT_TYPE.ECAT_TYPE_U16.value)
        pdo_data_size = c_uint32(sizeof(c_uint16))
        pdo_index = c_uint32(0x2180)
        val_range = c_uint16(3)
        pdo_range_sub_index = c_uint32(0x02)
        self.errCde = self.AdvMot.Acm2_DevWriteSDO(ring_no, id_type, sub_dev_pos, pdo_index, pdo_range_sub_index, pdo_type, pdo_data_size, byref(val_range))
        self.assertEqual(excepted_err, self.errCde)
        # Set AO(0) output enable
        pdo_enable_sub_index = c_uint32(0x01)
        val_enable = c_uint16(1)
        self.errCde = self.AdvMot.Acm2_DevWriteSDO(ring_no, id_type, sub_dev_pos, pdo_index, pdo_enable_sub_index, pdo_type, pdo_data_size, byref(val_enable))
        self.assertEqual(excepted_err, self.errCde)
        # AMAX-4820 default AO(0) ~ AO(3)
        ao_ch = c_uint32(0)
        # Set AO(0) as 10V
        data_type = c_uint(DAQ_DATA_TYPE.SCALED_DATA.value)
        ao_data = c_double(10)
        self.errCde = self.AdvMot.Acm2_ChSetAOData(ao_ch, data_type, ao_data)
        self.assertEqual(excepted_err, self.errCde)
        # Get AO(0) data
        get_data_ao = c_double(0)
        self.errCde = self.AdvMot.Acm2_ChGetAOData(ao_ch, data_type, byref(get_data_ao))
        self.assertEqual(excepted_err, self.errCde)
        self.assertAlmostEqual(ao_data.value, get_data_ao.value, delta=1.0)
        # Sleep for AI ready
        time.sleep(2)
        # Get AI(0) data
        get_data_ai = c_double(0)
        self.errCde = self.AdvMot.Acm2_ChGetAIData(ao_ch, data_type, byref(get_data_ai))
        self.assertEqual(excepted_err, self.errCde)
        self.assertAlmostEqual(ao_data.value, get_data_ai.value, delta=1.0, msg='{0} failed.'.format(self._testMethodName))

    def test_ReadCommErrCnt(self):
        excepted_err = c_uint32(ErrorCode2.FunctionNotSupport.value)
        # Ring as IO Ring
        ring_no = c_uint32(1)
        get_err_cnt = c_uint32(128)
        err_arr = (c_uint32 * get_err_cnt.value)()
        self.errCde = self.AdvMot.Acm2_DevReadSubDeviceCommErrCnt(ring_no, err_arr, byref(get_err_cnt))
        self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_SetCNTProperty(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        # Set encoder 0 property
        cnt_ch = c_uint32(0)
        # Set encoder(0) pulse in mode as CW/CCW.
        ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        get_val = c_double(0)
        self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch, ppt_arr, val_arr)
        self.assertEqual(excepted_err.value, self.errCde)
        self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch, ppt_arr, byref(get_val))
        self.assertEqual(excepted_err.value, self.errCde)
        self.assertEqual(val_arr.value, get_val.value)
        reset_cnt_data = c_double(0)
        # Reset encoder data as 0
        self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch, reset_cnt_data)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get encoder data
        get_cnt_data = c_double(0)
        self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
        self.assertEqual(excepted_err.value, self.errCde)
        self.assertEqual(reset_cnt_data.value, get_cnt_data.value)
    
    def test_SetCMPProperty(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        cmp_ch = c_uint32(0)
        # Set compare property, disable compare before setting.
        cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value)]
        trans_arr = (c_uint32 * len(cmp_set_arr))(*cmp_set_arr)
        val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value), c_double(COMPARE_LOGIC.CP_ACT_LOW.value)]
        trans_val = (c_double * len(val_arr))(*val_arr)
        err_buffer = (c_uint32 * len(val_arr))()
        self.errCde = self.AdvMot.Acm2_SetMultiProperty(cmp_ch, trans_arr, trans_val, len(val_arr), err_buffer)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get value
        get_val_arr = (c_double * len(val_arr))()
        self.errCde = self.AdvMot.Acm2_GetMultiProperty(cmp_ch, trans_arr, get_val_arr, len(val_arr), err_buffer)
        for i in range(len(val_arr)):
            self.assertEqual(val_arr[i].value, get_val_arr[i])
    
    def test_RunCMP_Pulse(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = c_uint32(ch)
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch, ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch, ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get value
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = [cnt_ch]
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)
            end_pos = c_double(3500)
            # Set compare data table
            # Compare DO behavior: ---ON---        ---OFF---        ---ON---       ---OFF---
            set_cmp_data_arr = [c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetCmpBufferData(cmp_ch, trans_cmp_data_arr, len(set_cmp_data_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch, reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            # Get encoder data
            get_cnt_data = c_double(0)
            while get_cnt_data.value < end_pos.value:
                time.sleep(0.1)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_RunCMP_Toggle(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = c_uint32(ch)
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch, ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch, ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get value
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = [cnt_ch]
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcTrigSel.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), 
                        c_double(LATCH_BUF_EDGE.LATCH_BUF_BOTH_EDGE.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)
            end_pos = c_double(3500)
            # Set compare data table
            # Compare DO behavior: ---ON---        ---OFF---        ---ON---       ---OFF---
            set_cmp_data_arr = [c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetCmpBufferData(cmp_ch, trans_cmp_data_arr, len(set_cmp_data_arr))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch, reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Get encoder data
            get_cnt_data = c_double(0)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_RunCMPAutoPulseWidth(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = c_uint32(ch)
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch, ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch, ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(val_arr.value, get_val.value)
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Get value
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
                self.assertEqual(val_arr[i].value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = [cnt_ch]
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, 0)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            end_check_pos = c_double(10500)
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)
            # Set compare data
            start_pos = c_double(1000)
            end_pos = c_double(10000)
            interval_pulse = c_double(500)
            self.errCde = self.AdvMot.Acm2_ChSetCmpAuto(cmp_ch, start_pos, end_pos, interval_pulse)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch, reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                                                    c_double(COMPARE_ENABLE.CMP_ENABLE.value))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Get encoder data
            get_cnt_data = c_double(0)
            while get_cnt_data.value < end_check_pos.value:
                time.sleep(0.1)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_RunCMPDiff(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = c_uint32(ch)
            # Local CMP Diff channel is 2
            cmp_ch = c_uint32(2)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            get_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch, ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch, ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(val_arr.value, get_val.value, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
            # Link local encoder/counter to compare
            cnt_arr = [cnt_ch]
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            # Reset Link connection
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, 0)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get value
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Set compare data table
            # Compare DO behavior: ---ON---        ---OFF---        ---ON---       ---OFF---
            set_cmp_data_arr = [c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetCmpBufferData(cmp_ch, trans_cmp_data_arr, len(set_cmp_data_arr))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch, reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Get encoder data
            get_cnt_data = c_double(0)
            end_pos = c_double(3500)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                for i in range(2):
                    tmp_ch = c_uint32(i)
                    self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                    # print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
                self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde)
            # Disable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_RunCMPLTC(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = c_uint32(ch)
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch, ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch, ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = [cnt_ch]
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000), c_double(0)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get CMP proerty
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Get linked local encoder/counter to latch
            get_obj_type = c_uint(0)
            get_linked_arr = (c_uint32 * 2)()
            get_linked_cnt = c_uint32(2)
            self.errCde = self.AdvMot.Acm2_ChGetLinkedLatchObject(ltc_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)
            # Set compare data
            set_cmp_data_arr = [c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetCmpBufferData(cmp_ch, trans_cmp_data_arr, len(set_cmp_data_arr))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch, reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value), 
                                                    c_double(COMPARE_ENABLE.CMP_ENABLE.value))
            self.assertEqual(excepted_err.value, self.errCde)
            # Get encoder data
            get_cnt_data = c_double(0)
            end_pos = c_double(3500)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                self.assertEqual(excepted_err.value, self.errCde)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(cnt_ch, byref(get_cnt_data))
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)

    def test_Set2CntInCMP(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = [c_uint32(0), c_uint32(1)]
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
                self.assertEqual(excepted_err.value, self.errCde)
                self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr.value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = cnt_ch
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            get_obj_type = c_uint(0)
            get_linked_arr = (c_uint32 * 2)()
            get_linked_cnt = c_uint32(2)
            # Get linked local encoder/counter to compare
            self.errCde = self.AdvMot.Acm2_ChGetLinkedCmpObject(cmp_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[CMP] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000), c_double(0)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get CMP proerty
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Get linked local encoder/counter to latch
            self.errCde = self.AdvMot.Acm2_ChGetLinkedLatchObject(ltc_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[LTC] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)

            # Set compare data
            set_cmp_data_arr = [c_double(100), c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(3000), 
                                c_double(100), c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(3000)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(cmp_ch, trans_cmp_data_arr, len(cnt_ch), c_uint32(int(len(set_cmp_data_arr) / len(cnt_ch))))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[i], reset_cnt_data)
                self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            # Get encoder data
            get_cnt_data = c_double(0)
            end_pos = c_double(3500)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                for i in range(len(cnt_ch)):
                    tmp_ch = c_uint32(i)
                    self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                    print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)

    def test_Set2CntInCMPWithDeviation(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = [c_uint32(0), c_uint32(1)]
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
                self.assertEqual(excepted_err.value, self.errCde)
                self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr.value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = cnt_ch
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            get_obj_type = c_uint(0)
            get_linked_arr = (c_uint32 * 2)()
            get_linked_cnt = c_uint32(2)
            # Get linked local encoder/counter to compare
            self.errCde = self.AdvMot.Acm2_ChGetLinkedCmpObject(cmp_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[CMP] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000), c_double(10)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get CMP proerty
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Get linked local encoder/counter to latch
            self.errCde = self.AdvMot.Acm2_ChGetLinkedLatchObject(ltc_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[LTC] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)

            # Set compare data
            set_cmp_data_arr = [c_double(100), c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(3000), 
                                c_double(110), c_double(510), c_double(1010), c_double(1510), c_double(2010), c_double(3010)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(cmp_ch, trans_cmp_data_arr, len(cnt_ch), c_uint32(int(len(set_cmp_data_arr) / len(cnt_ch))))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[i], reset_cnt_data)
                self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            # Get encoder data
            get_cnt_data = c_double(0)
            end_pos = c_double(3500)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                for i in range(len(cnt_ch)):
                    tmp_ch = c_uint32(i)
                    self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                    print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)


    def test_Set2CntInCMPWithDifferentTable(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = [c_uint32(0), c_uint32(1)]
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
                self.assertEqual(excepted_err.value, self.errCde)
                self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr.value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = cnt_ch
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            get_obj_type = c_uint(0)
            get_linked_arr = (c_uint32 * 2)()
            get_linked_cnt = c_uint32(2)
            # Get linked local encoder/counter to compare
            self.errCde = self.AdvMot.Acm2_ChGetLinkedCmpObject(cmp_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[CMP] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000), c_double(0)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get CMP proerty
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Get linked local encoder/counter to latch
            self.errCde = self.AdvMot.Acm2_ChGetLinkedLatchObject(ltc_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[LTC] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)

            # Set compare data
            set_cmp_data_arr = [c_double(100), c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(3000), 
                                c_double(110), c_double(510), c_double(1010), c_double(1510), c_double(2010), c_double(3010)]
            trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
            self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(cmp_ch, trans_cmp_data_arr, len(cnt_ch), c_uint32(int(len(set_cmp_data_arr) / len(cnt_ch))))
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data
            reset_cnt_data = c_double(0)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[0], reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
            reset_cnt_data_1 = c_double(10)
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[1], reset_cnt_data_1)
            self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            # Get encoder data
            get_cnt_data = c_double(0)
            end_pos = c_double(3500)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                for i in range(len(cnt_ch)):
                    tmp_ch = c_uint32(i)
                    self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                    print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)

    def test_2CntCMPLTCAuto(self):
        channel_arr = [0, 1]
        for ch in range(len(channel_arr)):
            excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
            cnt_ch = [c_uint32(0), c_uint32(1)]
            cmp_ch = c_uint32(ch)
            ltc_ch = c_uint32(ch)
            # Set encoder(0) pulse in mode as CW/CCW.
            ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
            val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
            get_val = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
                self.assertEqual(excepted_err.value, self.errCde)
                self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr.value, get_val.value)
            # Link local encoder/counter to compare
            cnt_arr = cnt_ch
            trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
            axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
            self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
            self.assertEqual(excepted_err.value, self.errCde)
            get_obj_type = c_uint(0)
            get_linked_arr = (c_uint32 * 2)()
            get_linked_cnt = c_uint32(2)
            # Get linked local encoder/counter to compare
            self.errCde = self.AdvMot.Acm2_ChGetLinkedCmpObject(cmp_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('[CMP] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
            for i in range(get_linked_cnt.value):
                print('Linked channel:{0}'.format(get_linked_arr[i]))
            # Set compare property, disable compare before setting.
            cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                        c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value)]
            val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                    c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value),
                    c_double(COMPARE_LOGIC.CP_ACT_LOW.value),
                    c_double(500000)]
            for i in range(len(cmp_set_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get CMP proerty
            get_val = c_double(0)
            for i in range(len(val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(val_arr[i].value, get_val.value)
            # Reset LTC buffer
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(ltc_ch)
            self.assertEqual(excepted_err.value, self.errCde)
            # Set LTC property
            ltc_set_ppt_arr = [c_uint32(PropertyID2.CFG_CH_DaqLtcMinDist.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value),
                            c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)]
            ltc_val_arr = [c_double(10), c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(COMPARE_ENABLE.CMP_ENABLE.value)]
            for i in range(len(ltc_set_ppt_arr)):
                self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, ltc_set_ppt_arr[i].value, ltc_val_arr[i])
                self.assertEqual(excepted_err.value, self.errCde)
            # Get LTC property
            get_val_ltc = c_double(0)
            for i in range(len(ltc_val_arr)):
                self.errCde = self.AdvMot.Acm2_GetProperty(ltc_ch, ltc_set_ppt_arr[i], byref(get_val_ltc))
                self.assertEqual(excepted_err.value, self.errCde)
                self.assertEqual(ltc_val_arr[i].value, get_val_ltc.value)
            # Set compare data
            start_pos = c_double(1000)
            end_pos = c_double(4000)
            interval_pulse = c_double(500)
            self.errCde = self.AdvMot.Acm2_ChSetCmpAuto(cmp_ch, start_pos, end_pos, interval_pulse)
            self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Reset encoder data as 0
            reset_cnt_data = c_double(0)
            for i in range(len(cnt_ch)):
                self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[i], reset_cnt_data)
                self.assertEqual(excepted_err.value, self.errCde)
            # Enable compare
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            # Get encoder data
            get_cnt_data = c_double(0)
            end_pos = c_double(3500)
            while get_cnt_data.value <= end_pos.value:
                time.sleep(0.1)
                for i in range(len(cnt_ch)):
                    tmp_ch = c_uint32(i)
                    self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                    # print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
            # Get LTC data
            get_ltc_buf_status = BUFFER_STATUS()
            act_data_cnt = c_uint32(128)
            get_ltc_data_arr = (c_double * act_data_cnt.value)()
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(ltc_ch, byref(get_ltc_buf_status))
            self.assertEqual(excepted_err.value, self.errCde)
            print('RemainCount:{0}, FreeSpaceCount:{1}'.format(get_ltc_buf_status.RemainCount, get_ltc_buf_status.FreeSpaceCount))
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(ltc_ch, get_ltc_data_arr, act_data_cnt, byref(act_data_cnt))
            self.assertEqual(excepted_err.value, self.errCde)
            print('act_data_cnt:{0}'.format(act_data_cnt.value))
            for i in range(act_data_cnt.value):
                print('get_ltc_data_arr[{0}]:{1}'.format(i, get_ltc_data_arr[i]))
            # Disable compare and latch
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_SetProperty(ltc_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                    c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
            self.assertEqual(excepted_err.value, self.errCde)

    def test_2CntCMPDiffAuto(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        cnt_ch = [c_uint32(0), c_uint32(1)]
        cmp_ch = c_uint32(2)
        # Set encoder(0) pulse in mode as CW/CCW.
        ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        get_val = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
        # Link local encoder/counter to compare
        cnt_arr = cnt_ch
        trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
        axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
        self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
        self.assertEqual(excepted_err.value, self.errCde)
        get_obj_type = c_uint(0)
        get_linked_arr = (c_uint32 * 2)()
        get_linked_cnt = c_uint32(2)
        # Get linked local encoder/counter to compare
        self.errCde = self.AdvMot.Acm2_ChGetLinkedCmpObject(cmp_ch, byref(get_obj_type), get_linked_arr, byref(get_linked_cnt))
        self.assertEqual(excepted_err.value, self.errCde)
        print('[CMP] Linked type:{0}, linked count:{1}'.format(get_obj_type.value, get_linked_cnt.value))
        for i in range(get_linked_cnt.value):
            print('Linked channel:{0}'.format(get_linked_arr[i]))
        # Set compare property, disable compare before setting.
        cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value)]
        val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                   c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value),
                   c_double(COMPARE_LOGIC.CP_ACT_LOW.value)]
        for i in range(len(cmp_set_arr)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
            self.assertEqual(excepted_err.value, self.errCde)
        # Get CMP proerty
        get_val = c_double(0)
        for i in range(len(val_arr)):
            self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr[i].value, get_val.value)
        # Set compare data
        start_pos = c_double(1000)
        end_pos = c_double(4500)
        interval_pulse = c_double(500)
        self.errCde = self.AdvMot.Acm2_ChSetCmpAuto(cmp_ch, start_pos, end_pos, interval_pulse)
        self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
        # Reset encoder data as 0
        reset_cnt_data = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[i], reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
        # Enable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get encoder data
        get_cnt_data = c_double(0)
        end_pos = c_double(3500)
        while get_cnt_data.value <= end_pos.value:
            time.sleep(0.1)
            for i in range(len(cnt_ch)):
                tmp_ch = c_uint32(i)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                # print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
        # Disable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                   c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)
    
    def test_2CntInCMPDiffTable(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        cnt_ch = [c_uint32(0), c_uint32(1)]
        cmp_ch = c_uint32(2)
        # Set encoder(0) pulse in mode as CW/CCW.
        ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        get_val = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
        # Link local encoder/counter to compare
        cnt_arr = cnt_ch
        trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
        axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
        self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
        self.assertEqual(excepted_err.value, self.errCde)
        # Set compare property, disable compare before setting.
        cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value)]
        val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                   c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value),
                   c_double(COMPARE_LOGIC.CP_ACT_LOW.value)]
        for i in range(len(cmp_set_arr)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
            self.assertEqual(excepted_err.value, self.errCde)
        # Get CMP proerty
        get_val = c_double(0)
        for i in range(len(val_arr)):
            self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr[i].value, get_val.value)
        # Set compare data
        set_cmp_data_arr = [c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000),
                            c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000)]
        trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
        self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(cmp_ch, trans_cmp_data_arr, len(cnt_ch), c_uint32(int(len(set_cmp_data_arr)/len(cnt_ch))))
        self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
        # Reset encoder data as 0
        reset_cnt_data = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[i], reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
        # Enable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get encoder data
        get_cnt_data = c_double(0)
        end_pos = c_double(3500)
        while get_cnt_data.value <= end_pos.value:
            time.sleep(0.1)
            for i in range(len(cnt_ch)):
                tmp_ch = c_uint32(i)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde)
                # print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
        # Disable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                   c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)
    
    def test_2CntInCMPDiffWithDifferentTable(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        cnt_ch = [c_uint32(0), c_uint32(1)]
        cmp_ch = c_uint32(2)
        # Set encoder(0) pulse in mode as CW/CCW.
        ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        get_val = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
        # Link local encoder/counter to compare
        cnt_arr = cnt_ch
        trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
        axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
        self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
        self.assertEqual(excepted_err.value, self.errCde)
        # Set compare property, disable compare before setting.
        cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)]
        val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                   c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value),
                   c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(0)]
        for i in range(len(cmp_set_arr)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
            self.assertEqual(excepted_err.value, self.errCde)
        # Get CMP proerty
        get_val = c_double(0)
        for i in range(len(val_arr)):
            self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr[i].value, get_val.value)
        # Set compare data
        set_cmp_data_arr = [c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(2500), c_double(3000),
                            c_double(510), c_double(1010), c_double(1510), c_double(2010), c_double(2510), c_double(3010)]
        trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
        self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(cmp_ch, trans_cmp_data_arr, len(cnt_ch), c_uint32(int(len(set_cmp_data_arr)/len(cnt_ch))))
        self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
        # Reset encoder data
        reset_cnt_data = c_double(0)
        reset_cnt_data_1 = c_double(10)
        self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[0], reset_cnt_data)
        self.assertEqual(excepted_err.value, self.errCde)
        self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[1], reset_cnt_data_1)
        self.assertEqual(excepted_err.value, self.errCde)
        # Enable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get encoder data
        get_cnt_data = c_double(0)
        end_pos = c_double(3500)
        while get_cnt_data.value <= end_pos.value:
            time.sleep(0.1)
            for i in range(len(cnt_ch)):
                tmp_ch = c_uint32(i)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde)
                # print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
        # Disable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                   c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)

    def test_2CntInCMPDiffWithDeviation(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        cnt_ch = [c_uint32(0), c_uint32(1)]
        cmp_ch = c_uint32(2)
        # Set encoder(0) pulse in mode as CW/CCW.
        ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        get_val = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
        # Link local encoder/counter to compare
        cnt_arr = cnt_ch
        trans_cnt_arr = (c_uint32 * len(cnt_arr))(*cnt_arr)
        axis_type = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
        self.errCde = self.AdvMot.Acm2_ChLinkCmpObject(cmp_ch, axis_type, trans_cnt_arr, len(cnt_arr))
        self.assertEqual(excepted_err.value, self.errCde)
        # Set compare property, disable compare before setting.
        cmp_set_arr = [c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value),
                       c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)]
        val_arr = [c_double(COMPARE_ENABLE.CMP_DISABLE.value),
                   c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value),
                   c_double(COMPARE_LOGIC.CP_ACT_LOW.value), c_double(10)]
        for i in range(len(cmp_set_arr)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, cmp_set_arr[i].value, val_arr[i])
            self.assertEqual(excepted_err.value, self.errCde)
        # Get CMP proerty
        get_val = c_double(0)
        for i in range(len(val_arr)):
            self.errCde = self.AdvMot.Acm2_GetProperty(cmp_ch, cmp_set_arr[i], byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr[i].value, get_val.value)
        # Set compare data
        set_cmp_data_arr = [c_double(100), c_double(500), c_double(1000), c_double(1500), c_double(2000), c_double(3000), 
                            c_double(110), c_double(510), c_double(1010), c_double(1510), c_double(2010), c_double(3010)]
        trans_cmp_data_arr = (c_double * len(set_cmp_data_arr))(*set_cmp_data_arr)
        self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(cmp_ch, trans_cmp_data_arr, len(cnt_ch), c_uint32(int(len(set_cmp_data_arr)/len(cnt_ch))))
        self.assertEqual(excepted_err.value, self.errCde, '{0} failed.'.format(self._testMethodName))
        # Reset encoder data as 0
        reset_cnt_data = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[i], reset_cnt_data)
            self.assertEqual(excepted_err.value, self.errCde)
        # Enable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value, c_double(COMPARE_ENABLE.CMP_ENABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get encoder data
        get_cnt_data = c_double(0)
        end_pos = c_double(3500)
        while get_cnt_data.value <= end_pos.value:
            time.sleep(0.1)
            for i in range(len(cnt_ch)):
                tmp_ch = c_uint32(i)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                self.assertEqual(excepted_err.value, self.errCde)
                # print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
        # Disable compare
        self.errCde = self.AdvMot.Acm2_SetProperty(cmp_ch, c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value).value,
                                                   c_double(COMPARE_ENABLE.CMP_DISABLE.value).value)
        self.assertEqual(excepted_err.value, self.errCde)

    def test_MPG(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        mpg_ch = c_uint32(0)
        mpg_mode_property = c_uint32(PropertyID2.CFG_CH_ExtPulseInMode.value)
        mpg_mode = c_uint32(PULSE_IN_MODE.AB_1X.value)
        # Set MPG property
        self.errCde = self.AdvMot.Acm2_SetProperty(mpg_ch, mpg_mode_property.value, mpg_mode.value)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get MPG data
        get_ext_data = c_double(0)
        self.errCde = self.AdvMot.Acm2_ChGetExtDriveData(mpg_ch, byref(get_ext_data))
        self.assertEqual(excepted_err.value, self.errCde)
        time.sleep(3)
        print('MPG data:', get_ext_data.value)
  
    def test_MotionDoneEvent(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        ax_id = c_uint32(0)
        abs_mode = c_uint(ABS_MODE.MOVE_REL.value)
        distance = c_double(10000)
        ax_motion_cnt = c_uint32(0)
        # Set callback function, enable event
        self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.AXIS_MOTION_DONE.value), EvtAxMotionDone)
        self.assertEqual(excepted_err.value, self.errCde)
        # Move
        for i in range(1):
            self.errCde = self.AdvMot.Acm2_AxPTP(ax_id, abs_mode, distance)
            self.assertEqual(excepted_err.value, self.errCde)
            # Check status
            while self.state.value != AXIS_STATE.STA_AX_READY.value:
                time.sleep(1)
                self.test_GetAxState()
        time.sleep(1)
        print('AX:{0} is done, event cnt is:{1}'.format(ax_id.value, ax_motion_cnt.value))
        # self.assertEqual(2, ax_motion_cnt.value)
        # Remove callback function, disable event
        # self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.EVENT_DISABLE.value), EmptyFunction)
        self.assertEqual(excepted_err.value, self.errCde)

    def test_MotionDoneEvent_MultiThreads(self):
        def unitAxPTP(axis):
            print('[unitAxPTP] axis:{0}'.format(axis))
            ax_id = c_uint32(axis)
            state_type = c_uint(AXIS_STATUS_TYPE.AXIS_STATE.value)
            abs_mode = c_uint(ABS_MODE.MOVE_REL.value)
            distance = c_double(1000)
            get_state = c_uint32(0)
            speed_profile = SPEED_PROFILE_PRM()
            speed_profile.FH = c_double(3000)
            speed_profile.FL = c_double(1000)
            speed_profile.Acc = c_double(10000)
            speed_profile.Dec = c_double(1000)
            AdvCmnAPI_CM2.Acm2_AxSetSpeedProfile(ax_id, speed_profile)
            AdvCmnAPI_CM2.Acm2_AxPTP(ax_id, abs_mode, distance)
            AdvCmnAPI_CM2.Acm2_AxGetState(ax_id, state_type, byref(get_state))
            while get_state.value != AXIS_STATE.STA_AX_READY.value:
                time.sleep(1)
                AdvCmnAPI_CM2.Acm2_AxGetState(ax_id, state_type, byref(get_state))

        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        # Set callback function, enable event
        for i in range(5):
            ax_id = c_uint32(i)
            ax_evt_cnt[i].value = 0
            if i == 0:
                self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.AXIS_MOTION_DONE.value), EvtAxMotionDone_multi_0)
                self.assertEqual(excepted_err.value, self.errCde)
            elif i == 1:
                self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.AXIS_MOTION_DONE.value), EvtAxMotionDone_multi_1)
                self.assertEqual(excepted_err.value, self.errCde)
            elif i == 2:
                self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.AXIS_MOTION_DONE.value), EvtAxMotionDone_multi_2)
                self.assertEqual(excepted_err.value, self.errCde)
            elif i == 3:
                self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.AXIS_MOTION_DONE.value), EvtAxMotionDone_multi_3)
                self.assertEqual(excepted_err.value, self.errCde)
            elif i == 4:
                self.errCde = self.AdvMot.Acm2_EnableCallBackFuncForOneEvent(ax_id, c_int(ADV_EVENT_SUBSCRIBE.AXIS_MOTION_DONE.value), EvtAxMotionDone_multi_4)
                self.assertEqual(excepted_err.value, self.errCde)
        time.sleep(1)
        # Move
        threads = []
        for j in range(5):
            thread = threading.Thread(target=unitAxPTP, args=(j,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        time.sleep(2)

    def test_SQATest(self):
        excepted_err = c_uint32(ErrorCode2.SUCCESS.value)
        cnt_ch = [c_uint32(0), c_uint32(1)]
        # Set encoder(0) pulse in mode as CW/CCW.
        ppt_arr = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        val_arr = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        get_val = c_double(0)
        for i in range(len(cnt_ch)):
            self.errCde = self.AdvMot.Acm2_SetProperty(cnt_ch[i], ppt_arr, val_arr)
            self.assertEqual(excepted_err.value, self.errCde)
            self.errCde = self.AdvMot.Acm2_GetProperty(cnt_ch[i], ppt_arr, byref(get_val))
            self.assertEqual(excepted_err.value, self.errCde)
            self.assertEqual(val_arr.value, get_val.value)
        # Reset encoder data as 0
        reset_cnt_data = c_double(0)
        self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[0], reset_cnt_data)
        self.assertEqual(excepted_err.value, self.errCde)
        reset_cnt_data_1 = c_double(10)
        self.errCde = self.AdvMot.Acm2_ChSetCntData(cnt_ch[1], reset_cnt_data_1)
        self.assertEqual(excepted_err.value, self.errCde)
        # Get encoder data
        get_cnt_data = c_double(0)
        end_pos = c_double(3500)
        while get_cnt_data.value <= end_pos.value:
            time.sleep(0.1)
            for i in range(len(cnt_ch)):
                tmp_ch = c_uint32(i)
                self.errCde = self.AdvMot.Acm2_ChGetCntData(tmp_ch, byref(get_cnt_data))
                print('[{0}]get_cnt_data:{1}'.format(i, get_cnt_data.value))
        
def DownloadENISuite():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_LoadENI']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetMDevice():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_GetMDevice']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def DeviceClose():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_DevClose']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def AxMoveContinue():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_MoveContinue', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

# def ExportMappingTable():
#     tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_DevExportMappingTable']
#     suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
#     return suite

# def ImportMappingTable():
#     tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_DevImportMappingTable']
#     suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
#     return suite

def AxPTP_Check():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_AxPTP', 'test_AxGetPosition', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def DeviceDO():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_SetDeviceDIOProperty', 'test_GetDeviceDIOProperty', 'test_SetDeviceDO_ON']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GroupCreateCheck():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_RemoveGroup', 'test_CreatGroup', 'test_CheckGroupAxes', 'test_RemoveGroup']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetAllError():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_GetLastError_Device', 'test_GetLastError_AXIS', 'test_GetLastError_Group']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetAxis0SpeedLimit():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_SetMultiPropertyAndCheck_AxisSpeed', 'test_GetLastError_AXIS']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetAxis0SpeedWithProfile():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_SetAxSpeedInfoAndCheck', 'test_GetLastError_AXIS']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def PVTTable():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_PVTTable', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def PTTable():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_PTTable', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Gear0And1():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Gear', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Gantry0And1():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Gantry', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMoveLineRel():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_GpLine', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove2DArcCW():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2DArc', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove2DArcCW3P():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2DArc3P', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove2DArcCWAngle():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2DArcAngle', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove3DArcCW():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_3DArcCenter', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove3DArcCWNormVec():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_3DArcNormVec', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove3DArcCW3P():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Gp3DArc3P', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMove3DArcCW3P():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_3DArcAngle', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMoveHelixCenter():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'GpHelixCenter', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMoveHelix3P():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Helix3P', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMoveHelixAngle():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_HelixAngle', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpMoveLinePauseAndResume():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_GpLinePauseAndResume', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpChangeVelWhenMove():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_GpStop', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpAddLoadPath():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_GpAddPath', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GpLoadPath():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_GpLoadPath', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def ECATLoadConnect5074_5057SO():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetAndCheck5057SO():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_Set5057SODO', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetAndCheck5057SOByte():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'Set5057DOByByte', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetSubdeviceInfo():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_GetSubdeviceInfo', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetMaindeviceInfo():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_GetMainDeviceInfo', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetValueByPDO():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_WriteAndReadByPDO', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetAOGetAI():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_Set4820AOData', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetCommuError():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_LoadConnect5074And5057SO', 'test_ReadCommErrCnt', 'test_DisConnectAll', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetCntProperty():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_SetCNTProperty', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite 

def SetCMPProperty():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_SetCMPProperty', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMPCNTPulse():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_RunCMP_Pulse', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMPCNTToggle():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_RunCMP_Toggle', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMPAutoPulse():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_RunCMPAutoPulseWidth', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def EventMotionDone():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_MotionDoneEvent', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SQATest():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_SQATest']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def MotionDoneEventMultiThreads():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_MotionDoneEvent_MultiThreads', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMPDiff():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_RunCMPDiff', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMPLTC():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_RunCMPLTC', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntLinkedCMP():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Set2CntInCMP', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntLinkedCMPDifferentTable():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Set2CntInCMPWithDifferentTable', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntLinkedCMPDeviation():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_Set2CntInCMPWithDeviation', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntLinkedCMPDiff():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2CntInCMPDiffTable', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntLinkedCMPDiffWithDifferentTable():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2CntInCMPDiffWithDifferentTable', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntLinkedCMPDiffWithDeviation():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2CntInCMPDiffWithDeviation', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite    

def Run2CntCMPLTCAuto():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2CntCMPLTCAuto', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Run2CntCMPDiffAuto():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_2CntCMPDiffAuto', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetExtData():
    tests = ['test_GetAvailableDevs', 'test_Initialize', 'test_ResetAll', 'test_MPG', 'test_ResetAll']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def JustGetAvailableDevices():
    tests = ['test_GetAvailableDevs']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

if __name__ == '__main__':
    # Test all case without order
    # unittest.main()
    # Test case with self-defined order
    runner = unittest.TextTestRunner()
    # get_available_devs = runner.run(JustGetAvailableDevices())
    # get_device = runner.run(GetMDevice())
    # ax_ptp = runner.run(AxPTP_Check())
    # device_do = runner.run(DeviceDO())
    # gp_create = runner.run(GroupCreateCheck())
    # get_all_error = runner.run(GetAllError())
    # ax_move_continue = runner.run(AxMoveContinue())
    # set_ax_speed_limit = runner.run(SetAxis0SpeedLimit())
    # set_ax_profile = runner.run(SetAxis0SpeedWithProfile())
    # pvt_table = runner.run(PVTTable())
    # pt_table = runner.run(PTTable())
    # gear_0_1 = runner.run(Gear0And1())
    # gantry_0_1 = runner.run(Gantry0And1())
    # gp_move_line = runner.run(GpMoveLineRel())
    # gp_move_2D_arc = runner.run(GpMove2DArcCW())
    # gp_move_2D_3P = runner.run(GpMove2DArcCW3P())
    # gp_2D_angle = runner.run(GpMove2DArcCWAngle())
    # gp_3D_arc = runner.run(GpMove3DArcCW())
    # gp_3D_norm_vec = runner.run(GpMove3DArcCWNormVec())
    # gp_3D_3P = runner.run(GpMove3DArcCW3P())
    # gp_helix_center = runner.run(GpMoveHelixCenter())
    # gp_helix_3P = runner.run(GpMoveHelix3P())
    # gp_helix_angle = runner.run(GpMoveHelixAngle())
    # gp_line_pause_resume = runner.run(GpMoveLinePauseAndResume())
    # set_byte_5057SO = runner.run(SetAndCheck5057SOByte())
    # change_vel_when_move = runner.run(GpChangeVelWhenMove())
    # gp_add_load_path = runner.run(GpAddLoadPath())
    # gp_load_path = runner.run(GpLoadPath())
    # load_connect = runner.run(ECATLoadConnect5074_5057SO())
    # set_5057SO = runner.run(SetAndCheck5057SO())
    # get_subdevice_info = runner.run(GetSubdeviceInfo())
    # get_main_device_info = runner.run(GetMaindeviceInfo())
    # set_pdo_val = runner.run(SetValueByPDO())
    # set_ao_get_ai = runner.run(SetAOGetAI())
    # get_commu_error = runner.run(GetCommuError())
    # set_cnt_property = runner.run(SetCntProperty())
    # set_cmp_property = runner.run(SetCMPProperty())
    # run_cmp_cnt_pulse = runner.run(RunCMPCNTPulse())
    run_cmp_diff = runner.run(RunCMPDiff())
    # run_cmp_auto_pulse = runner.run(RunCMPAutoPulse())
    # run_cmp_cnt_toggle = runner.run(RunCMPCNTToggle())
    # run_cmp_ltc = runner.run(RunCMPLTC())
    # run_2_cnt_linked_cmp = runner.run(Run2CntLinkedCMP())
    # run_2_cnt_linked_cmp_diff = runner.run(Run2CntLinkedCMPDiff())
    # run_2_cnt_cmp_ltc_auto = runner.run(Run2CntCMPLTCAuto())
    # run_2_cnt_cmp_diff_atuo = runner.run(Run2CntCMPDiffAuto())
    # run_2_cnt_cmp_diff_with_deviation = runner.run(Run2CntLinkedCMPDiffWithDeviation())
    # run_2_cnt_cmp_diff_with_different_table = runner.run(Run2CntLinkedCMPDiffWithDifferentTable())
    # run_2_cnt_cmp_ltc_different_table = runner.run(Run2CntLinkedCMPDifferentTable())
    # run_2_cnt_cmp_ltc_deviation = runner.run(Run2CntLinkedCMPDeviation())
    # evt_motion_done = runner.run(EventMotionDone())
    # sqa_test = runner.run(SQATest())
    # evt_motion_multi = runner.run(MotionDoneEventMultiThreads())
    # get_ext_data = runner.run(GetExtData())
    # total_run_arr = [get_available_devs, get_device, export_mapping_table, import_mapping_table, ax_ptp,
    #                  device_do, gp_create, get_all_error, ax_move_continue, set_ax_speed_limit,
    #                  set_ax_profile, pvt_table, pt_table, gear_0_1, gantry_0_1,
    #                  gp_move_line, gp_move_2D_arc, gp_move_2D_3P, gp_2D_angle, gp_3D_arc,
    #                  gp_3D_norm_vec, gp_3D_3P, gp_helix_center, gp_helix_3P, gp_helix_angle,
    #                  gp_line_pause_resume, set_byte_5057SO, change_vel_when_move, gp_add_load_path, gp_load_path,
    #                  load_connect, set_5057SO, get_subdevice_info, get_main_device_info, set_pdo_val,
    #                  set_ao_get_ai, get_commu_error, set_cnt_property, run_cmp_ltc, get_ext_data,
    #                  evt_motion_multi, evt_motion_done, run_cmp_diff, run_cmp_auto_pulse, run_cmp_cnt_pulse,
    #                  run_cmp_cnt_toggle, set_cmp_property]
    # failed_cnt = 0
    # total_cnt = 0
    # for i in range(len(total_run_arr)):
    #     failed_cnt += len(total_run_arr[i].failures)
    #     total_cnt += total_run_arr[i].testsRun
    # print('=========== Test result ===========')
    # print('Total test:{0}, failures:{1}'.format(total_cnt, failed_cnt))
    # print('=========== End of unit test ===========')
