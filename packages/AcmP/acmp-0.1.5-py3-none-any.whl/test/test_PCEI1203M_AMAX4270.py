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

global_ltc_mode = 0
global_cmp_mode = 0
global_cmp_delay = False

class AdvCmnAPI_Test(unittest.TestCase):
    def setUp(self):
        self.maxEnt = 10
        self.devlist = (DEVLIST*self.maxEnt)()
        self.outEnt = c_uint32(0)
        self.errCde = 0
        # IO Ring connect to AMAX-4270
        self.ringNo = c_uint32(0)
        self.state = c_uint32(16)
        self.AdvMot = AdvCmnAPI_CM2
        self.gpid = c_uint32(0)
        # PDO
        self.pdoControlWordIdx = [c_uint32(0x7014), c_uint32(0x7114), c_uint32(0x7214), c_uint32(0x7314)]
        self.pdoControlWordSubIdx = c_uint32(0x11)
        # CNT
        self.cntChLocal = [c_uint32(0), c_uint32(1)]
        self.cntCh4270 = [c_uint32(2), c_uint32(3), c_uint32(4), c_uint32(5)]
        self.cnt_ch0_ch1 = [c_uint32(2), c_uint32(3)]
        self.cnt_ch0_ch2 = [c_uint32(2), c_uint32(4)]
        self.cnt_ch0_ch2_ch3 = [c_uint32(2), c_uint32(4), c_uint32(5)]
        # Local CMP, ch 2 as diff CMP
        self.cmpChLocal = [c_uint32(0), c_uint32(1), c_uint32(2)]
        self.cmpCh4270 = [c_uint32(3), c_uint32(4), c_uint32(5), c_uint32(6)]
        self.cmp_ch0_ch1 = [c_uint32(3), c_uint32(4)]
        self.cmp_ch0_ch2 = [c_uint32(3), c_uint32(5)]
        self.cmp_ch0_ch2_ch3 = [c_uint32(3), c_uint32(5), c_uint32(6)]
        self.delay_cmp_ch1_ch3 = [c_uint32(4), c_uint32(6)]
        # LTC
        self.ltcChLocal = [c_uint32(0), c_uint32(1)]
        self.ltcCh4270 = [c_uint32(2), c_uint32(3), c_uint32(4), c_uint32(5)]
        self.ltc_ch0_ch1 = [c_uint32(2), c_uint32(3)]
        self.ltc_ch0_ch2 = [c_uint32(2), c_uint32(4)]
        self.ltc_ch0_ch1_ch2 = [c_uint32(2), c_uint32(3), c_uint32(4)]
        self.subDevicePos = c_uint32(0)
        self.ltcLinkedCnt = c_uint32(0)
        self.cmpLinkedCnt = c_uint32(0)
        gp_arr = [c_uint32(0), c_uint32(1)]
        self.axis_array = (c_uint32 * len(gp_arr))(*gp_arr)
        if global_cmp_delay:
            self.delta = 100
        elif global_cmp_mode == 2 or global_cmp_mode == 3:
            self.delta = 500
        else:
            self.delta = 20
        if global_ltc_mode == 0 and global_cmp_mode == 0:
            self.ltcLinkedCnt = c_uint32(1)
            self.cmpLinkedCnt = c_uint32(1)
            self.LTCCh = self.ltcCh4270
            self.CMPCh = self.cmpCh4270
            # self.CMPCh = [c_uint32(3), c_uint32(4), c_uint32(5), c_uint32(6)]
            self.CNTCh = self.cnt_ch0_ch2
            # eni file can be create by the Utility
            if os.name == 'nt':
                self.eni_path = b'test\\4270_eni_LTCmode0CMPmode0.xml'
            else:
                self.eni_path = b'test/4270_eni_LTCmode0CMPmode0.xml'
        elif global_ltc_mode == 0 and global_cmp_mode == 1:
            self.ltcLinkedCnt = c_uint32(1)
            self.cmpLinkedCnt = c_uint32(1)
            if (global_cmp_delay):
                self.LTCCh = self.ltcCh4270
            else:
                self.LTCCh = self.ltcCh4270
            self.CMPCh = self.cmp_ch0_ch2
            self.CNTCh = self.cnt_ch0_ch2
            if os.name == 'nt':
                self.eni_path = b'test\\4270_eni_LTCmode0CMPmode1.xml'
            else:
                self.eni_path = b'test/4270_eni_LTCmode0CMPmode1.xml'
        elif global_ltc_mode == 0 and global_cmp_mode == 2:
            self.ltcLinkedCnt = c_uint32(1)
            self.cmpLinkedCnt = c_uint32(2)
            self.LTCCh = self.ltcCh4270
            self.CMPCh = self.cmp_ch0_ch2
            self.CNTCh = self.cnt_ch0_ch2
            if os.name == 'nt':
                self.eni_path = b'test\\4270_eni_LTCmode0CMPmode2.xml'
            else:
                self.eni_path = b'test/4270_eni_LTCmode0CMPmode2.xml'
        elif global_ltc_mode == 0 and global_cmp_mode == 3:
            self.ltcLinkedCnt = c_uint32(1)
            self.cmpLinkedCnt = c_uint32(1)
            self.LTCCh = self.ltcCh4270
            self.CNTCh = self.cnt_ch0_ch2_ch3
            self.CMPCh = self.cmp_ch0_ch2_ch3
            if os.name == 'nt':
                self.eni_path = b'test\\4270_eni_LTCmode0CMPmode3.xml'
            else:
                self.eni_path = b'test/4270_eni_LTCmode0CMPmode3.xml'
        elif global_ltc_mode == 1 and global_cmp_mode == 0:
            self.ltcLinkedCnt = c_uint32(4)
            self.cmpLinkedCnt = c_uint32(1)
            self.LTCCh = self.ltc_ch0_ch1
            self.CMPCh = self.cmp_ch0_ch1
            self.CNTCh = self.cnt_ch0_ch1
            if os.name == 'nt':
                self.eni_path = b'test\\4270_eni_LTCmode1CMPmode0.xml'
            else:
                self.eni_path = b'test/4270_eni_LTCmode1CMPmode0.xml'
        elif global_ltc_mode == 1 and global_cmp_mode == 1:
            self.ltcLinkedCnt = c_uint32(4)
            self.cmpLinkedCnt = c_uint32(1)
            self.LTCCh = self.ltc_ch0_ch1
            self.CMPCh = self.cmp_ch0_ch2
            self.CNTCh = self.cnt_ch0_ch2
            if os.name == 'nt':
                self.eni_path = b'test\\4270_eni_LTCmode1CMPmode1.xml'
            else:
                self.eni_path = b'test/4270_eni_LTCmode1CMPmode1.xml'
    
    def tearDown(self):
        self.errCde = 0
    
    def test_Initial(self):
        # your switch number on board as device number
        excepted_err = 0
        self.errCde = self.AdvMot.Acm2_GetAvailableDevs(self.devlist, self.maxEnt, byref(self.outEnt))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        for i in range(self.outEnt.value):
            print('Dev number:{0:x}'.format(self.devlist[i].dwDeviceNum))
        self.errCde = self.AdvMot.Acm2_DevInitialize()
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_DisConnect(self):
        excepted_err = 0
        getState = c_uint32(SUB_DEV_STATE.EC_SLAVE_STATE_INIT.value)
        self.errCde = self.AdvMot.Acm2_DevDisConnect(self.ringNo)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        time.sleep(2)
        self.errCde = self.AdvMot.Acm2_DevGetSubDeviceStates(self.ringNo, ECAT_ID_TYPE.SUBDEVICE_POS.value, self.subDevicePos, byref(getState))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        self.assertEqual(SUB_DEV_STATE.EC_SLAVE_STATE_PREOP.value, getState.value, 'Fail to connect. State:{0}'.format(getState.value))

    def test_Conntect(self):
        excepted_err = 0
        getState = c_uint32(SUB_DEV_STATE.EC_SLAVE_STATE_INIT.value)
        self.errCde = self.AdvMot.Acm2_DevConnect(self.ringNo)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        time.sleep(2)
        self.errCde = self.AdvMot.Acm2_DevGetSubDeviceStates(self.ringNo, ECAT_ID_TYPE.SUBDEVICE_POS.value, self.subDevicePos, byref(getState))
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        self.assertEqual(SUB_DEV_STATE.EC_SLAVE_STATE_OP.value, getState.value, 'Fail to connect. State:{0}'.format(getState.value))

    def test_Load4270ENI(self):
        excepted_err = 0
        print(self.eni_path)
        self.errCde = self.AdvMot.Acm2_DevLoadENI(self.ringNo, self.eni_path)
        self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Reset4270Counter(self):
        excepted_err = 0
        resetCnt = c_double(0)
        for idx in range(len(self.cntCh4270)):
            print('---** Reset counter{0} data as 0 by CM2 API **---'.format(self.cntCh4270[idx].value))
            self.errCde = self.AdvMot.Acm2_ChSetCntData(self.cntCh4270[idx], resetCnt)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
    
    def test_SetCntPulseMode(self):
        excepted_err = 0
        cntPulseMode = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMode.value)
        cntPulseLogic = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInLogic.value)
        cntMaxFreq = c_uint32(PropertyID2.CFG_CH_DaqCntPulseInMaxFreq.value)
        cntPulseVal = c_double(PULSE_IN_MODE.I_CW_CCW.value)
        cntPulseLogicVal = c_double(PULSE_IN_LOGIC.NO_INV_DIR.value)
        cntMaxFreqVal = c_double(0)
        getVal = c_double(0)
        for idx in range(len(self.cntCh4270)):
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cntCh4270[idx], cntPulseMode, cntPulseVal)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cntCh4270[idx], cntPulseMode, byref(getVal))
            # print('Cnt ch:{0}, PulseInMode:{1}'.format(self.cntCh4270[idx].value, getVal.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(cntPulseVal.value, getVal.value, 'Set pulse mode failed! Ch:{2} set {0}, get {1}'.format(cntPulseVal.value, getVal.value, self.cntCh4270[idx].value))
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cntCh4270[idx], cntPulseLogic, cntPulseLogicVal)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cntCh4270[idx], cntPulseLogic, byref(getVal))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(cntPulseLogicVal.value, getVal.value, 'Set pulse logic failed! Ch:{2} set {0}, get {1}'.format(cntPulseLogicVal.value, getVal.value, self.cntCh4270[idx].value))
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cntCh4270[idx], cntMaxFreq, cntMaxFreqVal)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cntCh4270[idx], cntMaxFreq, byref(getVal))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(cntMaxFreqVal.value, getVal.value, 'Set pulse max freq failed! Ch:{2} set {0}, get {1}'.format(cntMaxFreqVal.value, getVal.value, self.cntCh4270[idx].value))
    
    def test_Get4270CounterData(self):
        excepted_err = 0
        getCnt = c_double(0)
        print('---** Get counter data by CM2 API **---')
        for idx in range(len(self.cntCh4270)):
            self.errCde = self.AdvMot.Acm2_ChGetCntData(self.cntCh4270[idx], byref(getCnt))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            print('Cnt ch:{0}, val:{1}'.format(self.cntCh4270[idx].value, getCnt.value))
        cntPDOidx = [c_uint32(0x6000), c_uint32(0x6100), c_uint32(0x6200), c_uint32(0x6300)]
        cntPDOsubIdx = c_uint32(0x11)
        getPDOData = c_int32(0)
        print('---** Get counter data by PDO **---')
        for idx in range(len(cntPDOidx)):
            self.errCde = self.AdvMot.Acm2_DevReadPDO(self.ringNo, ECAT_ID_TYPE.SUBDEVICE_POS.value, self.subDevicePos, cntPDOidx[idx], cntPDOsubIdx, ECAT_TYPE.ECAT_TYPE_I32.value, c_uint32(sizeof(c_int32)), byref(getPDOData))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            print('PDO:0x{0:x}, val:{1}'.format(cntPDOidx[idx].value, getPDOData.value))
    
    def test_GetLocalCounterData(self):
        excepted_err = 0
        getCnt = c_double(0)
        for idx in range(len(self.cntChLocal)):
            self.errCde = self.AdvMot.Acm2_ChGetCntData(self.cntChLocal[idx], byref(getCnt))
            print('Cnt ch:{0}, val:{1}'.format(self.cntChLocal[idx].value, getCnt.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Set4270CmpSoftTrigger(self):
        excepted_err = 0
        cmpOutMode = c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value)
        cmpOutEnable = c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value)
        cmpOutDelay = c_uint32(PropertyID2.CFG_CH_DaqCmpDoDelay.value)
        toggle = c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value)
        getSettingValue = c_double(0)
        on = c_uint(DO_ONOFF.DO_ON.value)
        off = c_uint(DO_ONOFF.DO_OFF.value)
        delay0 = c_double(0)
        for idx in range(len(self.cmpCh4270)):
            print('--- Set cmp ch:{0} property---'.format(self.cmpCh4270[idx].value,))
            # Disable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx], cmpOutEnable, c_double(DO_ONOFF.DO_OFF.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx], cmpOutEnable, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(off.value, getSettingValue.value, 'Set enable failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpCh4270[idx].value))
            # Set CMP output mode as toggle
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx], cmpOutMode, toggle)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx], cmpOutMode, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(toggle.value, getSettingValue.value, 'Set pulse mode failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpCh4270[idx].value))
            # Set CMP output delay 0
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx], cmpOutDelay, delay0)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx], cmpOutDelay, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(delay0.value, getSettingValue.value, 'Set delay failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpCh4270[idx].value))
            # Enable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx], cmpOutEnable, c_double(DO_ONOFF.DO_ON.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx], cmpOutEnable, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(on.value, getSettingValue.value, 'Set enable failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpCh4270[idx].value))
        for idx in range(len(self.cmpCh4270)):
            # Force trigger CMP ON
            self.errCde = self.AdvMot.Acm2_ChSetCmpOut(self.cmpCh4270[idx], on)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Let LED light on for 1 second
            time.sleep(1)
            # Force trigger CMP OFF
            self.errCde = self.AdvMot.Acm2_ChSetCmpOut(self.cmpCh4270[idx], off)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            time.sleep(1)
        for idx in range(len(self.cmpCh4270)):
            # Disable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx], cmpOutEnable, c_double(DO_ONOFF.DO_OFF.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx], cmpOutEnable, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(off.value, getSettingValue.value, 'Set enable failed! Ch:{2} set {0}, get {1}'.format(off.value, getSettingValue.value, self.cmpCh4270[idx].value))

    def test_SetLocalCmpSoftTrigger(self):
        excepted_err = 0
        cmpFuncMode = c_uint32(PropertyID2.CFG_CH_DaqDoFuncSelect.value)
        cmpOutMode = c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value)
        cmpOutEnable = c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value)
        toggle = c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value)
        getSettingValue = c_double(0)
        cmpDo = c_double(DEVICE_DO_MODE.ENABLE_GENERAL_DO.value)
        on = c_uint(DO_ONOFF.DO_ON.value)
        off = c_uint(DO_ONOFF.DO_OFF.value)
        for idx in range(len(self.cmpChLocal)):
            # Disable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpChLocal[idx], cmpOutEnable, c_double(DO_ONOFF.DO_OFF.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpChLocal[idx], cmpOutEnable, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(off.value, getSettingValue.value, 'Set enable failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpChLocal[idx].value))
            # Set local CMP output as comparator
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpChLocal[idx], cmpFuncMode, cmpDo)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpChLocal[idx], cmpFuncMode, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(cmpDo.value, getSettingValue.value, 'Set enable failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpChLocal[idx].value))
            # Set CMP output mode as toggle
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpChLocal[idx], cmpOutMode, toggle)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpChLocal[idx], cmpOutMode, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(toggle.value, getSettingValue.value, 'Set pulse mode failed! Ch:{2} set {0}, get {1}'.format(toggle.value, getSettingValue.value, self.cmpChLocal[idx].value))
            # Force trigger CMP ON
            self.errCde = self.AdvMot.Acm2_ChSetCmpOut(self.cmpChLocal[idx], on)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Let LED light on for 1 second
            time.sleep(1)
            # Force trigger CMP OFF
            self.errCde = self.AdvMot.Acm2_ChSetCmpOut(self.cmpChLocal[idx], off)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Disable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpChLocal[idx], cmpOutEnable, c_double(DO_ONOFF.DO_OFF.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpChLocal[idx], cmpOutEnable, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(off.value, getSettingValue.value, 'Set enable failed! Ch:{2} set {0}, get {1}'.format(off.value, getSettingValue.value, self.cmpChLocal[idx].value))

    def test_Get4270CMPLinkedCnt(self):
        excepted_err = 0
        objType = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
        arrElement = c_uint32(2)
        objArr = (c_uint32 * 2)()
        for idx in range(len(self.cmpCh4270)):
            self.errCde = self.AdvMot.Acm2_ChGetLinkedCmpObject(self.cmpCh4270[idx].value, byref(objType), objArr, byref(arrElement))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            print('CMP {0} linked to CNT {1}'.format(self.cmpCh4270[idx].value, objArr[0]))

    def test_Get4270LTCLinkedCnt(self):
        excepted_err = 0
        objType = c_uint(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value)
        arrElement = c_uint32(4)
        objArr = (c_uint32 * 4)()
        for idx in range(len(self.LTCCh)):
            self.errCde = self.AdvMot.Acm2_ChGetLinkedLatchObject(self.LTCCh[idx].value, byref(objType), objArr, byref(arrElement))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            for i in range(arrElement.value):
                print('LTC {0} linked to CNT {1}'.format(self.LTCCh[idx].value, objArr[i]))
    
    def test_Enable4270CMPLTC(self):
        excepted_err = 0
        cmpOutEnable = c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value)
        ltcEnable = c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)
        enable = c_double(COMPARE_ENABLE.CMP_ENABLE.value)
        getSettingValue = c_double(0)
        for idx in range(len(self.cmpCh4270)):
            # Enable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpOutEnable, enable)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpOutEnable, byref(getSettingValue))
            self.assertEqual(enable.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqCmpDoEnable.name, enable.value, getSettingValue.value, self.cmpCh4270[idx].value))
        for idx in range(len(self.LTCCh)):
            # Enable LTC
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcEnable, enable)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcEnable, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(enable.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
               PropertyID2.CFG_CH_DaqLtcEnable.name, enable.value, getSettingValue.value, self.LTCCh[idx].value))

    def test_Reset4270CMPLTCData(self):
        excepted_err = 0
        for idx in range(len(self.CMPCh)):
            # Reset CMP data
            self.errCde = self.AdvMot.Acm2_ChResetCmpData(self.cmpCh4270[idx].value)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        for idx in range(len(self.LTCCh)):
            # Reset LTC data
            self.errCde = self.AdvMot.Acm2_ChResetLatchBuffer(self.LTCCh[idx].value)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))

    def test_Disable4270CMPLTC(self):
        excepted_err = 0
        cmpOutEnable = c_uint32(PropertyID2.CFG_CH_DaqCmpDoEnable.value)
        ltcEnable = c_uint32(PropertyID2.CFG_CH_DaqLtcEnable.value)
        disable = c_double(COMPARE_ENABLE.CMP_DISABLE.value)
        getSettingValue = c_double(0)
        # Get LTC enable
        for idx in range(len(self.LTCCh)):
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcEnable, byref(getSettingValue))
            print('LTC[{0}] enable:{1}'.format(self.LTCCh[idx].value, getSettingValue.value))
        for idx in range(len(self.cmpCh4270)):
            # Disable CMP
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpOutEnable, disable)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpOutEnable, byref(getSettingValue))
            self.assertEqual(disable.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqCmpDoEnable.name, disable.value, getSettingValue.value, self.cmpCh4270[idx].value))
        # for idx in range(len(self.LTCCh)):
        #     # Disable LTC
        #     self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcEnable, disable)
        #     self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        #     self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcEnable, byref(getSettingValue))
        #     self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        #     self.assertEqual(disable.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
        #        PropertyID2.CFG_CH_DaqLtcEnable.name, disable.value, getSettingValue.value, self.LTCCh[idx].value))

    def test_Set4270CMPPulse(self):
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        # CMP Property
        cmpOutMode = c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value)
        cmpOutDelay = c_uint32(PropertyID2.CFG_CH_DaqCmpDoDelay.value)
        cmpPulseWidth = c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidth.value)
        cmpPulseWidthEx = c_uint32(PropertyID2.CFG_CH_DaqCmpDoPulseWidthEx.value)
        cmpDeviation = c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)
        cmpLogic = c_uint32(PropertyID2.CFG_CH_DaqCmpDoLogic.value)
        getSettingValue = c_double(0)
        delay0 = c_double(0)
        pulseMode = c_double(COMPARE_OUTPUT_MODE.CMP_PULSE.value)
        # 23: 168ms
        pulseWidth = c_double(23)
        deviation500 = c_double(0)
        for idx in range(len(self.cmpCh4270)):
            # Set Logic
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpLogic, delay0)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpLogic, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(delay0.value, getSettingValue.value, 'CMP[{0}] Set {1} failed! Set {2}, get {3}'.format(self.cmpCh4270[idx].value, PropertyID2.CFG_CH_DaqCmpDoLogic.name, delay0.value, getSettingValue.value))
            # Set Deviation
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpDeviation, deviation500)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpDeviation, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(deviation500.value, getSettingValue.value, 'CMP[{0}] Set {1} failed! Set {2}, get {3}'.format(self.cmpCh4270[idx].value, PropertyID2.CFG_CH_DaqCmpDeviation.name, deviation500.value, getSettingValue.value))
            # Set widthEx
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpPulseWidthEx, pulseWidth)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpPulseWidthEx, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(pulseWidth.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqCmpDoPulseWidthEx.name, pulseWidth.value, getSettingValue.value, self.cmpCh4270[idx].value))
            # Set CMP output mode as Pulse mode
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpOutMode, pulseMode)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpOutMode, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(pulseMode.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqCmpDoOutputMode.name, pulseMode.value, getSettingValue.value, self.cmpCh4270[idx].value))
            # Set CMP output pulse width as 168ms
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpPulseWidth, pulseWidth)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpPulseWidth, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(pulseWidth.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqCmpDoPulseWidth.name, pulseWidth.value, getSettingValue.value, self.cmpCh4270[idx].value))
            self.errCde = self.AdvMot.Acm2_SetProperty(0, c_uint32(PropertyID2.CFG_CH_DaqDoFuncSelect.value), c_double(1))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Set CMP output delay time as 0
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpOutDelay, delay0)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpOutDelay, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(delay0.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                'Delay time', delay0.value, getSettingValue.value, self.cmpCh4270[idx].value))            
        if global_cmp_mode == 2:
            cmpDeviation = c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)
            deviation500 = c_double(500)
            for idx in range(len(self.cmpCh4270)):
                self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpDeviation, deviation500)
                self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
                self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpDeviation, byref(getSettingValue))
                self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
                self.assertEqual(deviation500.value, getSettingValue.value, 'CMP[{0}] Set {1} failed! Set {2}, get {3}'.format(self.cmpCh4270[idx].value, PropertyID2.CFG_CH_DaqCmpDeviation.name, deviation500.value, getSettingValue.value))

    def test_Set4270CMPToggle(self):
        global global_cmp_mode
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        # CMP Property
        cmpOutMode = c_uint32(PropertyID2.CFG_CH_DaqCmpDoOutputMode.value)
        cmpOutDelay = c_uint32(PropertyID2.CFG_CH_DaqCmpDoDelay.value)
        getSettingValue = c_double(0)
        cmpMode = c_double(COMPARE_OUTPUT_MODE.CMP_TOGGLE.value)
        delay0 = c_double(0)
        for idx in range(len(self.cmpCh4270)):
            # Set CMP output mode as Toggle mode
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpOutMode, cmpMode)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpOutMode, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(cmpMode.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqCmpDoOutputMode.name, cmpMode.value, getSettingValue.value, self.cmpCh4270[idx].value))
            # Set CMP output delay time as 0
            self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpOutDelay, delay0)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpOutDelay, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(delay0.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                'Delay time', delay0.value, getSettingValue.value, self.cmpCh4270[idx].value))
        if global_cmp_mode == 2:
            cmpDeviation = c_uint32(PropertyID2.CFG_CH_DaqCmpDeviation.value)
            deviation500 = c_double(300)
            for idx in range(len(self.cmpCh4270)):
                self.errCde = self.AdvMot.Acm2_SetProperty(self.cmpCh4270[idx].value, cmpDeviation, deviation500)
                self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
                self.errCde = self.AdvMot.Acm2_GetProperty(self.cmpCh4270[idx].value, cmpDeviation, byref(getSettingValue))
                self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
                self.assertEqual(deviation500.value, getSettingValue.value, 'CMP[{0}] Set {1} failed! Set {2}, get {3}'.format(self.cmpCh4270[idx].value, PropertyID2.CFG_CH_DaqCmpDeviation.name, deviation500.value, getSettingValue.value))

    def test_Set4270CMPDelay(self):
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        getSettingValue = c_double(0)
        delay65535 = c_double(65535)
        cmpOutDelay = c_uint32(PropertyID2.CFG_CH_DaqCmpDoDelay.value)
        for idx in range(len(self.delay_cmp_ch1_ch3)):
            # Set CMP Ch 1, Ch3 delay 65535 us
            self.errCde = self.AdvMot.Acm2_SetProperty(self.delay_cmp_ch1_ch3[idx].value, cmpOutDelay, delay65535)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.delay_cmp_ch1_ch3[idx].value, cmpOutDelay, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(delay65535.value, getSettingValue.value, 'CMP[{3}] Set {0} failed! Set {1}, get {2}'.format(
                'Delay time', delay65535.value, getSettingValue.value, self.delay_cmp_ch1_ch3[idx].value))

    def test_Set4270LTCRising(self):
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        getSettingValue = c_double(0)
        # LTC Property
        ltcEdge = c_uint32(PropertyID2.CFG_CH_DaqLtcTrigSel.value)
        edgeRising = c_double(LATCH_BUF_EDGE.LATCH_BUF_RISING_EDGE.value)
        ltcReverse = c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value)
        logicNotInverse = c_double(0)
        ltcFilter = c_uint32(PropertyID2.CFG_CH_DaqLtcFilter.value)
        # Filter mode 10 as 10.2us
        filterMode = c_double(10)
        for idx in range(len(self.LTCCh)):
            # Set LTC edge as Rising
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcEdge, edgeRising)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcEdge, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(edgeRising.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqLtcTrigSel.name, edgeRising.value, getSettingValue.value, self.LTCCh[idx].value))
            # Set LTC logic
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcReverse, logicNotInverse)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcReverse, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(logicNotInverse.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqLtcLogic.name, logicNotInverse.value, getSettingValue.value, self.LTCCh[idx].value))
            # Set LTC filter
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcFilter, filterMode)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcFilter, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(filterMode.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqLtcFilter.name, filterMode.value, getSettingValue.value, self.LTCCh[idx].value))

    def test_Set4270LTCEdgeBoth(self):
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        getSettingValue = c_double(0)
        # LTC Property
        ltcEdge = c_uint32(PropertyID2.CFG_CH_DaqLtcTrigSel.value)
        edgeBoth = c_double(LATCH_BUF_EDGE.LATCH_BUF_BOTH_EDGE.value)
        ltcReverse = c_uint32(PropertyID2.CFG_CH_DaqLtcLogic.value)
        logicNotInverse = c_double(0)
        ltcFilter = c_uint32(PropertyID2.CFG_CH_DaqLtcFilter.value)
        # Filter mode 10 as 10.2us
        filterMode = c_double(10)
        for idx in range(len(self.LTCCh)):
            # Set LTC edge as Rising
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcEdge, edgeBoth)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcEdge, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(edgeBoth.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqLtcTrigSel.name, edgeBoth.value, getSettingValue.value, self.LTCCh[idx].value))
            # Set LTC logic
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcReverse, logicNotInverse)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcReverse, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(logicNotInverse.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqLtcLogic.name, logicNotInverse.value, getSettingValue.value, self.LTCCh[idx].value))
            # Set LTC filter
            self.errCde = self.AdvMot.Acm2_SetProperty(self.LTCCh[idx].value, ltcFilter, filterMode)
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.errCde = self.AdvMot.Acm2_GetProperty(self.LTCCh[idx].value, ltcFilter, byref(getSettingValue))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            self.assertEqual(filterMode.value, getSettingValue.value, 'LTC[{3}] Set {0} failed! Set {1}, get {2}'.format(
                PropertyID2.CFG_CH_DaqLtcFilter.name, filterMode.value, getSettingValue.value, self.LTCCh[idx].value))

    def test_SetCMPAutoAndCheckLTC(self):
        # Set CNT Pulse Mode as CW/CCW
        self.test_SetCntPulseMode()
        # Reset CMP & LTC Data
        self.test_Reset4270CMPLTCData()
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        startPos = c_double(3000)
        endPos = c_double(10000)
        interval = c_double(1000)
        numbers = list(range(int(startPos.value), int(endPos.value)+1, int(interval.value)))
        getCntData = [c_double(0), c_double(0), c_double(0)]
        getCmpData = (c_double * (len(self.CNTCh)))()
        bufferStatus = BUFFER_STATUS()
        getLTCDataCnt = c_uint32(128)
        getLTCData = (c_double * (getLTCDataCnt.value * self.ltcLinkedCnt.value))()
        # Enable CMP & LTC
        self.test_Enable4270CMPLTC()
        time.sleep(1)
        # Set CMP data
        for idx in range(len(self.CMPCh)):
            self.errCde = self.AdvMot.Acm2_ChSetCmpAuto(self.CMPCh[idx], startPos, endPos, interval)
            print('Set CMP[{0}] auto, start:{1}'.format(self.CMPCh[idx].value, startPos.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed. CMP[{1}]'.format(self._testMethodName, self.CMPCh[idx]))
        # Reset counter
        self.test_Reset4270Counter()
        # Check counter
        while ((getCntData[len(getCntData) - 1].value < endPos.value) and (getCntData[0].value < endPos.value)):
            for idx in range(len(self.CNTCh)):
                time.sleep(0.5)
                self.AdvMot.Acm2_ChGetCntData(self.CNTCh[idx].value, byref(getCntData[idx]))
        # Get LTC data
        for idx in range(len(self.LTCCh)):
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(self.LTCCh[idx].value, byref(bufferStatus))
            print('\nLTC[{0}] remain:{1}, free:{2}'.format(self.LTCCh[idx].value, bufferStatus.RemainCount, bufferStatus.FreeSpaceCount))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            getLTCDataCnt = c_uint32(128)
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(self.LTCCh[idx].value, getLTCData, self.ltcLinkedCnt, byref(getLTCDataCnt))
            print('getLTCDataCnt:{0}'.format(getLTCDataCnt.value))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            for i in range(len(getLTCData)):
                if (getLTCData[i] > 0):
                    print('LTC[{0}] CNT[{3}] Data[{1}]:{2}'.format(self.LTCCh[idx].value, i ,getLTCData[i], int(i//128)))
            for i, j in zip(range(len(getLTCData)), range(len(numbers))):
                self.assertAlmostEqual(numbers[j], getLTCData[i], delta=self.delta, msg='Check LTC[{2}] CNT[{3}] data: set {0}, get {1}'.format(numbers[j], getLTCData[i], self.LTCCh[idx].value, int(i//128)))
        # Reset CMP & LTC Data
        self.test_Reset4270CMPLTCData()

    def test_SetCMPTableAndCheckLTC(self):
        global global_cmp_mode
        # Set CNT Pulse Mode as CW/CCW
        self.test_SetCntPulseMode()
        # Reset CMP & LTC Data
        self.test_Reset4270CMPLTCData()
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        if (global_cmp_mode == 2):
            cmpDataTable = [c_double(2600), c_double(5800), c_double(8600), c_double(9900), c_double(12300), c_double(14500),
                            c_double(2601), c_double(5801), c_double(8601), c_double(9901), c_double(12301), c_double(14501)]
            refCMPDataTable = (c_double * len(cmpDataTable))(*cmpDataTable)
            lastPos = cmpDataTable[len(cmpDataTable) - 1]
        else:
            cmpDataTable = [c_double(4000), c_double(7500), c_double(8600), c_double(9900), c_double(12300), c_double(14500)]
            refCMPDataTable = (c_double * len(cmpDataTable))(*cmpDataTable)
            lastPos = cmpDataTable[len(cmpDataTable) - 1]
        getCntData = [c_double(0), c_double(0), c_double(0)]
        bufferStatus = BUFFER_STATUS()
        getLTCDataCnt = c_uint32(128)
        getLTCData = (c_double * (getLTCDataCnt.value * self.ltcLinkedCnt.value))()
        # Enable CMP & LTC
        self.test_Enable4270CMPLTC()
        time.sleep(1)
        # Set CMP data
        for idx in range(len(self.CMPCh)):
            if (global_cmp_mode == 2):
                self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(self.CMPCh[idx].value, refCMPDataTable, self.cmpLinkedCnt, c_uint32(int(len(cmpDataTable)/self.cmpLinkedCnt.value)))
                self.errCde = self.AdvMot.Acm2_ChEnableCmp(self.CMPCh[idx].value, c_uint32(COMPARE_ENABLE.CMP_ENABLE.value))
            else:
                self.errCde = self.AdvMot.Acm2_ChSetCmpBufferData(self.CMPCh[idx].value, refCMPDataTable, len(cmpDataTable))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
        # Reset counter
        self.test_Reset4270Counter()
        # Check counter
        while ((getCntData[0].value < lastPos.value) and (getCntData[len(getCntData) - 1].value < lastPos.value)):
            for idx in range(len(self.CNTCh)):
                time.sleep(0.5)
                self.AdvMot.Acm2_ChGetCntData(self.CNTCh[idx].value, byref(getCntData[idx]))
        # Get LTC data
        for idx in range(len(self.LTCCh)):
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(self.LTCCh[idx].value, byref(bufferStatus))
            print('LTC[{0}] remain:{1}, free:{2}'.format(self.LTCCh[idx].value, bufferStatus.RemainCount, bufferStatus.FreeSpaceCount))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            getLTCDataCnt = c_uint32(128)
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(self.LTCCh[idx].value, getLTCData, self.ltcLinkedCnt, byref(getLTCDataCnt))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Check LTC data
            for i, j in zip(range(len(getLTCData)), range(int(len(cmpDataTable)/self.cmpLinkedCnt.value))):
                print('LTC[{0}] CNT[{1}] Set:{2} Get:{3}'.format(self.LTCCh[idx].value, self.cntCh4270[idx].value, cmpDataTable[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTable)/self.cmpLinkedCnt.value)].value, getLTCData[i]))
                self.assertAlmostEqual(cmpDataTable[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTable)/self.cmpLinkedCnt.value)].value, getLTCData[i], delta=self.delta, msg= 'Check LTC[{2}] CNT[{3}] data: set {0}, get {1}'.format(cmpDataTable[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTable)/self.cmpLinkedCnt.value)].value, getLTCData[i], self.LTCCh[idx].value, self.cntCh4270[idx].value))
        # Reset CMP & LTC Data
        self.test_Reset4270CMPLTCData()

    def test_SetCMP3TableAndCheckLTC(self):
        # Set CNT Pulse Mode as CW/CCW
        self.test_SetCntPulseMode()
        # Reset CMP & LTC Data
        self.test_Reset4270CMPLTCData()
        # Disable CMP & LTC
        self.test_Disable4270CMPLTC()
        excepted_err = 0
        cmpDataTableMulti = [c_double(2600), c_double(5800), c_double(8600), c_double(9900), c_double(12300), c_double(14500),
                            c_double(2601), c_double(5801), c_double(8601), c_double(9901), c_double(12301), c_double(14501)]
        cmpDataTableSingle = [c_double(4000), c_double(7500), c_double(8600), c_double(9900), c_double(12300), c_double(14500)]
        refCMPDataTableMulti = (c_double * len(cmpDataTableMulti))(*cmpDataTableMulti)
        refCMPDataTableSingle = (c_double * len(cmpDataTableSingle))(*cmpDataTableSingle)
        lastPos = cmpDataTableMulti[len(cmpDataTableMulti) - 1]
        getCntData = [c_double(0), c_double(0), c_double(0)]
        bufferStatus = BUFFER_STATUS()
        getLTCDataCnt = c_uint32(128)
        getLTCData = (c_double * (getLTCDataCnt.value * self.ltcLinkedCnt.value))()
        # Enable CMP & LTC
        self.test_Enable4270CMPLTC()
        time.sleep(1)
        # Set CMP data
        for idx in range(len(self.CMPCh)):
            if idx == 0:
                self.cmpLinkedCnt = c_uint32(2)
                self.errCde = self.AdvMot.Acm2_ChSetMultiCmpBufferData(self.CMPCh[idx].value, refCMPDataTableMulti, self.cmpLinkedCnt, c_uint32(int(len(cmpDataTableMulti)/self.cmpLinkedCnt.value)))
                self.errCde = self.AdvMot.Acm2_ChEnableCmp(self.CMPCh[idx].value, c_uint32(COMPARE_ENABLE.CMP_ENABLE.value))
            else:
                self.cmpLinkedCnt = c_uint32(1)
                self.errCde = self.AdvMot.Acm2_ChSetCmpBufferData(self.CMPCh[idx].value, refCMPDataTableSingle, len(cmpDataTableSingle))
        # Reset counter
        self.test_Reset4270Counter()
        # Check counter
        while ((getCntData[0].value < lastPos.value) and (getCntData[len(getCntData) - 1].value < lastPos.value)):
            for idx in range(len(self.CNTCh)):
                time.sleep(0.5)
                self.AdvMot.Acm2_ChGetCntData(self.CNTCh[idx].value, byref(getCntData[idx]))
        # Get LTC data
        for idx in range(len(self.LTCCh)):
            self.errCde = self.AdvMot.Acm2_ChGetLatchBufferStatus(self.LTCCh[idx].value, byref(bufferStatus))
            print('LTC[{0}] remain:{1}, free:{2}'.format(self.LTCCh[idx].value, bufferStatus.RemainCount, bufferStatus.FreeSpaceCount))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            getLTCDataCnt = c_uint32(128)
            self.errCde = self.AdvMot.Acm2_ChReadLatchBuffer(self.LTCCh[idx].value, getLTCData, self.ltcLinkedCnt, byref(getLTCDataCnt))
            self.assertEqual(excepted_err, self.errCde, '{0} failed.'.format(self._testMethodName))
            # Check LTC data
            if idx == 0 or idx == 1:
                self.cmpLinkedCnt = c_uint32(2)
                for i, j in zip(range(len(getLTCData)), range(int(len(cmpDataTableMulti)/self.cmpLinkedCnt.value))):
                    print('LTC[{0}] CNT[{1}] Set:{2} Get:{3}'.format(self.LTCCh[idx].value, self.cntCh4270[idx].value, cmpDataTableMulti[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTableMulti)/self.cmpLinkedCnt.value)].value, getLTCData[i]))
                    self.assertAlmostEqual(cmpDataTableMulti[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTableMulti)/self.cmpLinkedCnt.value)].value, getLTCData[i], delta=self.delta, msg= 'Check LTC[{2}] CNT[{3}] data: set {0}, get {1}'.format(cmpDataTableMulti[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTableMulti)/self.cmpLinkedCnt.value)].value, getLTCData[i], self.LTCCh[idx].value, self.cntCh4270[idx].value))
            elif idx == 2 or idx == 3:
                self.cmpLinkedCnt = c_uint32(1)
                for i, j in zip(range(len(getLTCData)), range(int(len(cmpDataTableSingle)/self.cmpLinkedCnt.value))):
                    print('LTC[{0}] CNT[{1}] Set:{2} Get:{3}'.format(self.LTCCh[idx].value, self.cntCh4270[idx].value, cmpDataTableSingle[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTableSingle)/self.cmpLinkedCnt.value)].value, getLTCData[i]))
                    self.assertAlmostEqual(cmpDataTableSingle[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTableSingle)/self.cmpLinkedCnt.value)].value, getLTCData[i], delta=self.delta, msg= 'Check LTC[{2}] CNT[{3}] data: set {0}, get {1}'.format(cmpDataTableSingle[j+int(idx%self.cmpLinkedCnt.value)*int(len(cmpDataTableSingle)/self.cmpLinkedCnt.value)].value, getLTCData[i], self.LTCCh[idx].value, self.cntCh4270[idx].value))
        # Reset CMP & LTC Data
        self.test_Reset4270CMPLTCData()

    def test_SingleAPI(self):
        self.test_Initial()
        getInfo = ADVAPI_IO_LINK_INFO()
        self.errCde = self.AdvMot.Acm2_GetMappedObjInfo(c_int(ADV_OBJ_TYPE.ADV_COUNTER_CHANNEL.value), 0, byref(getInfo))
        print('Dev:{0}'.format(getInfo.DeviceName))

