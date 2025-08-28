# This unit test is for common motion 1.0
import unittest
import time
import os
import numpy as np
import xml.etree.ElementTree as xml
import threading
from AcmP.AdvCmnAPI_CM2 import AdvCmnAPI
from AcmP.AdvMotApi_CM2 import *
from AcmP.AdvMotDrv import *
from AcmP.MotionInfo import *
from AcmP.AdvMotPropID_CM2 import PropertyID
from AcmP.AdvMotErr_CM2 import ErrorCode

class AdvCmnAPICM1_Test(unittest.TestCase):
    def setUp(self):
        self.AdvMot = AdvCmnAPI
    # Call once by test case
    @classmethod
    def setUpClass(cls):
        cls.maxDevCnt = 10
        cls.maxDevList = (DEVLIST * cls.maxDevCnt)()
        cls.maxDev = c_uint32(0)
        cls.errCde = c_uint32(ErrorCode.SUCCESS.value)
        cls.axStart = c_uint32(0)
        cls.axCnt = c_uint32(64)
        cls.gpID = c_uint32(0)
        cls.gpArr = [c_uint32(0), c_uint32(1)]
        cls.transGpArr = (c_uint32 * len(cls.gpArr))(*cls.gpArr)
        cls.exceptError = c_uint32(ErrorCode.SUCCESS.value)
        cls.devNum = c_uint32(0)
        cls.stateArr = [c_uint32(AXIS_STATE.STA_AX_EXT_JOG_READY.value + 1) for v in range(cls.axCnt.value)]
        cls.devHandle = c_void_p()

    # Call everytime by unit
    def tearDown(self):
        self.errCde = c_uint32(ErrorCode.SUCCESS.value)
        self.exceptError = c_uint32(ErrorCode.SUCCESS.value)
# Device
    def GetAvailableDevs(self):
        self.errCde = self.AdvMot.Acm_GetAvailableDevs(self.maxDevList, self.maxDevCnt, byref(self.maxDev))
        self.assertEqual(self.exceptError.value, self.errCde, '{0} failed.'.format(self._testMethodName))
        print('---Device counts:{0}---'.format(self.maxDev.value))
        print('index devNum{:<4} devName'.format(''))
        for i in range(self.maxDev.value):
            print('{index:<5} 0x{devNum:x} {devName}'.format(index=i,
            devNum=self.maxDevList[i].dwDeviceNum, devName=self.maxDevList[i].szDeviceName))
        print('---End of GetAvailableDevs---')
        if self.maxDev.value > 0:
            self.devNum.value = self.maxDevList[0].dwDeviceNum

    def DeviceOpen(self):
        self.errCde = self.AdvMot.Acm_DevOpen(self.devNum.value, byref(self.devHandle))
        self.assertEqual(self.exceptError.value, self.errCde, '{0} failed.'.format(self._testMethodName))

    def DeviceClose(self):
        self.errCde = self.AdvMot.Acm_DevClose(byref(self.devHandle))
        self.assertEqual(self.exceptError.value, self.errCde, '{0} failed.'.format(self._testMethodName))

    def AxisOpen(self):
        axid = c_uint16(0)
        axHand = c_void_p()
        self.errCde = self.AdvMot.Acm_AxOpen(self.devHandle, axid, byref(axHand))
        self.assertEqual(self.exceptError.value, self.errCde, '{0} failed.'.format(self._testMethodName))
        self.errCde = self.AdvMot.Acm_AxClose(axHand)
        self.assertEqual(self.exceptError.value, self.errCde, '{0} failed.'.format(self._testMethodName))

def JustGetAvailableDevices():
    tests = ['GetAvailableDevs']
    suite = unittest.TestSuite(map(AdvCmnAPICM1_Test, tests))
    return suite
def DeviceOpenAndClose():
    tests = ['GetAvailableDevs', 'DeviceOpen', 'DeviceClose']
    suite = unittest.TestSuite(map(AdvCmnAPICM1_Test, tests))
    return suite
def AxisOpenAndClose():
    tests = ['GetAvailableDevs', 'DeviceOpen', 'AxisOpen', 'DeviceClose']
    suite = unittest.TestSuite(map(AdvCmnAPICM1_Test, tests))
    return suite
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    # get_available_devs = runner.run(JustGetAvailableDevices())
    # dev_open_close = runner.run(DeviceOpenAndClose())
    ax_open_close = runner.run(AxisOpenAndClose())