def InitialDevice():
    tests = ['test_Initial']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def DownloadENIAndSetOPMode():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 1
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Get4270CntData():
    tests = ['test_Initial', 'test_Get4270CounterData']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def GetLocalCntData():
    tests = ['test_Initial', 'test_GetLocalCounterData']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Reset4270CntData():
    tests = ['test_Initial', 'test_Reset4270Counter']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Set4270CntPulseMode():
    tests = ['test_Initial', 'test_SetCntPulseMode']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Set4270CmpSoftTriggerOn():
    tests = ['test_Initial', 'test_Set4270CmpSoftTrigger', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def SetLocalCmpSoftTriggerOn():
    tests = ['test_Initial', 'test_SetLocalCmpSoftTrigger']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Get4270CMPLinkedCnt():
    tests = ['test_Initial', 'test_Get4270CMPLinkedCnt', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def Get4270LTCLinkedCnt():
    tests = ['test_Initial', 'test_Get4270LTCLinkedCnt', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC0AutoPulseRising():
    global global_cmp_mode, global_ltc_mode
    global_ltc_mode = 0
    global_cmp_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC0TablePulseRising():
    global global_cmp_mode, global_ltc_mode
    global_ltc_mode = 0
    global_cmp_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC0AutoToggleEdgeBoth():
    global global_cmp_mode, global_ltc_mode
    global_ltc_mode = 0
    global_cmp_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC0TableToggleEdgeBoth():
    global global_cmp_mode, global_ltc_mode
    global_ltc_mode = 0
    global_cmp_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC1AutoPulseRising():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 0
    global_ltc_mode = 1
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC1TablePulseRising():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 0
    global_ltc_mode = 1
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC1AutoToggleEdgeBoth():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 0
    global_ltc_mode = 1
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP0LTC1TableToggleEdgeBoth():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 0
    global_ltc_mode = 1
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP1LTC0AutoPulseRising():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 1
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP1LTC0TablePulseRising():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 1
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP1LTC0AutoToggleEdgeBoth():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 1
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP1LTC0TableToggleEdgeBoth():
    global global_cmp_mode, global_ltc_mode
    global_cmp_mode = 1
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP1LTC0AutoPulseRisingDelay():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 1
    global_ltc_mode = 0
    global_cmp_delay = True
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_Set4270CMPDelay', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP1LTC0TablePulseRisingDelay():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 1
    global_ltc_mode = 0
    global_cmp_delay = True
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_Set4270CMPDelay', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP2LTC0AutoPulseRising():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 2
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP2LTC0TablePulseRising():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 2
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP2LTC0AutoToggleBothEdge():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 2
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP2LTC0TableToggleBothEdge():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 2
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPTableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP3LTC0AutoPulseRising():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 3
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP3LTC0TablePulseRising():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 3
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPPulse',
             'test_Set4270LTCRising', 'test_SetCMP3TableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP3LTC0AutoToggleBothEdge():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 3
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMPAutoAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunCMP3LTC0TableToggleBothEdge():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 3
    global_ltc_mode = 0
    tests = ['test_Initial', 'test_Load4270ENI', 'test_Conntect', 'test_Set4270CMPToggle',
             'test_Set4270LTCEdgeBoth', 'test_SetCMP3TableAndCheckLTC', 'test_DisConnect']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

def RunTestSingleAPI():
    global global_cmp_mode, global_ltc_mode, global_cmp_delay
    global_cmp_mode = 1
    global_ltc_mode = 1
    tests = ['test_SingleAPI']
    suite = unittest.TestSuite(map(AdvCmnAPI_Test, tests))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    run_test_single_api = runner.run(RunTestSingleAPI())
    # get_available_devs = runner.run(InitialDevice())
    # load_eni_set_op_mode = runner.run(DownloadENIAndSetOPMode())
    # set_4270cnt_pulse_mode = runner.run(Set4270CntPulseMode())
    # reset_4270cnt_data = runner.run(Reset4270CntData())
    # get_4270cnt_data = runner.run(Get4270CntData())
    # get_localcnt_data = runner.run(GetLocalCntData())
    # get_4270cmp_linked_cnt = runner.run(Get4270CMPLinkedCnt())
    # set_4270cmp_soft_trigger_on = runner.run(Set4270CmpSoftTriggerOn())
    # set_local_soft_trigger_on = runner.run(SetLocalCmpSoftTriggerOn())
    # get_4270ltc_linked_cnt = runner.run(Get4270LTCLinkedCnt())
# CMP Mode 0 LTC Mode 0
    # run_cmp0_ltc0_auto_pulse = runner.run(RunCMP0LTC0AutoPulseRising())
    # run_cmp0_ltc0_table_pulse = runner.run(RunCMP0LTC0TablePulseRising())
    # run_cmp0_ltc0_auto_toggle_edge_both = runner.run(RunCMP0LTC0AutoToggleEdgeBoth())
    # run_cmp0_ltc0_table_toggle_edge_both = runner.run(RunCMP0LTC0TableToggleEdgeBoth())
# CMP Mode 0 LTC Mode 1
    # run_cmp0_ltc1_auto_pulse_rising = runner.run(RunCMP0LTC1AutoPulseRising())
    # run_cmp0_ltc1_table_pulse_rising = runner.run(RunCMP0LTC1TablePulseRising())
    # run_cmp0_ltc1_auto_toggle_edge_both = runner.run(RunCMP0LTC1AutoToggleEdgeBoth())
    # run_cmp0_ltc1_table_toggle_edge_both = runner.run(RunCMP0LTC1TableToggleEdgeBoth())
# CMP Mode 1 LTC Mode 0
    # run_cmp1_ltc0_auto_pulse_rising = runner.run(RunCMP1LTC0AutoPulseRising())
    # run_cmp1_ltc0_table_pulse_rising = runner.run(RunCMP1LTC0TablePulseRising())
    # run_cmp1_ltc0_auto_toggle_both_edge = runner.run(RunCMP1LTC0AutoToggleEdgeBoth())
    # run_cmp1_ltc0_table_toggle_both_edge = runner.run(RunCMP1LTC0TableToggleEdgeBoth())
    # run_cmp1_ltc0_auto_pulse_rising_delay = runner.run(RunCMP1LTC0AutoPulseRisingDelay())
    # run_cmp1_ltc0_table_pulse_rising_delay = runner.run(RunCMP1LTC0TablePulseRisingDelay())
# CMP Mode 2 LTC Mode 0
    # run_cmp2_ltc0_auto_pulse_rising = runner.run(RunCMP2LTC0AutoPulseRising())
    # run_cmp2_ltc0_table_pulse_rising = runner.run(RunCMP2LTC0TablePulseRising())
    # run_cmp2_ltc0_auto_toggle_both_edge = runner.run(RunCMP2LTC0AutoToggleBothEdge())
    # run_cmp2_ltc0_table_toggle_both_edge = runner.run(RunCMP2LTC0TableToggleBothEdge())
# CMP Mode 3 LTC Mode0
    # run_cmp3_ltc0_auto_pulse_rising = runner.run(RunCMP3LTC0AutoPulseRising())
    # run_cmp3_ltc0_table_pulse_rising = runner.run(RunCMP3LTC0TablePulseRising())
    # run_cmp3_ltc0_auto_toggle_both_edge = runner.run(RunCMP3LTC0AutoToggleBothEdge())
    # run_cmp3_ltc0_table_toggle_both_edge = runner.run(RunCMP3LTC0TableToggleBothEdge())
