from AcmP.AdvMotApi_CM2 import *
from AcmP.MotionInfo import *
from AcmP.AdvMotDrv import *
import os

if os.name == 'nt':
    lib = CDLL(r'C:\Windows\System32\ADVMOT.dll')
else:
    lib = CDLL('/usr/lib/libadvmot.so')

class AdvCmnAPI_CM2:
# Device
    # try:
    #     Acm2_DevOpen = lib.Acm2_DevOpen
    #     Acm2_DevOpen.argtypes = [c_uint32, POINTER(DEVICEINFO)]
    #     Acm2_DevOpen.restype = c_uint32
    # except:
    #     pass

    try:
        Acm2_DevInitialize = lib.Acm2_DevInitialize
        Acm2_DevInitialize.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetAvailableDevs = lib.Acm2_GetAvailableDevs
        Acm2_GetAvailableDevs.argtypes = [POINTER(DEVLIST), c_uint32, POINTER(c_uint32)]
        Acm2_GetAvailableDevs.restype = c_uint32
    except:
        pass

    # try:
    #     Acm2_DevExportMappingTable = lib.Acm2_DevExportMappingTable
    #     Acm2_DevExportMappingTable.argtypes = [c_char_p]
    #     Acm2_DevExportMappingTable.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm2_DevImportMappingTable = lib.Acm2_DevImportMappingTable
    #     Acm2_DevImportMappingTable.argtypes = [c_char_p]
    #     Acm2_DevImportMappingTable.restype = c_uint32
    # except:
    #     pass

    try:
        Acm2_DevSaveAllMapFile = lib.Acm2_DevSaveAllMapFile
        Acm2_DevSaveAllMapFile.argtypes = [c_char_p]
        Acm2_DevSaveAllMapFile.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevLoadAllMapFile = lib.Acm2_DevLoadAllMapFile
        Acm2_DevLoadAllMapFile.argtypes = [c_char_p]
        Acm2_DevLoadAllMapFile.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetMappedPhysicalID = lib.Acm2_GetMappedPhysicalID
        Acm2_GetMappedPhysicalID.argtypes = [c_int, c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_GetMappedPhysicalID.restype = c_uint32
    except:
        pass
    
    try:
        Acm2_GetMappedLogicalIDList = lib.Acm2_GetMappedLogicalIDList
        Acm2_GetMappedLogicalIDList.argtypes = [c_int, c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_GetMappedLogicalIDList.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetMappedObjInfo = lib.Acm2_GetMappedObjInfo
        Acm2_GetMappedObjInfo.argtypes = [c_int, c_uint32, c_void_p]
        Acm2_GetMappedObjInfo.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevAllClose = lib.Acm2_DevAllClose
        Acm2_DevAllClose.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetLastError = lib.Acm2_GetLastError
        Acm2_GetLastError.argtypes = [c_uint, c_uint32]
        Acm2_GetLastError.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetProperty = lib.Acm2_GetProperty
        Acm2_GetProperty.argtypes = [c_uint32, c_uint32, POINTER(c_double)]
        Acm2_GetProperty.restype = c_uint32
    except:
        pass

    try:
        Acm2_SetProperty = lib.Acm2_SetProperty
        Acm2_SetProperty.argtypes = [c_uint32, c_uint32, c_double]
        Acm2_SetProperty.restype = c_uint32
    except:
        pass

    try:
        Acm2_SetMultiProperty = lib.Acm2_SetMultiProperty
        Acm2_SetMultiProperty.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_double), c_uint32, POINTER(c_uint32)]
        Acm2_SetMultiProperty.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetMultiProperty = lib.Acm2_GetMultiProperty
        Acm2_GetMultiProperty.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_double), c_uint32, POINTER(c_uint32)]
        Acm2_GetMultiProperty.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetRawProperty = lib.Acm2_GetRawProperty
        Acm2_GetRawProperty.argtypes = [c_uint32, c_uint32, c_void_p, POINTER(c_uint32)]
        Acm2_GetRawProperty.restype = c_uint32
    except:
        pass

    try:
        Acm2_EnableCallBackFuncForOneEvent = lib.Acm2_EnableCallBackFuncForOneEvent
        Acm2_EnableCallBackFuncForOneEvent.argtypes = [c_uint32, c_int, CALLBACK_FUNC]
        Acm2_EnableCallBackFuncForOneEvent.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevLoadAllConfig = lib.Acm2_DevLoadAllConfig
        Acm2_DevLoadAllConfig.argtypes = [c_char_p]
        Acm2_DevLoadAllConfig.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevLoadConfig = lib.Acm2_DevLoadConfig
        Acm2_DevLoadConfig.argtypes = [c_uint32, c_char_p]
        Acm2_DevLoadConfig.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevReadMailBox = lib.Acm2_DevReadMailBox
        Acm2_DevReadMailBox.argtypes = [c_uint, c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_DevReadMailBox.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevWriteMailBox = lib.Acm2_DevWriteMailBox
        Acm2_DevWriteMailBox.argtypes = [c_uint, c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_DevWriteMailBox.restype = c_uint32
    except:
        pass

    try:
        Acm2_GetErrors = lib.Acm2_GetErrors
        Acm2_GetErrors.argtypes = [c_uint32, c_void_p, POINTER(c_uint32)]
        Acm2_GetErrors.restype = c_uint32
    except:
        pass

    try:
        Acm2_ResetErrorRecord = lib.Acm2_ResetErrorRecord
        Acm2_ResetErrorRecord.argtypes = [c_uint32]
        Acm2_ResetErrorRecord.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevPreviewMotion = lib.Acm2_DevPreviewMotion
        Acm2_DevPreviewMotion.argtypes = [c_uint32, c_char_p, c_char_p, c_uint16]
        Acm2_DevPreviewMotion.restype = c_uint32
    except:
        pass
# Axis
    try:
        Acm2_AxReturnPausePosition = lib.Acm2_AxReturnPausePosition
        Acm2_AxReturnPausePosition.argtypes = [c_uint32]
        Acm2_AxReturnPausePosition.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetSvOn = lib.Acm2_AxSetSvOn
        Acm2_AxSetSvOn.argtypes = [c_uint32, c_uint]
        Acm2_AxSetSvOn.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevSetAllSvOn = lib.Acm2_DevSetAllSvOn
        Acm2_DevSetAllSvOn.argtypes = [c_uint]
        Acm2_DevSetAllSvOn.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetErcOn = lib.Acm2_AxSetErcOn
        Acm2_AxSetErcOn.argtypes = [c_uint32, c_uint]
        Acm2_AxSetErcOn.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxResetAlm = lib.Acm2_AxResetAlm
        Acm2_AxResetAlm.argtypes = [c_uint32, c_uint]
        Acm2_AxResetAlm.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxPTP = lib.Acm2_AxPTP
        Acm2_AxPTP.argtypes = [c_uint32, c_uint, c_double]
        Acm2_AxPTP.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMoveContinue = lib.Acm2_AxMoveContinue
        Acm2_AxMoveContinue.argtypes = [c_uint32, c_uint]
        Acm2_AxMoveContinue.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMotionStop = lib.Acm2_AxMotionStop
        Acm2_AxMotionStop.argtypes = [POINTER(c_uint32), c_uint32, c_uint, c_double]
        Acm2_AxMotionStop.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxHome = lib.Acm2_AxHome
        Acm2_AxHome.argtypes = [c_uint32, c_uint, c_uint]
        Acm2_AxHome.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMoveGantryHome = lib.Acm2_AxMoveGantryHome
        Acm2_AxMoveGantryHome.argtypes = [c_uint32, c_uint, c_uint]
        Acm2_AxMoveGantryHome.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetHomeSpeedProfile = lib.Acm2_AxSetHomeSpeedProfile
        Acm2_AxSetHomeSpeedProfile.argtypes = [c_uint32, SPEED_PROFILE_PRM]
        Acm2_AxSetHomeSpeedProfile.restype = c_uint32
    except:
        pass
    
    try:
        Acm2_AxChangePos = lib.Acm2_AxChangePos
        Acm2_AxChangePos.argtypes = [c_uint32, c_double]
        Acm2_AxChangePos.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxChangeVel = lib.Acm2_AxChangeVel
        Acm2_AxChangeVel.argtypes = [c_uint32, c_double, c_double, c_double]
        Acm2_AxChangeVel.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxChangeVelByRate = lib.Acm2_AxChangeVelByRate
        Acm2_AxChangeVelByRate.argtypes = [c_uint32, c_uint32, c_double, c_double]
        Acm2_AxChangeVelByRate.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMoveImpose = lib.Acm2_AxMoveImpose
        Acm2_AxMoveImpose.argtypes = [c_uint32, c_double, c_double]
        Acm2_AxMoveImpose.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxResetError = lib.Acm2_AxResetError
        Acm2_AxResetError.argtypes = [c_uint32]
        Acm2_AxResetError.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevResetAllError = lib.Acm2_DevResetAllError
        Acm2_DevResetAllError.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetState = lib.Acm2_AxGetState
        Acm2_AxGetState.argtypes = [c_uint32, c_uint, POINTER(c_uint32)]
        Acm2_AxGetState.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetMotionIO = lib.Acm2_AxGetMotionIO
        Acm2_AxGetMotionIO.argtypes = [c_uint32, POINTER(MOTION_IO)]
        Acm2_AxGetMotionIO.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetPosition = lib.Acm2_AxSetPosition
        Acm2_AxSetPosition.argtypes = [c_uint32, c_uint, c_double]
        Acm2_AxSetPosition.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetPosition = lib.Acm2_AxGetPosition
        Acm2_AxGetPosition.argtypes = [c_uint32, c_uint, POINTER(c_double)]
        Acm2_AxGetPosition.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetMachPosition = lib.Acm2_AxGetMachPosition
        Acm2_AxGetMachPosition.argtypes = [c_uint32, POINTER(c_double)]
        Acm2_AxGetMachPosition.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetSpeedProfile = lib.Acm2_AxSetSpeedProfile
        Acm2_AxSetSpeedProfile.argtypes = [c_uint32, SPEED_PROFILE_PRM]
        Acm2_AxSetSpeedProfile.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetVel = lib.Acm2_AxGetVel
        Acm2_AxGetVel.argtypes = [c_uint32, c_uint, POINTER(c_double)]
        Acm2_AxGetVel.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxEnableExternalMode = lib.Acm2_AxEnableExternalMode
        Acm2_AxEnableExternalMode.argtypes = [c_uint32, c_uint]
        Acm2_AxEnableExternalMode.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSoftJog = lib.Acm2_AxSoftJog
        Acm2_AxSoftJog.argtypes = [c_uint32, c_uint]
        Acm2_AxSoftJog.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetJogSpeedProfile = lib.Acm2_AxSetJogSpeedProfile
        Acm2_AxSetJogSpeedProfile.argtypes = [c_uint32, JOG_SPEED_PROFILE_PRM]
        Acm2_AxSetJogSpeedProfile.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMotionStart = lib.Acm2_AxMotionStart
        Acm2_AxMotionStart.argtypes = [c_uint32, c_uint32]
        Acm2_AxMotionStart.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxPause = lib.Acm2_AxPause
        Acm2_AxPause.argtypes = [c_uint32]
        Acm2_AxPause.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxResume = lib.Acm2_AxResume
        Acm2_AxResume.argtypes = [c_uint32]
        Acm2_AxResume.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxResetPVTTable = lib.Acm2_AxResetPVTTable
        Acm2_AxResetPVTTable.argtypes = [c_uint32]
        Acm2_AxResetPVTTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxLoadPVTTable = lib.Acm2_AxLoadPVTTable
        Acm2_AxLoadPVTTable.argtypes = [c_uint32, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_uint32]
        Acm2_AxLoadPVTTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxLoadPVTTableContinuous = lib.Acm2_AxLoadPVTTableContinuous
        Acm2_AxLoadPVTTableContinuous.argtypes = [c_uint32, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), c_double, c_uint32]
        Acm2_AxLoadPVTTableContinuous.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMovePVT = lib.Acm2_AxMovePVT
        Acm2_AxMovePVT.argtypes = [c_uint32]
        Acm2_AxMovePVT.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxCheckPTBuffer = lib.Acm2_AxCheckPTBuffer
        Acm2_AxCheckPTBuffer.argtypes = [c_uint32, POINTER(c_uint32)]
        Acm2_AxCheckPTBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxAddPTData = lib.Acm2_AxAddPTData
        Acm2_AxAddPTData.argtypes = [c_uint32, c_double, c_double]
        Acm2_AxAddPTData.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxMovePT = lib.Acm2_AxMovePT
        Acm2_AxMovePT.argtypes = [c_uint32]
        Acm2_AxMovePT.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxResetPTData = lib.Acm2_AxResetPTData
        Acm2_AxResetPTData.argtypes = [c_uint32]
        Acm2_AxResetPTData.restype = c_uint32
    except:
        pass
# Follow
    try:
        Acm2_AxGearIn = lib.Acm2_AxGearIn
        Acm2_AxGearIn.argtypes = [c_uint32, c_uint32, GEAR_IN_PRM]
        Acm2_AxGearIn.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGantryIn = lib.Acm2_AxGantryIn
        Acm2_AxGantryIn.argtypes = [c_uint32, c_uint32, GANTRY_IN_PRM]
        Acm2_AxGantryIn.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxPhaseAx = lib.Acm2_AxPhaseAx
        Acm2_AxPhaseAx.argtypes = [c_uint32, PHASE_AXIS_PRM]
        Acm2_AxPhaseAx.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSyncOut = lib.Acm2_AxSyncOut
        Acm2_AxSyncOut.argtypes = [c_uint32]
        Acm2_AxSyncOut.restype = c_uint32
    except:
        pass

# Group
    try:
        Acm2_GpGetPausePosition = lib.Acm2_GpGetPausePosition
        Acm2_GpGetPausePosition.argtypes = [c_uint32, POINTER(c_double)]
        Acm2_GpGetPausePosition.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpCreate = lib.Acm2_GpCreate
        Acm2_GpCreate.argtypes = [c_uint32, POINTER(c_uint32), c_uint32]
        Acm2_GpCreate.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpGetAxesInGroup = lib.Acm2_GpGetAxesInGroup
        Acm2_GpGetAxesInGroup.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_GpGetAxesInGroup.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpResetError = lib.Acm2_GpResetError
        Acm2_GpResetError.argtypes = [c_uint32]
        Acm2_GpResetError.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpLine = lib.Acm2_GpLine
        Acm2_GpLine.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_uint32)]
        Acm2_GpLine.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpArc_Center = lib.Acm2_GpArc_Center
        Acm2_GpArc_Center.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint]
        Acm2_GpArc_Center.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpArc_3P = lib.Acm2_GpArc_3P
        Acm2_GpArc_3P.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint]
        Acm2_GpArc_3P.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpArc_Angle = lib.Acm2_GpArc_Angle
        Acm2_GpArc_Angle.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_uint32), c_double, c_uint]
        Acm2_GpArc_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm2_Gp3DArc_Center = lib.Acm2_Gp3DArc_Center
        Acm2_Gp3DArc_Center.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint]
        Acm2_Gp3DArc_Center.restype = c_uint32
    except:
        pass

    try:
        Acm2_Gp3DArc_NormVec = lib.Acm2_Gp3DArc_NormVec
        Acm2_Gp3DArc_NormVec.argtypese = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_float), c_double, c_uint]
        Acm2_Gp3DArc_NormVec.restype = c_uint32
    except:
        pass

    try:
        Acm2_Gp3DArc_3P = lib.Acm2_Gp3DArc_3P
        Acm2_Gp3DArc_3P.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint, c_uint32]
        Acm2_Gp3DArc_3P.restype = c_uint32
    except:
        pass

    try:
        Acm2_Gp3DArc_3PAngle = lib.Acm2_Gp3DArc_3PAngle
        Acm2_Gp3DArc_3PAngle.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_double, c_uint]
        Acm2_Gp3DArc_3PAngle.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpHelix_Center = lib.Acm2_GpHelix_Center
        Acm2_GpHelix_Center.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint]
        Acm2_GpHelix_Center.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpHelix_3P = lib.Acm2_GpHelix_3P
        Acm2_GpHelix_3P.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint]
        Acm2_GpHelix_3P.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpHelix_Angle = lib.Acm2_GpHelix_Angle
        Acm2_GpHelix_Angle.argtypes = [c_uint32, c_uint, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_uint]
        Acm2_GpHelix_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpResume = lib.Acm2_GpResume
        Acm2_GpResume.argtypes = [c_uint32]
        Acm2_GpResume.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpPause = lib.Acm2_GpPause
        Acm2_GpPause.argtypes = [c_uint32]
        Acm2_GpPause.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpMotionStop = lib.Acm2_GpMotionStop
        Acm2_GpMotionStop.argtypes = [c_uint32, c_uint, c_double]
        Acm2_GpMotionStop.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpChangeVel = lib.Acm2_GpChangeVel
        Acm2_GpChangeVel.argtypes = [c_uint32, c_double, c_double, c_double]
        Acm2_GpChangeVel.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpChangeVelByRate = lib.Acm2_GpChangeVelByRate
        Acm2_GpChangeVelByRate.argtypes = [c_uint32, c_uint32, c_double, c_double]
        Acm2_GpChangeVelByRate.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpGetVel = lib.Acm2_GpGetVel
        Acm2_GpGetVel.argtypes = [c_uint32, c_uint, POINTER(c_double)]
        Acm2_GpGetVel.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpSetSpeedProfile = lib.Acm2_GpSetSpeedProfile
        Acm2_GpSetSpeedProfile.argtypes = [c_uint32, SPEED_PROFILE_PRM]
        Acm2_GpSetSpeedProfile.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpGetState = lib.Acm2_GpGetState
        Acm2_GpGetState.argtypes = [c_uint32, POINTER(c_uint32)]
        Acm2_GpGetState.restype = c_uint32
    except:
        pass

# Path
    try:
        Acm2_GpLoadPath = lib.Acm2_GpLoadPath
        Acm2_GpLoadPath.argtypes = [c_uint32, c_char_p, POINTER(c_uint32)]
        Acm2_GpLoadPath.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpAddPath = lib.Acm2_GpAddPath
        Acm2_GpAddPath.argtypes = [c_uint32, c_uint32, c_uint, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
        Acm2_GpAddPath.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpMovePath = lib.Acm2_GpMovePath
        Acm2_GpMovePath.argtypes = [c_uint32]
        Acm2_GpMovePath.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpResetPath = lib.Acm2_GpResetPath
        Acm2_GpResetPath.argtypes = [c_uint32]
        Acm2_GpResetPath.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpGetPathStatus = lib.Acm2_GpGetPathStatus
        Acm2_GpGetPathStatus.argtypes = [c_uint32, POINTER(c_uint)]
        Acm2_GpGetPathStatus.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpMoveSelPath = lib.Acm2_GpMoveSelPath
        Acm2_GpMoveSelPath.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        Acm2_GpMoveSelPath.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpGetPathIndexStatus = lib.Acm2_GpGetPathIndexStatus
        Acm2_GpGetPathIndexStatus.argtypes = [c_uint32, c_uint32, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
        Acm2_GpGetPathIndexStatus.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpDelay = lib.Acm2_GpDelay
        Acm2_GpDelay.argtypes = [c_uint32, c_uint32]
        Acm2_GpDelay.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpPathDO = lib.Acm2_GpPathDO
        Acm2_GpPathDO.argtypes = [c_uint32, PATH_DO_PRM]
        Acm2_GpPathDO.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpPathWaitDI = lib.Acm2_GpPathWaitDI
        Acm2_GpPathWaitDI.argtypes = [c_uint32, PATH_DI_WAIT_PRM]
        Acm2_GpPathWaitDI.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpPathWaitForAxis = lib.Acm2_GpPathWaitForAxis
        Acm2_GpPathWaitForAxis.argtypes = [c_uint32, PATH_AX_WAIT_PRM]
        Acm2_GpPathWaitForAxis.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpLookAheadPath = lib.Acm2_GpLookAheadPath
        Acm2_GpLookAheadPath.argtypes = [c_uint32, c_uint16, c_char_p]
        Acm2_GpLookAheadPath.restype = c_uint32
    except:
        pass

    try:
        Acm2_GpLookAheadPathFile = lib.Acm2_GpLookAheadPathFile
        Acm2_GpLookAheadPathFile.argtypes = [c_uint32, c_uint16, c_char_p, c_char_p, POINTER(c_uint32)]
        Acm2_GpLookAheadPathFile.restype = c_uint32
    except:
        pass

    # try:
    #     Acm2_GpLoadAndMovePath = lib.Acm2_GpLoadAndMovePath
    #     Acm2_GpLoadAndMovePath.argtypes = [c_uint32, c_char_p, POINTER(c_uint32)]
    #     Acm2_GpLoadAndMovePath.restype = c_uint32
    # except:
    #     pass

# DIO
    try:
        Acm2_ChSetDOBit = lib.Acm2_ChSetDOBit
        Acm2_ChSetDOBit.argtypes = [c_uint32, c_uint32]
        Acm2_ChSetDOBit.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDOBit = lib.Acm2_ChGetDOBit
        Acm2_ChGetDOBit.argtypes = [c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDOBit.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDIBit = lib.Acm2_ChGetDIBit
        Acm2_ChGetDIBit.argtypes = [c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDIBit.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetDOBitByRingNo = lib.Acm2_ChSetDOBitByRingNo
        Acm2_ChSetDOBitByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32]
        Acm2_ChSetDOBitByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDOBitByRingNo = lib.Acm2_ChGetDOBitByRingNo
        Acm2_ChGetDOBitByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDOBitByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDIBitByRingNo = lib.Acm2_ChGetDIBitByRingNo
        Acm2_ChGetDIBitByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDIBitByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetDOByte = lib.Acm2_ChSetDOByte
        Acm2_ChSetDOByte.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChSetDOByte.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDOByte = lib.Acm2_ChGetDOByte
        Acm2_ChGetDOByte.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDOByte.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDIByte = lib.Acm2_ChGetDIByte
        Acm2_ChGetDIByte.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDIByte.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetDOByteByRingNo = lib.Acm2_ChSetDOByteByRingNo
        Acm2_ChSetDOByteByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChSetDOByteByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDOByteByRingNo = lib.Acm2_ChGetDOByteByRingNo
        Acm2_ChGetDOByteByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDOByteByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetDIByteByRingNo = lib.Acm2_ChGetDIByteByRingNo
        Acm2_ChGetDIByteByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm2_ChGetDIByteByRingNo.restype = c_uint32
    except:
        pass
# AIO
    try:
        Acm2_ChSetAOData = lib.Acm2_ChSetAOData
        Acm2_ChSetAOData.argtypes = [c_uint32, c_uint, c_double]
        Acm2_ChSetAOData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetAOData = lib.Acm2_ChGetAOData
        Acm2_ChGetAOData.argtypes = [c_uint32, c_uint, POINTER(c_double)]
        Acm2_ChGetAOData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetAODataByRingNo = lib.Acm2_ChSetAODataByRingNo
        Acm2_ChSetAODataByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint, c_double]
        Acm2_ChSetAODataByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetAODataByRingNo = lib.Acm2_ChGetAODataByRingNo
        Acm2_ChGetAODataByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint, POINTER(c_double)]
        Acm2_ChGetAODataByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetAIData = lib.Acm2_ChGetAIData
        Acm2_ChGetAIData.argtypes = [c_uint32, c_uint, POINTER(c_double)]
        Acm2_ChGetAIData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetAIDataByRingNo = lib.Acm2_ChGetAIDataByRingNo
        Acm2_ChGetAIDataByRingNo.argtypes = [c_uint32, c_uint32, c_uint32, c_uint, POINTER(c_double)]
        Acm2_ChGetAIDataByRingNo.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetCntData = lib.Acm2_ChGetCntData
        Acm2_ChGetCntData.argtypes = [c_uint32, POINTER(c_double)]
        Acm2_ChGetCntData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetCntData = lib.Acm2_ChSetCntData
        Acm2_ChSetCntData.argtypes = [c_uint32, c_double]
        Acm2_ChSetCntData.restype = c_uint32
    except:
        pass
# Motion DIO:Compare
    try:
        Acm2_ChLinkCmpFIFO = lib.Acm2_ChLinkCmpFIFO
        Acm2_ChLinkCmpFIFO.argtypes = [c_uint32, POINTER(c_uint32), c_uint32]
        Acm2_ChLinkCmpFIFO.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChLinkCmpObject = lib.Acm2_ChLinkCmpObject
        Acm2_ChLinkCmpObject.argtypes = [c_uint32, c_uint, POINTER(c_uint32), c_uint32]
        Acm2_ChLinkCmpObject.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetLinkedCmpObject = lib.Acm2_ChGetLinkedCmpObject
        Acm2_ChGetLinkedCmpObject.argtypes = [c_uint32, POINTER(c_uint), POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_ChGetLinkedCmpObject.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChEnableCmp = lib.Acm2_ChEnableCmp
        Acm2_ChEnableCmp.argtypes = [c_uint32, c_uint32]
        Acm2_ChEnableCmp.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetCmpOut = lib.Acm2_ChSetCmpOut
        Acm2_ChSetCmpOut.argtypes = [c_uint32, c_uint]
        Acm2_ChSetCmpOut.restype = c_uint32
    except:
        pass
    
    try:
        Acm2_ChSetCmpDoOut = lib.Acm2_ChSetCmpDoOut
        Acm2_ChSetCmpDoOut.argtypes = [c_uint32, c_uint]
        Acm2_ChSetCmpDoOut.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetCmpData = lib.Acm2_AxGetCmpData
        Acm2_AxGetCmpData.argtypes = [c_uint32, POINTER(c_double)]
        Acm2_AxGetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetCmpData = lib.Acm2_ChGetCmpData
        Acm2_ChGetCmpData.argtypes = [c_uint32, POINTER(c_double), c_uint32]
        Acm2_ChGetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetCmpTable = lib.Acm2_AxSetCmpTable
        Acm2_AxSetCmpTable.argtypes = [c_uint32, POINTER(c_double), c_uint32]
        Acm2_AxSetCmpTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxSetCmpAuto = lib.Acm2_AxSetCmpAuto
        Acm2_AxSetCmpAuto.argtypes = [c_uint32, c_double, c_double, c_double]
        Acm2_AxSetCmpAuto.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetCmpAuto = lib.Acm2_ChSetCmpAuto
        Acm2_ChSetCmpAuto.argtypes = [c_uint32, c_double, c_double, c_double]
        Acm2_ChSetCmpAuto.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetCmpBufferData = lib.Acm2_ChSetCmpBufferData
        Acm2_ChSetCmpBufferData.argtypes = [c_uint32, POINTER(c_double), c_uint32]
        Acm2_ChSetCmpBufferData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetMultiCmpTable = lib.Acm2_ChSetMultiCmpTable
        Acm2_ChSetMultiCmpTable.argtypes = [c_uint32, c_uint, c_uint32]
        Acm2_ChSetMultiCmpTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetMultiCmpBufferData = lib.Acm2_ChSetMultiCmpBufferData
        Acm2_ChSetMultiCmpBufferData.argtypes = [c_uint32, POINTER(c_double), c_uint32, c_uint32]
        Acm2_ChSetMultiCmpBufferData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChResetCmpData = lib.Acm2_ChResetCmpData
        Acm2_ChResetCmpData.argtypes = [c_uint32]
        Acm2_ChResetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetCmpBufferStatus = lib.Acm2_ChGetCmpBufferStatus
        Acm2_ChGetCmpBufferStatus.argtypes = [c_uint32, POINTER(BUFFER_STATUS)]
        Acm2_ChGetCmpBufferStatus.restype = c_uint32
    except:
        pass
# Motion IO: Latch
    try:
        Acm2_ChLinkLatchAxis = lib.Acm2_ChLinkLatchAxis
        Acm2_ChLinkLatchAxis.argtypes = [c_uint32, POINTER(c_uint32), c_uint32]
        Acm2_ChLinkLatchAxis.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChLinkLatchObject = lib.Acm2_ChLinkLatchObject
        Acm2_ChLinkLatchObject.argtypes = [c_uint32, c_uint, POINTER(c_uint32), c_uint32]
        Acm2_ChLinkLatchObject.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetLinkedLatchObject = lib.Acm2_ChGetLinkedLatchObject
        Acm2_ChGetLinkedLatchObject.argtypes = [c_uint32, POINTER(c_uint),POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_ChGetLinkedLatchObject.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChTriggerLatch = lib.Acm2_ChTriggerLatch
        Acm2_ChTriggerLatch.argtypes = [c_uint32]
        Acm2_ChTriggerLatch.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxReadLatchBuffer = lib.Acm2_AxReadLatchBuffer
        Acm2_AxReadLatchBuffer.argtypes = [c_uint32, POINTER(c_double), POINTER(c_uint32)]
        Acm2_AxReadLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChReadLatchBuffer = lib.Acm2_ChReadLatchBuffer
        Acm2_ChReadLatchBuffer.argtypes = [c_uint32, POINTER(c_double), c_uint32, POINTER(c_uint32)]
        Acm2_ChReadLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetLatchBufferStatus = lib.Acm2_AxGetLatchBufferStatus
        Acm2_AxGetLatchBufferStatus.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_AxGetLatchBufferStatus.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetLatchBufferStatus = lib.Acm2_ChGetLatchBufferStatus
        Acm2_ChGetLatchBufferStatus.argtypes = [c_uint32, POINTER(BUFFER_STATUS)]
        Acm2_ChGetLatchBufferStatus.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxResetLatchBuffer = lib.Acm2_AxResetLatchBuffer
        Acm2_AxResetLatchBuffer.argtypes = [c_uint32]
        Acm2_AxResetLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChResetLatchBuffer = lib.Acm2_ChResetLatchBuffer
        Acm2_ChResetLatchBuffer.argtypes = [c_uint32]
        Acm2_ChResetLatchBuffer.restype = c_uint32
    except:
        pass
# Motion IO: PWM
    try:
        Acm2_ChLinkPWMTable = lib.Acm2_ChLinkPWMTable
        Acm2_ChLinkPWMTable.argtypes = [c_uint32, c_uint, c_uint32]
        Acm2_ChLinkPWMTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetLinkedPWMTable = lib.Acm2_ChGetLinkedPWMTable
        Acm2_ChGetLinkedPWMTable.argtypes = [c_uint32, POINTER(c_uint), POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_ChGetLinkedPWMTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetPWMTable = lib.Acm2_ChSetPWMTable
        Acm2_ChSetPWMTable.argtypes = [c_uint32, POINTER(c_double), POINTER(c_double), c_uint32]
        Acm2_ChSetPWMTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChLoadPWMTableFile = lib.Acm2_ChLoadPWMTableFile
        Acm2_ChLoadPWMTableFile.argtypes = [c_uint32, c_char_p, POINTER(c_uint32)]
        Acm2_ChLoadPWMTableFile.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetPWMTableStatus = lib.Acm2_ChGetPWMTableStatus
        Acm2_ChGetPWMTableStatus.argtypes = [c_uint32, POINTER(PWM_TABLE_STATUS)]
        Acm2_ChGetPWMTableStatus.restype = c_uint32
    except:
        pass
# Motion IO: External Drive
    try:
        Acm2_ChGetExtDriveData = lib.Acm2_ChGetExtDriveData
        Acm2_ChGetExtDriveData.argtypes = [c_uint32, POINTER(c_double)]
        Acm2_ChGetExtDriveData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChSetExtDriveData = lib.Acm2_ChSetExtDriveData
        Acm2_ChSetExtDriveData.argtypes = [c_uint32, c_double]
        Acm2_ChSetExtDriveData.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChLinkExtDriveObject = lib.Acm2_ChLinkExtDriveObject
        Acm2_ChLinkExtDriveObject.argtypes = [c_uint32, c_uint, c_uint32]
        Acm2_ChLinkExtDriveObject.restype = c_uint32
    except:
        pass

    try:
        Acm2_ChGetLinkedExtDriveObject = lib.Acm2_ChGetLinkedExtDriveObject
        Acm2_ChGetLinkedExtDriveObject.argtypes = [c_uint32, POINTER(c_uint), POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_ChGetLinkedExtDriveObject.restype = c_uint32
    except:
        pass
# Motion DAQ
    try:
        Acm2_DevMDaqConfig = lib.Acm2_DevMDaqConfig
        Acm2_DevMDaqConfig.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32]
        Acm2_DevMDaqConfig.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevMDaqGetConfig = lib.Acm2_DevMDaqGetConfig
        Acm2_DevMDaqGetConfig.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_DevMDaqGetConfig.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevMDaqStart = lib.Acm2_DevMDaqStart
        Acm2_DevMDaqStart.argtypes = [c_uint32]
        Acm2_DevMDaqStart.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevMDaqStop = lib.Acm2_DevMDaqStop
        Acm2_DevMDaqStop.argtypes = [c_uint32]
        Acm2_DevMDaqStop.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevMDaqReset = lib.Acm2_DevMDaqReset
        Acm2_DevMDaqReset.argtypes = [c_uint32]
        Acm2_DevMDaqReset.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevMDaqGetStatus = lib.Acm2_DevMDaqGetStatus
        Acm2_DevMDaqGetStatus.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_DevMDaqGetStatus.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevMDaqGetData = lib.Acm2_DevMDaqGetData
        Acm2_DevMDaqGetData.argtypes = [c_uint32, c_uint32, c_uint32, POINTER(c_double)]
        Acm2_DevMDaqGetData.restype = c_uint32
    except:
        pass
# # Donwload DSP FW
#     try:
#         Acm2_GetDSPFrmWareDwnLoadRate = lib.Acm2_GetDSPFrmWareDwnLoadRate
#         Acm2_GetDSPFrmWareDwnLoadRate.argtypes = [c_uint32, POINTER(c_double)]
#         Acm2_GetDSPFrmWareDwnLoadRate.restype = c_uint32
#     except:
#         pass

#     try:
#         Acm2_DevDownLoadDSPFrmWare_STP2 = lib.Acm2_DevDownLoadDSPFrmWare_STP2
#         Acm2_DevDownLoadDSPFrmWare_STP2.argtypes = [c_uint32, c_char_p]
#         Acm2_DevDownLoadDSPFrmWare_STP2.restype = c_uint32
#     except:
#         pass
# EtherCAT
    try:
        Acm2_DevLoadENI = lib.Acm2_DevLoadENI
        Acm2_DevLoadENI.argtypes = [c_uint32, c_char_p]
        Acm2_DevLoadENI.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevConnect = lib.Acm2_DevConnect
        Acm2_DevConnect.argtypes = [c_uint32]
        Acm2_DevConnect.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevDisConnect = lib.Acm2_DevDisConnect
        Acm2_DevDisConnect.argtypes = [c_uint32]
        Acm2_DevDisConnect.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetSubDevicesID = lib.Acm2_DevGetSubDevicesID
        Acm2_DevGetSubDevicesID.argtypes = [c_uint32, c_uint, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_DevGetSubDevicesID.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetMDeviceInfo = lib.Acm2_DevGetMDeviceInfo
        Acm2_DevGetMDeviceInfo.argtypes = [c_uint32, POINTER(ADVAPI_MDEVICE_INFO)]
        Acm2_DevGetMDeviceInfo.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetSubDeviceInfo = lib.Acm2_DevGetSubDeviceInfo
        Acm2_DevGetSubDeviceInfo.argtypes = [c_uint32, c_uint, c_uint32, POINTER(ADVAPI_SUBDEVICE_INFO_CM2)]
        Acm2_DevGetSubDeviceInfo.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetSubDeviceFwVersion = lib.Acm2_DevGetSubDeviceFwVersion
        Acm2_DevGetSubDeviceFwVersion.argtypes = [c_uint32, c_uint, c_uint32, c_char_p]
        Acm2_DevGetSubDeviceFwVersion.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevSetSubDeviceID = lib.Acm2_DevSetSubDeviceID
        Acm2_DevSetSubDeviceID.argtypes = [c_uint32, c_int, c_uint32, c_uint32]
        Acm2_DevSetSubDeviceID.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevSetSubDeviceStates = lib.Acm2_DevSetSubDeviceStates
        Acm2_DevSetSubDeviceStates.argtypes = [c_uint32, c_uint, c_uint32, POINTER(c_uint32)]
        Acm2_DevSetSubDeviceStates.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetSubDeviceStates = lib.Acm2_DevGetSubDeviceStates
        Acm2_DevGetSubDeviceStates.argtypes = [c_uint32, c_uint, c_uint32, POINTER(c_uint32)]
        Acm2_DevGetSubDeviceStates.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevWriteSDO = lib.Acm2_DevWriteSDO
        Acm2_DevWriteSDO.argtypes = [c_uint32, c_uint, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
        Acm2_DevWriteSDO.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevReadSDO = lib.Acm2_DevReadSDO
        Acm2_DevReadSDO.argtypes = [c_uint32, c_uint, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
        Acm2_DevReadSDO.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevWritePDO = lib.Acm2_DevWritePDO
        Acm2_DevWritePDO.argtypes = [c_uint32, c_uint, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
        Acm2_DevWritePDO.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevReadPDO = lib.Acm2_DevReadPDO
        Acm2_DevReadPDO.argtypes = [c_uint32, c_uint, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
        Acm2_DevReadPDO.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevWriteReg = lib.Acm2_DevWriteReg
        Acm2_DevWriteReg.argtypes = [c_uint32, c_uint, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
        Acm2_DevWriteReg.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevReadReg = lib.Acm2_DevReadReg
        Acm2_DevReadReg.argtypes = [c_uint32, c_uint, c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
        Acm2_DevReadReg.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevReadSubDeviceCommErrCnt = lib.Acm2_DevReadSubDeviceCommErrCnt
        Acm2_DevReadSubDeviceCommErrCnt.argtypes = [c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
        Acm2_DevReadSubDeviceCommErrCnt.restype = c_uint32
    except:
        pass

    try:
        Acm2_Ax1DCompensateTable = lib.Acm2_Ax1DCompensateTable
        Acm2_Ax1DCompensateTable.argtypes = [c_uint32, c_double, c_double, POINTER(c_double), c_uint32, c_uint32]
        Acm2_Ax1DCompensateTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_Ax2DCompensateTable = lib.Acm2_Ax2DCompensateTable
        Acm2_Ax2DCompensateTable.argtypes = [c_uint32, c_uint32, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), c_uint32, c_uint32]
        Acm2_Ax2DCompensateTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxZAxisCompensateTable = lib.Acm2_AxZAxisCompensateTable
        Acm2_AxZAxisCompensateTable.argtypes = [c_uint32, c_uint32, c_uint32, c_double, c_double, c_double, c_double, POINTER(c_double), c_uint32, c_uint32]
        Acm2_AxZAxisCompensateTable.restype = c_uint32
    except:
        pass

    try:
        Acm2_AxGetCompensatePosition = lib.Acm2_AxGetCompensatePosition
        Acm2_AxGetCompensatePosition.argtypes = [c_uint32, POINTER(c_double)]
        Acm2_AxGetCompensatePosition.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevOscChannelDataStart = lib.Acm2_DevOscChannelDataStart
        Acm2_DevOscChannelDataStart.argtypes = [c_uint32]
        Acm2_DevOscChannelDataStart.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevOscChannelDataStop = lib.Acm2_DevOscChannelDataStop
        Acm2_DevOscChannelDataStop.argtypes = [c_uint32]
        Acm2_DevOscChannelDataStop.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetOscChannelDataConfig = lib.Acm2_DevGetOscChannelDataConfig
        Acm2_DevGetOscChannelDataConfig.argtypes = [c_uint32, c_uint16, POINTER(OSC_PROFILE_PRM)]
        Acm2_DevGetOscChannelDataConfig.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevSetOscChannelDataConfig = lib.Acm2_DevSetOscChannelDataConfig
        Acm2_DevSetOscChannelDataConfig.argtypes = [c_uint32, c_uint16, OSC_PROFILE_PRM]
        Acm2_DevSetOscChannelDataConfig.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetOscChannelData = lib.Acm2_DevGetOscChannelData
        Acm2_DevGetOscChannelData.argtypes = [c_uint32, c_uint16, c_uint32, POINTER(c_uint32), POINTER(c_double)]
        Acm2_DevGetOscChannelData.restype = c_uint32
    except:
        pass

    try:
        Acm2_DevGetOscChannelStatus = lib.Acm2_DevGetOscChannelStatus
        Acm2_DevGetOscChannelStatus.argtypes = [c_uint32, POINTER(c_uint32)]
        Acm2_DevGetOscChannelStatus.restype = c_uint32
    except:
        pass

class AdvCmnAPI:
# Device
    try:
        Acm_GetAvailableDevs = lib.Acm_GetAvailableDevs
        Acm_GetAvailableDevs.argtypes = [POINTER(DEVLIST), c_uint32, POINTER(c_uint32)]
        Acm_GetAvailableDevs.restype = c_uint32
    except:
        pass

    try:
        Acm_GetErrorMessage = lib.Acm_GetErrorMessage
        Acm_GetErrorMessage.argtypes = [c_uint32, c_char_p, c_uint32]
        Acm_GetErrorMessage.restype = c_bool
    except:
        pass

    try:
        Acm_DevOpen = lib.Acm_DevOpen
        Acm_DevOpen.argtypes = [c_uint32, POINTER(c_void_p)]
        Acm_DevOpen.restype = c_uint32
    except:
        pass

    try:
        Acm_DevECATOpen = lib.Acm_DevECATOpen
        Acm_DevECATOpen.argtypes = [c_uint32, c_uint16, c_uint16, c_uint16, POINTER(c_void_p)]
        Acm_DevECATOpen.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReOpen = lib.Acm_DevReOpen
        # Acm_DevReOpen.argtypes = [HANDLE]
        Acm_DevReOpen.argtypes = [c_void_p]
        Acm_DevReOpen.restype = c_uint32
    except:
        pass

    try:
        Acm_DevClose = lib.Acm_DevClose
        # Acm_DevClose.argtypes = [POINTER(HANDLE)]
        Acm_DevClose.argtypes = [POINTER(c_void_p)]
        Acm_DevClose.restype = c_uint32
    except:
        pass

    try:
        Acm_GetLastError = lib.Acm_GetLastError
        Acm_GetLastError.argtypes = [c_void_p]
        Acm_GetLastError.restype = c_uint32
    except:
        pass

    try:
        Acm_GetProperty = lib.Acm_GetProperty
        Acm_GetProperty.argtypes = [c_void_p, c_uint32, c_void_p, POINTER(c_uint32)]
        Acm_GetProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_SetProperty = lib.Acm_SetProperty
        Acm_SetProperty.argtypes = [c_void_p, c_uint32, c_void_p, c_uint32]
        Acm_SetProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_GetU32Property = lib.Acm_GetU32Property
        Acm_GetU32Property.argtypes = [c_void_p, c_uint32, POINTER(c_uint32)]
        Acm_GetU32Property.restype = c_uint32
    except:
        pass

    try:
        Acm_GetI32Property = lib.Acm_GetI32Property
        Acm_GetI32Property.argtypes = [c_void_p, c_uint32, POINTER(c_int32)]
        Acm_GetI32Property.restype = c_uint32
    except:
        pass

    try:
        Acm_GetF64Property = lib.Acm_GetF64Property
        Acm_GetF64Property.argtypes = [c_void_p, c_uint32, POINTER(c_double)]
        Acm_GetF64Property.restype = c_uint32
    except:
        pass

    try:
        Acm_GetStringProperty = lib.Acm_GetStringProperty
        Acm_GetStringProperty.argtypes = [c_void_p, c_uint32, POINTER(c_uint8)]
        Acm_GetStringProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_SetU32Property = lib.Acm_SetU32Property
        Acm_SetU32Property.argtypes = [c_void_p, c_uint32, c_uint32]
        Acm_SetU32Property.restype = c_uint32
    except:
        pass

    try:
        Acm_SetI32Property = lib.Acm_SetI32Property
        Acm_SetI32Property.argtypes = [c_void_p, c_uint32, c_int32]
        Acm_SetI32Property.restype = c_uint32
    except:
        pass

    try:
        Acm_SetF64Property = lib.Acm_SetF64Property
        Acm_SetF64Property.argtypes = [c_void_p, c_uint32, c_double]
        Acm_SetF64Property.restype = c_uint32
    except:
        pass

    try:
        Acm_SetStringProperty = lib.Acm_SetStringProperty
        Acm_SetStringProperty.argtypes = [c_void_p, c_uint32, POINTER(c_uint8)]
        Acm_SetStringProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_GetMultiProperty = lib.Acm_GetMultiProperty
        Acm_GetMultiProperty.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_double), c_uint32, POINTER(c_uint32)]
        Acm_GetMultiProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_SetMultiU32Property = lib.Acm_SetMultiU32Property
        Acm_SetMultiU32Property.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), c_uint32]
        Acm_SetMultiU32Property.restype = c_uint32
    except:
        pass

    try:
        Acm_SetMultiI32Property = lib.Acm_SetMultiI32Property
        Acm_SetMultiI32Property.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_int32), c_uint32]
        Acm_SetMultiI32Property.restype = c_uint32
    except:
        pass

    try:
        Acm_SetMultiF64Property = lib.Acm_SetMultiF64Property
        Acm_SetMultiF64Property.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_double), c_uint32]
        Acm_SetMultiF64Property.restype = c_uint32
    except:
        pass

    try:
        Acm_GetChannelProperty = lib.Acm_GetChannelProperty
        Acm_GetChannelProperty.argtypes = [c_void_p, c_uint32, c_uint32, POINTER(c_double)]
        Acm_GetChannelProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_SetChannelProperty = lib.Acm_SetChannelProperty
        Acm_SetChannelProperty.argtypes = [c_void_p, c_uint32, c_uint32, c_double]
        Acm_SetChannelProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_GetMultiChannelProperty = lib.Acm_GetMultiChannelProperty
        Acm_GetMultiChannelProperty.argtypes = [c_void_p, c_uint32, c_uint32, c_uint32, POINTER(c_double)]
        Acm_GetMultiChannelProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_SetMultiChannelProperty = lib.Acm_SetMultiChannelProperty
        Acm_SetMultiChannelProperty.argtypes = [c_void_p, c_uint32, c_uint32, c_uint32, POINTER(c_double)]
        Acm_SetMultiChannelProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_DevEnableEvent = lib.Acm_DevEnableEvent
        Acm_DevEnableEvent.argtypes = [c_void_p, c_uint32]
        Acm_DevEnableEvent.restype = c_uint32
    except:
        pass

    try:
        Acm_DevCheckEvent = lib.Acm_DevCheckEvent
        Acm_DevCheckEvent.argtypes = [c_void_p, POINTER(c_uint32), c_uint32]
        Acm_DevCheckEvent.restype = c_uint32
    except:
        pass

    try:
        Acm_EnableMotionEvent = lib.Acm_EnableMotionEvent
        Acm_EnableMotionEvent.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), c_uint32, c_uint32]
        Acm_EnableMotionEvent.restype = c_uint32
    except:
        pass

    try:
        Acm_CheckMotionEvent = lib.Acm_CheckMotionEvent
        Acm_CheckMotionEvent.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), c_uint32, c_uint32, c_uint32]
        Acm_CheckMotionEvent.restype = c_uint32
    except:
        pass

    try:
        Acm_CancelCheckEvent = lib.Acm_CancelCheckEvent
        Acm_CancelCheckEvent.argtypes = [c_void_p]
        Acm_CancelCheckEvent.restype = c_uint32
    except:
        pass

    try:
        Acm_DevEnableEvent_All = lib.Acm_DevEnableEvent_All
        Acm_DevEnableEvent_All.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), c_uint32, c_uint32]
        Acm_DevEnableEvent_All.restype = c_uint32
    except:
        pass

    try:
        Acm_DevCheckEvent_All = lib.Acm_DevCheckEvent_All
        Acm_DevCheckEvent_All.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), c_uint32, c_uint32, c_uint32]
        Acm_DevCheckEvent_All.restype = c_uint32
    except:
        pass

    try:
        Acm_DevLoadConfig = lib.Acm_DevLoadConfig
        Acm_DevLoadConfig.argtypes = [c_void_p, c_uint32, c_uint32]
        Acm_DevLoadConfig.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSlaveFwDownload = lib.Acm_DevSlaveFwDownload
        Acm_DevSlaveFwDownload.argtypes = [c_void_p, c_uint16, c_uint16, c_char_p, c_char_p, c_uint32]
        Acm_DevSlaveFwDownload.restype = c_uint32
    except:
        pass

    # try:
    #     Acm_DevDownloadCAMTable = lib.Acm_DevDownloadCAMTable
    #     Acm_DevDownloadCAMTable.argtypes = [c_void_p, c_uint32, POINTER(c_double), POINTER(c_double),
    #                                         POINTER(c_double), POINTER(c_double), c_uint32]
    #     Acm_DevDownloadCAMTable.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_DevLoadCAMTableFile = lib.Acm_DevLoadCAMTableFile
    #     Acm_DevLoadCAMTableFile.argtypes = [c_void_p, c_char_p, c_uint32, POINTER(c_uint32), POINTER(c_uint32)]
    #     Acm_DevLoadCAMTableFile.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_DevConfigCAMTable = lib.Acm_DevConfigCAMTable
    #     Acm_DevConfigCAMTable.argtypes = [c_void_p, c_uint32, c_uint32, c_uint32, c_uint32]
    #     Acm_DevConfigCAMTable.restype = c_uint32
    # except:
    #     pass

    try:
        Acm_DevReadMailBox = lib.Acm_DevReadMailBox
        Acm_DevReadMailBox.argtypes = [c_void_p, c_uint16, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm_DevReadMailBox.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReadMultiMailBox = lib.Acm_DevReadMultiMailBox
        Acm_DevReadMultiMailBox.argtypes = [c_void_p, c_uint8, POINTER(c_uint16), POINTER(c_uint32), POINTER(c_uint32), c_uint32]
        Acm_DevReadMultiMailBox.restype = c_uint32
    except:
        pass

    try:
        Acm_DevWriteMailBox = lib.Acm_DevWriteMailBox
        Acm_DevWriteMailBox.argtypes = [c_void_p, c_uint16, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm_DevWriteMailBox.restype = c_uint32
    except:
        pass

    try:
        Acm_DevWriteDPMData = lib.Acm_DevWriteDPMData
        Acm_DevWriteDPMData.argtypes = [c_void_p, c_uint16, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm_DevWriteDPMData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevWriteMultiMailBox = lib.Acm_DevWriteMultiMailBox
        Acm_DevWriteMultiMailBox.argtypes = [c_void_p, c_uint8, POINTER(c_uint16), POINTER(c_uint32), POINTER(c_uint32), c_uint32]
        Acm_DevWriteMultiMailBox.restype = c_uint32
    except:
        pass

    try:
        Acm_WriteRingBuffer = lib.Acm_WriteRingBuffer
        Acm_WriteRingBuffer.argtypes = [c_void_p, c_uint32, c_uint32, c_uint32, POINTER(c_uint32)]
        Acm_WriteRingBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_ReadRingBuffer = lib.Acm_ReadRingBuffer
        Acm_ReadRingBuffer.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), c_uint32, POINTER(c_uint32)]
        Acm_ReadRingBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_LoadENI = lib.Acm_LoadENI
        Acm_LoadENI.argtypes = [c_void_p, c_char_p]
        Acm_LoadENI.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetComStatus = lib.Acm_DevGetComStatus
        Acm_DevGetComStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DevGetComStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetErrorTable = lib.Acm_DevGetErrorTable
        Acm_DevGetErrorTable.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DevGetErrorTable.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetMasInfo = lib.Acm_DevGetMasInfo
        Acm_DevGetMasInfo.argtypes = [c_void_p, c_void_p, POINTER(c_uint16), POINTER(c_uint32)]
        Acm_DevGetMasInfo.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetMasStates = lib.Acm_DevGetMasStates
        Acm_DevGetMasStates.argtypes = [c_void_p, c_uint16, POINTER(c_uint16), POINTER(c_uint16)]
        Acm_DevGetMasStates.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveInfo = lib.Acm_DevGetSlaveInfo
        Acm_DevGetSlaveInfo.argtypes = [c_void_p, c_uint16, c_uint16, c_void_p]
        Acm_DevGetSlaveInfo.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetModuleInfo = lib.Acm_DevGetModuleInfo
        Acm_DevGetModuleInfo.argtypes = [c_void_p, c_uint16, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DevGetModuleInfo.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetIOInfo = lib.Acm_DevGetIOInfo
        Acm_DevGetIOInfo.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint8, c_void_p]
        Acm_DevGetIOInfo.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveDataCnt = lib.Acm_DevGetSlaveDataCnt
        Acm_DevGetSlaveDataCnt.argtypes = [c_void_p, c_uint16, c_uint16, c_uint8, POINTER(c_uint32)]
        Acm_DevGetSlaveDataCnt.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveFwVersion = lib.Acm_DevGetSlaveFwVersion
        Acm_DevGetSlaveFwVersion.argtypes = [c_void_p, c_uint16, c_uint16, c_char_p]
        Acm_DevGetSlaveFwVersion.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetSlaveID = lib.Acm_DevSetSlaveID
        Acm_DevSetSlaveID.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DevSetSlaveID.restype = c_uint32
    except:
        pass

    try:
        Acm_CheckVersion = lib.Acm_CheckVersion
        Acm_CheckVersion.argtypes = [c_void_p, c_uint32, POINTER(c_uint32)]
        Acm_CheckVersion.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMultiTrigSetPWMTableOnTime = lib.Acm_DevMultiTrigSetPWMTableOnTime
        Acm_DevMultiTrigSetPWMTableOnTime.argtypes = [c_void_p, POINTER(c_uint32), c_uint32]
        Acm_DevMultiTrigSetPWMTableOnTime.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMultiTrigSetCmpDO = lib.Acm_DevMultiTrigSetCmpDO
        Acm_DevMultiTrigSetCmpDO.argtypes = [c_void_p, c_uint32]
        Acm_DevMultiTrigSetCmpDO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMultiTrigForceCmpOut = lib.Acm_DevMultiTrigForceCmpOut
        Acm_DevMultiTrigForceCmpOut.argtypes = [c_void_p, c_uint32]
        Acm_DevMultiTrigForceCmpOut.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMutiTrigSetCmpDO = lib.Acm_DevMutiTrigSetCmpDO
        Acm_DevMutiTrigSetCmpDO.argtypes = [c_void_p, c_uint32]
        Acm_DevMutiTrigSetCmpDO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMutiTrigForceCmpOut = lib.Acm_DevMutiTrigForceCmpOut
        Acm_DevMutiTrigForceCmpOut.argtypes = [c_void_p, c_uint32]
        Acm_DevMutiTrigForceCmpOut.restype = c_uint32
    except:
        pass

    try:
        Acm_MasStartRing = lib.Acm_MasStartRing
        Acm_MasStartRing.argtypes = [c_void_p, c_uint16]
        Acm_MasStartRing.restype = c_uint32
    except:
        pass

    try:
        Acm_MasStopRing = lib.Acm_MasStopRing
        Acm_MasStopRing.argtypes = [c_void_p, c_uint16]
        Acm_MasStopRing.restype = c_uint32
    except:
        pass

    try:
        Acm_MasGetComStatus = lib.Acm_MasGetComStatus
        Acm_MasGetComStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_MasGetComStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_MasGetComCyclicTime = lib.Acm_MasGetComCyclicTime
        Acm_MasGetComCyclicTime.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_MasGetComCyclicTime.restype = c_uint32
    except:
        pass

    try:
        Acm_MasGetDataCyclicTime = lib.Acm_MasGetDataCyclicTime
        Acm_MasGetDataCyclicTime.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_MasGetDataCyclicTime.restype = c_uint32
    except:
        pass

    try:
        Acm_MasGetActiveTable = lib.Acm_MasGetActiveTable
        Acm_MasGetActiveTable.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_MasGetActiveTable.restype = c_uint32
    except:
        pass

    try:
        Acm_MasGetErrorTable = lib.Acm_MasGetErrorTable
        Acm_MasGetErrorTable.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_MasGetErrorTable.restype = c_uint32
    except:
        pass

    try:
        Acm_MasGetSlaveInfo = lib.Acm_MasGetSlaveInfo
        Acm_MasGetSlaveInfo.argtypes = [c_void_p, c_uint16, c_uint16, POINTER(c_uint32)]
        Acm_MasGetSlaveInfo.restype = c_uint32
    except:
        pass

    try:
        Acm_MasLogComStatus = lib.Acm_MasLogComStatus
        Acm_MasLogComStatus.argtypes = [c_void_p, c_uint16]
        Acm_MasLogComStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DevDownloadScanData = lib.Acm_DevDownloadScanData
        Acm_DevDownloadScanData.argtypes = [c_void_p, POINTER(DEV_PRE_SCAN_DATA), c_uint32]
        Acm_DevDownloadScanData.restype = c_uint32
    except:
        pass
# Axis
    try:
        Acm_AxOpen = lib.Acm_AxOpen
        Acm_AxOpen.argtypes = [c_void_p, c_uint16, POINTER(c_void_p)]
        Acm_AxOpen.restype = c_uint32
    except:
        pass

    try:
        Acm_AxOpenbyID = lib.Acm_AxOpenbyID
        Acm_AxOpenbyID.argtypes = [c_void_p, c_uint16, c_uint8, POINTER(c_void_p)]
        Acm_AxOpenbyID.restype = c_uint32
    except:
        pass

    try:
        Acm_AxClose = lib.Acm_AxClose
        Acm_AxClose.argtypes = [POINTER(c_void_p)]
        Acm_AxClose.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetSvOn = lib.Acm_AxSetSvOn
        Acm_AxSetSvOn.argtypes = [c_void_p, c_uint32]
        Acm_AxSetSvOn.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetAlm = lib.Acm_AxResetAlm
        Acm_AxResetAlm.argtypes = [c_void_p, c_uint32]
        Acm_AxResetAlm.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveRel = lib.Acm_AxMoveRel
        Acm_AxMoveRel.argtypes = [c_void_p, c_double]
        Acm_AxMoveRel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveRel_T = lib.Acm_AxMoveRel_T
        Acm_AxMoveRel_T.argtypes = [c_void_p, c_double, c_double, c_double]
        Acm_AxMoveRel_T.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveRel_SD = lib.Acm_AxMoveRel_SD
        Acm_AxMoveRel_SD.argtypes = [c_void_p, c_double, c_double]
        Acm_AxMoveRel_SD.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveRel_EC = lib.Acm_AxMoveRel_EC
        Acm_AxMoveRel_EC.argtypes = [c_void_p, c_double]
        Acm_AxMoveRel_EC.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveAbs = lib.Acm_AxMoveAbs
        Acm_AxMoveAbs.argtypes = [c_void_p, c_double]
        Acm_AxMoveAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveAbs_T = lib.Acm_AxMoveAbs_T
        Acm_AxMoveAbs_T.argtypes = [c_void_p, c_double, c_double, c_double]
        Acm_AxMoveAbs_T.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveAbs_SD = lib.Acm_AxMoveAbs_SD
        Acm_AxMoveAbs_SD.argtypes = [c_void_p, c_double, c_double]
        Acm_AxMoveAbs_SD.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveAbs_EC = lib.Acm_AxMoveAbs_EC
        Acm_AxMoveAbs_EC.argtypes = [c_void_p, c_double]
        Acm_AxMoveAbs_EC.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveVel = lib.Acm_AxMoveVel
        Acm_AxMoveVel.argtypes = [c_void_p, c_uint16]
        Acm_AxMoveVel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStopDec = lib.Acm_AxStopDec
        Acm_AxStopDec.argtypes = [c_void_p]
        Acm_AxStopDec.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStopDecEx = lib.Acm_AxStopDecEx
        Acm_AxStopDecEx.argtypes = [c_void_p, c_double]
        Acm_AxStopDecEx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStopEmg = lib.Acm_AxStopEmg
        Acm_AxStopEmg.argtypes = [c_void_p]
        Acm_AxStopEmg.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveImpose = lib.Acm_AxMoveImpose
        Acm_AxMoveImpose.argtypes = [c_void_p, c_double, c_double]
        Acm_AxMoveImpose.restype = c_uint32
    except:
        pass

    try:
        Acm_AxHomeEx = lib.Acm_AxHomeEx
        Acm_AxHomeEx.argtypes = [c_void_p, c_uint32]
        Acm_AxHomeEx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxHome = lib.Acm_AxHome
        Acm_AxHome.argtypes = [c_void_p, c_uint32, c_uint32]
        Acm_AxHome.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveHome = lib.Acm_AxMoveHome
        Acm_AxMoveHome.argtypes = [c_void_p, c_uint32, c_uint32]
        Acm_AxMoveHome.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveGantryHome = lib.Acm_AxMoveGantryHome
        Acm_AxMoveGantryHome.argtypes = [c_void_p, c_uint32, c_uint32]
        Acm_AxMoveGantryHome.restype = c_uint32
    except:
        pass

    try:
        Acm_AxChangeVel = lib.Acm_AxChangeVel
        Acm_AxChangeVel.argtypes = [c_void_p, c_double]
        Acm_AxChangeVel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxChangePos = lib.Acm_AxChangePos
        Acm_AxChangePos.argtypes = [c_void_p, c_double]
        Acm_AxChangePos.restype = c_uint32
    except:
        pass

    try:
        Acm_AxChangeVelByRate = lib.Acm_AxChangeVelByRate
        Acm_AxChangeVelByRate.argtypes = [c_void_p, c_uint32]
        Acm_AxChangeVelByRate.restype = c_uint32
    except:
        pass

    try:
        Acm_AxChangeVelEx = lib.Acm_AxChangeVelEx
        Acm_AxChangeVelEx.argtypes = [c_void_p, c_double, c_double, c_double]
        Acm_AxChangeVelEx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxChangeVelExByRate = lib.Acm_AxChangeVelExByRate
        Acm_AxChangeVelExByRate.argtypes = [c_void_p, c_uint32, c_double, c_double]
        Acm_AxChangeVelExByRate.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetError = lib.Acm_AxResetError
        Acm_AxResetError.argtypes = [c_void_p]
        Acm_AxResetError.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetState = lib.Acm_AxGetState
        Acm_AxGetState.argtypes = [c_void_p, POINTER(c_uint16)]
        Acm_AxGetState.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetMotionIO = lib.Acm_AxGetMotionIO
        Acm_AxGetMotionIO.argtypes = [c_void_p, POINTER(c_uint32)]
        Acm_AxGetMotionIO.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetMotionStatus = lib.Acm_AxGetMotionStatus
        Acm_AxGetMotionStatus.argtypes = [c_void_p, POINTER(c_uint32)]
        Acm_AxGetMotionStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCmdPosition = lib.Acm_AxGetCmdPosition
        Acm_AxGetCmdPosition.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetCmdPosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetMachPosition = lib.Acm_AxGetMachPosition
        Acm_AxGetMachPosition.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetMachPosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmdPosition = lib.Acm_AxSetCmdPosition
        Acm_AxSetCmdPosition.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxSetCmdPosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetActualPosition = lib.Acm_AxGetActualPosition
        Acm_AxGetActualPosition.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetActualPosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetActualPosition = lib.Acm_AxSetActualPosition
        Acm_AxSetActualPosition.argtypes = [c_void_p, c_double]
        Acm_AxSetActualPosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCmdVelocity = lib.Acm_AxGetCmdVelocity
        Acm_AxGetCmdVelocity.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetCmdVelocity.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetActVelocity = lib.Acm_AxGetActVelocity
        Acm_AxGetActVelocity.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetActVelocity.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetLagCounter = lib.Acm_AxGetLagCounter
        Acm_AxGetLagCounter.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetLagCounter.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetExtDrive = lib.Acm_AxSetExtDrive
        Acm_AxSetExtDrive.argtypes = [c_void_p, c_uint16]
        Acm_AxSetExtDrive.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDoSetBit = lib.Acm_AxDoSetBit
        Acm_AxDoSetBit.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_AxDoSetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDiSetBit = lib.Acm_AxDiSetBit
        Acm_AxDiSetBit.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_AxDiSetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDoGetBit = lib.Acm_AxDoGetBit
        Acm_AxDoGetBit.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_AxDoGetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDiGetBit = lib.Acm_AxDiGetBit
        Acm_AxDiGetBit.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_AxDiGetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDoSetByte = lib.Acm_AxDoSetByte
        Acm_AxDoSetByte.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_AxDoSetByte.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDoGetByte = lib.Acm_AxDoGetByte
        Acm_AxDoGetByte.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_AxDoGetByte.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDiGetByte = lib.Acm_AxDiGetByte
        Acm_AxDiGetByte.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_AxDiGetByte.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSimStartSuspendVel = lib.Acm_AxSimStartSuspendVel
        Acm_AxSimStartSuspendVel.argtypes = [c_void_p, c_uint16]
        Acm_AxSimStartSuspendVel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSimStartSuspendRel = lib.Acm_AxSimStartSuspendRel
        Acm_AxSimStartSuspendRel.argtypes = [c_void_p, c_double]
        Acm_AxSimStartSuspendRel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSimStartSuspendAbs = lib.Acm_AxSimStartSuspendAbs
        Acm_AxSimStartSuspendAbs.argtypes = [c_void_p, c_double]
        Acm_AxSimStartSuspendAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSimStart = lib.Acm_AxSimStart
        Acm_AxSimStart.argtypes = [c_void_p]
        Acm_AxSimStart.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSimStop = lib.Acm_AxSimStop
        Acm_AxSimStop.argtypes = [c_void_p]
        Acm_AxSimStop.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetLatchData = lib.Acm_AxGetLatchData
        Acm_AxGetLatchData.argtypes = [c_void_p, c_uint32, POINTER(c_double)]
        Acm_AxGetLatchData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStartSoftLatch = lib.Acm_AxStartSoftLatch
        Acm_AxStartSoftLatch.argtypes = [c_void_p]
        Acm_AxStartSoftLatch.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetLatch = lib.Acm_AxResetLatch
        Acm_AxResetLatch.argtypes = [c_void_p]
        Acm_AxResetLatch.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetLatchFlag = lib.Acm_AxGetLatchFlag
        Acm_AxGetLatchFlag.argtypes = [c_void_p, POINTER(c_uint8)]
        Acm_AxGetLatchFlag.restype = c_uint32
    except:
        pass

    try:
        Acm_AxTriggerLatch = lib.Acm_AxTriggerLatch
        Acm_AxTriggerLatch.argtypes = [c_void_p]
        Acm_AxTriggerLatch.restype = c_uint32
    except:
        pass

    try:
        Acm_AxReadLatchBuffer = lib.Acm_AxReadLatchBuffer
        Acm_AxReadLatchBuffer.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
        Acm_AxReadLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetLatchBuffer = lib.Acm_AxResetLatchBuffer
        Acm_AxResetLatchBuffer.argtypes = [c_void_p]
        Acm_AxResetLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetLatchBufferStatus = lib.Acm_AxGetLatchBufferStatus
        Acm_AxGetLatchBufferStatus.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_AxGetLatchBufferStatus.restype = c_uint32
    except:
        pass

    # try:
    #     Acm_AxCamInAx = lib.Acm_AxCamInAx
    #     Acm_AxCamInAx.argtypes = [c_void_p, c_void_p, c_double, c_double, c_double, c_double, c_uint32, c_uint32]
    #     Acm_AxCamInAx.restype = c_uint32
    # except:
    #     pass

    try:
        Acm_AxGearInAx = lib.Acm_AxGearInAx
        Acm_AxGearInAx.argtypes = [c_void_p, c_void_p, c_int32, c_int32, c_uint32, c_uint32]
        Acm_AxGearInAx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxTangentInGp = lib.Acm_AxTangentInGp
        Acm_AxTangentInGp.argtypes = [c_void_p, c_void_p, POINTER(c_int16), c_uint8, c_int16]
        Acm_AxTangentInGp.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGantryInAx = lib.Acm_AxGantryInAx
        Acm_AxGantryInAx.argtypes = [c_void_p, c_void_p, c_int16, c_int16]
        Acm_AxGantryInAx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxPhaseAx = lib.Acm_AxPhaseAx
        Acm_AxPhaseAx.argtypes = [c_void_p, c_double, c_double, c_double, c_double]
        Acm_AxPhaseAx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetChannelCmpSetting = lib.Acm_AxSetChannelCmpSetting
        Acm_AxSetChannelCmpSetting.argtypes = [c_void_p, c_uint16, c_uint32, c_uint32, c_uint32, c_uint32]
        Acm_AxSetChannelCmpSetting.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetChannelCmpSetting = lib.Acm_AxGetChannelCmpSetting
        Acm_AxGetChannelCmpSetting.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm_AxGetChannelCmpSetting.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetChannelCmp = lib.Acm_AxResetChannelCmp
        Acm_AxResetChannelCmp.argtypes = [c_void_p, c_uint16]
        Acm_AxResetChannelCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_AxAddChannelCmpDatas = lib.Acm_AxAddChannelCmpDatas
        Acm_AxAddChannelCmpDatas.argtypes = [c_void_p, c_uint16, POINTER(c_double), c_uint32]
        Acm_AxAddChannelCmpDatas.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetChannelCmpData = lib.Acm_AxGetChannelCmpData
        Acm_AxGetChannelCmpData.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_AxGetChannelCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxLoadChannelNextData = lib.Acm_AxLoadChannelNextData
        Acm_AxLoadChannelNextData.argtypes = [c_void_p, c_uint16]
        Acm_AxLoadChannelNextData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCmpbufferRemainCount = lib.Acm_AxGetCmpbufferRemainCount
        Acm_AxGetCmpbufferRemainCount.argtypes = [c_void_p, c_uint16, POINTER(c_uint32)]
        Acm_AxGetCmpbufferRemainCount.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmpAuto = lib.Acm_AxSetCmpAuto
        Acm_AxSetCmpAuto.argtypes = [c_void_p, c_double, c_double, c_double]
        Acm_AxSetCmpAuto.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCmpData = lib.Acm_AxGetCmpData
        Acm_AxGetCmpData.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmpData = lib.Acm_AxSetCmpData
        Acm_AxSetCmpData.argtypes = [c_void_p, c_double]
        Acm_AxSetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmpTable = lib.Acm_AxSetCmpTable
        Acm_AxSetCmpTable.argtypes = [c_void_p, POINTER(c_double), c_int32]
        Acm_AxSetCmpTable.restype = c_uint32
    except:
        pass

    try:
        Acm_AxChangeCmpIndex = lib.Acm_AxChangeCmpIndex
        Acm_AxChangeCmpIndex.argtypes = [c_void_p, c_uint32]
        Acm_AxChangeCmpIndex.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmpBufferData = lib.Acm_AxSetCmpBufferData
        Acm_AxSetCmpBufferData.argtypes = [c_void_p, POINTER(c_double), c_int32]
        Acm_AxSetCmpBufferData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetCmpData = lib.Acm_AxResetCmpData
        Acm_AxResetCmpData.argtypes = [c_void_p]
        Acm_AxResetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCmpBufferStatus = lib.Acm_AxGetCmpBufferStatus
        Acm_AxGetCmpBufferStatus.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm_AxGetCmpBufferStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetMPGOffset = lib.Acm_AxResetMPGOffset
        Acm_AxResetMPGOffset.argtypes = [c_void_p]
        Acm_AxResetMPGOffset.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMovePTPBufferRel = lib.Acm_AxMovePTPBufferRel
        Acm_AxMovePTPBufferRel.argtypes = [c_void_p, c_uint16, POINTER(c_double), POINTER(c_double),
                                           POINTER(c_double), POINTER(c_uint16), c_uint32]
        Acm_AxMovePTPBufferRel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMovePTPBufferAbs = lib.Acm_AxMovePTPBufferAbs
        Acm_AxMovePTPBufferAbs.argtypes = [c_void_p, c_uint16, POINTER(c_double), POINTER(c_double),
                                           POINTER(c_double), POINTER(c_uint16), c_uint32]
        Acm_AxMovePTPBufferAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_AxEnableCompensation = lib.Acm_AxEnableCompensation
        Acm_AxEnableCompensation.argtypes = [c_void_p, c_double]
        Acm_AxEnableCompensation.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCompensationValue = lib.Acm_AxGetCompensationValue
        Acm_AxGetCompensationValue.argtypes = [c_void_p, c_double, c_double, c_double]
        Acm_AxGetCompensationValue.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCompenPara = lib.Acm_AxSetCompenPara
        Acm_AxSetCompenPara.argtypes = [c_void_p, c_void_p, c_uint32, c_uint32, c_uint32]
        Acm_AxSetCompenPara.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDIStartMoveAbs = lib.Acm_AxDIStartMoveAbs
        Acm_AxDIStartMoveAbs.argtypes = [c_void_p, c_uint16, c_double]
        Acm_AxDIStartMoveAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDIStartMoveRel = lib.Acm_AxDIStartMoveRel
        Acm_AxDIStartMoveRel.argtypes = [c_void_p, c_uint16, c_double]
        Acm_AxDIStartMoveRel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDIStartMoveVel = lib.Acm_AxDIStartMoveVel
        Acm_AxDIStartMoveVel.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_AxDIStartMoveVel.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDisableDIStart = lib.Acm_AxDisableDIStart
        Acm_AxDisableDIStart.argtypes = [c_void_p]
        Acm_AxDisableDIStart.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetPWMTableOnTime = lib.Acm_AxSetPWMTableOnTime
        Acm_AxSetPWMTableOnTime.argtypes = [c_void_p, POINTER(c_uint32), c_int32]
        Acm_AxSetPWMTableOnTime.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetINxStopStatus = lib.Acm_AxGetINxStopStatus
        Acm_AxGetINxStopStatus.argtypes = [c_void_p, POINTER(c_uint32)]
        Acm_AxGetINxStopStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetINxStopStatus = lib.Acm_AxResetINxStopStatus
        Acm_AxResetINxStopStatus.argtypes = [c_void_p]
        Acm_AxResetINxStopStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_AxJog = lib.Acm_AxJog
        Acm_AxJog.argtypes = [c_void_p, c_uint16]
        Acm_AxJog.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmpDO = lib.Acm_AxSetCmpDO
        Acm_AxSetCmpDO.argtypes = [c_void_p, c_uint32]
        Acm_AxSetCmpDO.restype = c_uint32
    except:
        pass

    try:
        Acm_AxDownloadTorqueTable = lib.Acm_AxDownloadTorqueTable
        Acm_AxDownloadTorqueTable.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), c_uint32]
        Acm_AxDownloadTorqueTable.restype = c_uint32
    except:
        pass

    try:
        Acm_AxLoadTorqueTableFile = lib.Acm_AxLoadTorqueTableFile
        Acm_AxLoadTorqueTableFile.argtypes = [c_void_p, c_char_p, POINTER(c_uint32)]
        Acm_AxLoadTorqueTableFile.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetPVTTable = lib.Acm_AxResetPVTTable
        Acm_AxResetPVTTable.argtypes = [c_void_p]
        Acm_AxResetPVTTable.restype = c_uint32
    except:
        pass

    try:
        Acm_AxLoadPVTTable = lib.Acm_AxLoadPVTTable
        Acm_AxLoadPVTTable.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_uint32]
        Acm_AxLoadPVTTable.restype = c_uint32
    except:
        pass

    try:
        Acm_AxCalculatePVTTableContinuous = lib.Acm_AxCalculatePVTTableContinuous
        Acm_AxCalculatePVTTableContinuous.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double),
                                                      POINTER(c_double), POINTER(c_double), POINTER(c_double), c_uint32, POINTER(c_double)]
        Acm_AxCalculatePVTTableContinuous.restype = c_uint32
    except:
        pass

    try:
        Acm_AxLoadPVTTableContinuous = lib.Acm_AxLoadPVTTableContinuous
        Acm_AxLoadPVTTableContinuous.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double),
                                                 POINTER(c_double), POINTER(c_double), POINTER(c_double), c_double, c_uint32]
        Acm_AxLoadPVTTableContinuous.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStartPVT = lib.Acm_AxStartPVT
        Acm_AxStartPVT.argtypes = [c_void_p, c_uint8]
        Acm_AxStartPVT.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStartAllPVT = lib.Acm_AxStartAllPVT
        Acm_AxStartAllPVT.argtypes = [c_void_p, c_uint8, c_uint32]
        Acm_AxStartAllPVT.restype = c_uint32
    except:
        pass

    try:
        Acm_AxCheckPTBuffer = lib.Acm_AxCheckPTBuffer
        Acm_AxCheckPTBuffer.argtypes = [c_void_p, POINTER(c_uint16)]
        Acm_AxCheckPTBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_AxAddPTData = lib.Acm_AxAddPTData
        Acm_AxAddPTData.argtypes = [c_void_p, c_double, c_double]
        Acm_AxAddPTData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStartPT = lib.Acm_AxStartPT
        Acm_AxStartPT.argtypes = [c_void_p, c_uint8]
        Acm_AxStartPT.restype = c_uint32
    except:
        pass

    try:
        Acm_AxStartAllPT = lib.Acm_AxStartAllPT
        Acm_AxStartAllPT.argtypes = [c_void_p, c_uint8, c_uint32]
        Acm_AxStartAllPT.restype = c_uint32
    except:
        pass

    try:
        Acm_AxResetPTData = lib.Acm_AxResetPTData
        Acm_AxResetPTData.argtypes = [c_void_p]
        Acm_AxResetPTData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxAddPVAData = lib.Acm_AxAddPVAData
        Acm_AxAddPVAData.argtypes = [c_void_p, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_uint32]
        Acm_AxAddPVAData.restype = c_uint32
    except:
        pass
# Group
    try:
        Acm_GpOpen = lib.Acm_GpOpen
        Acm_GpOpen.argtypes = [c_void_p, POINTER(c_void_p), c_ushort]
        Acm_GpOpen.restype = c_uint32
    except:
        pass

    try:
        Acm_GpAddAxis = lib.Acm_GpAddAxis
        Acm_GpAddAxis.argtypes = [POINTER(c_void_p), c_void_p]
        Acm_GpAddAxis.restype = c_uint32
    except:
        pass

    try:
        Acm_GpRemAxis = lib.Acm_GpRemAxis
        Acm_GpRemAxis.argtypes = [c_void_p, c_void_p]
        Acm_GpRemAxis.restype = c_uint32
    except:
        pass

    try:
        Acm_GpClose = lib.Acm_GpClose
        Acm_GpClose.argtypes = [POINTER(c_void_p)]
        Acm_GpClose.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetState = lib.Acm_GpGetState
        Acm_GpGetState.argtypes = [c_void_p, POINTER(c_uint16)]
        Acm_GpGetState.restype = c_uint32
    except:
        pass

    try:
        Acm_GpResetError = lib.Acm_GpResetError
        Acm_GpResetError.argtypes = [c_void_p]
        Acm_GpResetError.restype = c_uint32
    except:
        pass

    try:
        Acm_GpIpoMask = lib.Acm_GpIpoMask
        Acm_GpIpoMask.argtypes = [c_void_p, c_void_p, c_uint32]
        Acm_GpIpoMask.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveLinearRel = lib.Acm_GpMoveLinearRel
        Acm_GpMoveLinearRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
        Acm_GpMoveLinearRel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveLinearAbs = lib.Acm_GpMoveLinearAbs
        Acm_GpMoveLinearAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
        Acm_GpMoveLinearAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveDirectRel = lib.Acm_GpMoveDirectRel
        Acm_GpMoveDirectRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
        Acm_GpMoveDirectRel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveDirectAbs = lib.Acm_GpMoveDirectAbs
        Acm_GpMoveDirectAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
        Acm_GpMoveDirectAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveCircularRel = lib.Acm_GpMoveCircularRel
        Acm_GpMoveCircularRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveCircularRel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveCircularAbs = lib.Acm_GpMoveCircularAbs
        Acm_GpMoveCircularAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveCircularAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveCircularRel_3P = lib.Acm_GpMoveCircularRel_3P
        Acm_GpMoveCircularRel_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveCircularRel_3P.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveCircularAbs_3P = lib.Acm_GpMoveCircularAbs_3P
        Acm_GpMoveCircularAbs_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveCircularAbs_3P.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveCircularRel_Angle = lib.Acm_GpMoveCircularRel_Angle
        Acm_GpMoveCircularRel_Angle.argtypes = [c_void_p, POINTER(c_double), c_uint16, POINTER(c_uint32), c_int16]
        Acm_GpMoveCircularRel_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveCircularAbs_Angle = lib.Acm_GpMoveCircularAbs_Angle
        Acm_GpMoveCircularAbs_Angle.argtypes = [c_void_p, POINTER(c_double), c_uint16, POINTER(c_uint32), c_int16]
        Acm_GpMoveCircularAbs_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveArcRel_Angle = lib.Acm_GpMoveArcRel_Angle
        Acm_GpMoveArcRel_Angle.argtypes = [c_void_p, POINTER(c_double), c_double, POINTER(c_uint32), c_int16]
        Acm_GpMoveArcRel_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveArcAbs_Angle = lib.Acm_GpMoveArcAbs_Angle
        Acm_GpMoveArcAbs_Angle.argtypes = [c_void_p, POINTER(c_double), c_double, POINTER(c_uint32), c_int16]
        Acm_GpMoveArcAbs_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcAbs = lib.Acm_GpMove3DArcAbs
        Acm_GpMove3DArcAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMove3DArcAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcRel = lib.Acm_GpMove3DArcRel
        Acm_GpMove3DArcRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMove3DArcRel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcAbs_V = lib.Acm_GpMove3DArcAbs_V
        Acm_GpMove3DArcAbs_V.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), c_double, POINTER(c_uint32), c_int16]
        Acm_GpMove3DArcAbs_V.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcRel_V = lib.Acm_GpMove3DArcRel_V
        Acm_GpMove3DArcRel_V.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), c_double, POINTER(c_uint32), c_int16]
        Acm_GpMove3DArcRel_V.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcAbs_3P = lib.Acm_GpMove3DArcAbs_3P
        Acm_GpMove3DArcAbs_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_uint16]
        Acm_GpMove3DArcAbs_3P.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcRel_3P = lib.Acm_GpMove3DArcRel_3P
        Acm_GpMove3DArcRel_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_uint16]
        Acm_GpMove3DArcRel_3P.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcAbs_3PAngle = lib.Acm_GpMove3DArcAbs_3PAngle
        Acm_GpMove3DArcAbs_3PAngle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_double]
        Acm_GpMove3DArcAbs_3PAngle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMove3DArcRel_3PAngle = lib.Acm_GpMove3DArcRel_3PAngle
        Acm_GpMove3DArcRel_3PAngle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_double]
        Acm_GpMove3DArcRel_3PAngle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveHelixAbs = lib.Acm_GpMoveHelixAbs
        Acm_GpMoveHelixAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveHelixAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveHelixRel = lib.Acm_GpMoveHelixRel
        Acm_GpMoveHelixRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveHelixRel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveHelixAbs_3P = lib.Acm_GpMoveHelixAbs_3P
        Acm_GpMoveHelixAbs_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveHelixAbs_3P.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveHelixRel_3P = lib.Acm_GpMoveHelixRel_3P
        Acm_GpMoveHelixRel_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveHelixRel_3P.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveHelixRel_Angle = lib.Acm_GpMoveHelixRel_Angle
        Acm_GpMoveHelixRel_Angle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveHelixRel_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveHelixAbs_Angle = lib.Acm_GpMoveHelixAbs_Angle
        Acm_GpMoveHelixAbs_Angle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
        Acm_GpMoveHelixAbs_Angle.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveEllipticalRel = lib.Acm_GpMoveEllipticalRel
        Acm_GpMoveEllipticalRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_double]
        Acm_GpMoveEllipticalRel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveEllipticalAbs = lib.Acm_GpMoveEllipticalAbs
        Acm_GpMoveEllipticalAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_double]
        Acm_GpMoveEllipticalAbs.restype = c_uint32
    except:
        pass

    try:
        Acm_GpLoadPath = lib.Acm_GpLoadPath
        Acm_GpLoadPath.argtypes = [c_void_p, c_char_p, POINTER(c_void_p), POINTER(c_uint32)]
        Acm_GpLoadPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpUnloadPath = lib.Acm_GpUnloadPath
        Acm_GpUnloadPath.argtypes = [c_void_p, POINTER(c_void_p)]
        Acm_GpUnloadPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMovePath = lib.Acm_GpMovePath
        Acm_GpMovePath.argtypes = [c_void_p, c_void_p]
        Acm_GpMovePath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveAllPath = lib.Acm_GpMoveAllPath
        Acm_GpMoveAllPath.argtypes = [POINTER(c_void_p), c_uint32]
        Acm_GpMoveAllPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpAddPath = lib.Acm_GpAddPath
        Acm_GpAddPath.argtypes = [c_void_p, c_uint16, c_uint16, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
        Acm_GpAddPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpAddPath2 = lib.Acm_GpAddPath2
        Acm_GpAddPath2.argtypes = [c_void_p, c_uint16, c_uint16, c_double, c_double, c_double,
                                   c_double, POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
        Acm_GpAddPath2.restype = c_uint32
    except:
        pass

    try:
        Acm_GpLookAheadPath = lib.Acm_GpLookAheadPath
        Acm_GpLookAheadPath.argtypes = [c_void_p, c_uint16, c_char_p]
        Acm_GpLookAheadPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpResetPath = lib.Acm_GpResetPath
        Acm_GpResetPath.argtypes = [POINTER(c_void_p)]
        Acm_GpResetPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetPathStatus = lib.Acm_GpGetPathStatus
        Acm_GpGetPathStatus.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm_GpGetPathStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_GpMoveSelPath = lib.Acm_GpMoveSelPath
        Acm_GpMoveSelPath.argtypes = [c_void_p, c_void_p, c_uint32, c_uint32, c_uint8]
        Acm_GpMoveSelPath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetPathIndexStatus = lib.Acm_GpGetPathIndexStatus
        Acm_GpGetPathIndexStatus.argtypes = [c_void_p, c_uint32, POINTER(c_uint16), POINTER(c_uint16), POINTER(c_double),
                                             POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
        Acm_GpGetPathIndexStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_GpAddBSplinePath = lib.Acm_GpAddBSplinePath
        Acm_GpAddBSplinePath.argtypes = [c_void_p, c_double, c_double, POINTER(c_double), POINTER(c_double), c_uint32, POINTER(c_double),
                                         c_uint32, c_uint32, c_uint32]
        Acm_GpAddBSplinePath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpAddCSplinePath = lib.Acm_GpAddCSplinePath
        Acm_GpAddCSplinePath.argtypes = [c_void_p, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double),
                                         c_uint32, c_uint32]
        Acm_GpAddCSplinePath.restype = c_uint32
    except:
        pass

    try:
        Acm_GpResumeMotion = lib.Acm_GpResumeMotion
        Acm_GpResumeMotion.argtypes = [c_void_p]
        Acm_GpResumeMotion.restype = c_uint32
    except:
        pass

    try:
        Acm_GpPauseMotion = lib.Acm_GpPauseMotion
        Acm_GpPauseMotion.argtypes = [c_void_p]
        Acm_GpPauseMotion.restype = c_uint32
    except:
        pass

    try:
        Acm_GpStopDec = lib.Acm_GpStopDec
        Acm_GpStopDec.argtypes = [c_void_p]
        Acm_GpStopDec.restype = c_uint32
    except:
        pass

    try:
        Acm_GpStopDecEx = lib.Acm_GpStopDecEx
        Acm_GpStopDecEx.argtypes = [c_void_p, c_double]
        Acm_GpStopDecEx.restype = c_uint32
    except:
        pass

    try:
        Acm_GpStopEmg = lib.Acm_GpStopEmg
        Acm_GpStopEmg.argtypes = [c_void_p]
        Acm_GpStopEmg.restype = c_uint32
    except:
        pass

    try:
        Acm_GpChangeVel = lib.Acm_GpChangeVel
        Acm_GpChangeVel.argtypes = [c_void_p, c_double]
        Acm_GpChangeVel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpChangeVelByRate = lib.Acm_GpChangeVelByRate
        Acm_GpChangeVelByRate.argtypes = [c_void_p, c_uint32]
        Acm_GpChangeVelByRate.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetCmdVel = lib.Acm_GpGetCmdVel
        Acm_GpGetCmdVel.argtypes = [c_void_p, POINTER(c_double)]
        Acm_GpGetCmdVel.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetINxStopStatus = lib.Acm_GpGetINxStopStatus
        Acm_GpGetINxStopStatus.argtypes = [c_void_p, POINTER(c_uint32)]
        Acm_GpGetINxStopStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_GpResetINxStopStatus = lib.Acm_GpResetINxStopStatus
        Acm_GpResetINxStopStatus.argtypes = [c_void_p]
        Acm_GpResetINxStopStatus.restype = c_uint32
    except:
        pass
# DIO
    try:
        Acm_DaqDiGetByte = lib.Acm_DaqDiGetByte
        Acm_DaqDiGetByte.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_DaqDiGetByte.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDiGetBit = lib.Acm_DaqDiGetBit
        Acm_DaqDiGetBit.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_DaqDiGetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoSetByte = lib.Acm_DaqDoSetByte
        Acm_DaqDoSetByte.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_DaqDoSetByte.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoSetBit = lib.Acm_DaqDoSetBit
        Acm_DaqDoSetBit.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_DaqDoSetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDiSetBit = lib.Acm_DaqDiSetBit
        Acm_DaqDiSetBit.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_DaqDiSetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoGetByte = lib.Acm_DaqDoGetByte
        Acm_DaqDoGetByte.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoGetByte.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoGetBit = lib.Acm_DaqDoGetBit
        Acm_DaqDoGetBit.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoGetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDiGetBytes = lib.Acm_DaqDiGetBytes
        Acm_DaqDiGetBytes.argtypes = [c_void_p, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDiGetBytes.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoSetBytes = lib.Acm_DaqDoSetBytes
        Acm_DaqDoSetBytes.argtypes = [c_void_p, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoSetBytes.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoGetBytes = lib.Acm_DaqDoGetBytes
        Acm_DaqDoGetBytes.argtypes = [c_void_p, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoGetBytes.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDiGetByteEx = lib.Acm_DaqDiGetByteEx
        Acm_DaqDiGetByteEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDiGetByteEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDiGetBitEx = lib.Acm_DaqDiGetBitEx
        Acm_DaqDiGetBitEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDiGetBitEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoSetByteEx = lib.Acm_DaqDoSetByteEx
        Acm_DaqDoSetByteEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoSetByteEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoSetBitEx = lib.Acm_DaqDoSetBitEx
        Acm_DaqDoSetBitEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoSetBitEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoGetByteEx = lib.Acm_DaqDoGetByteEx
        Acm_DaqDoGetByteEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoGetByteEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqDoGetBitEx = lib.Acm_DaqDoGetBitEx
        Acm_DaqDoGetBitEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DaqDoGetBitEx.restype = c_uint32
    except:
        pass
# AIO
    try:
        Acm_DaqAiGetRawData = lib.Acm_DaqAiGetRawData
        Acm_DaqAiGetRawData.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DaqAiGetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetEngData = lib.Acm_DaqAiGetEngData
        Acm_DaqAiGetEngData.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAiGetEngData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetVoltData = lib.Acm_DaqAiGetVoltData
        Acm_DaqAiGetVoltData.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAiGetVoltData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetCurrData = lib.Acm_DaqAiGetCurrData
        Acm_DaqAiGetCurrData.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAiGetCurrData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiZeroCalibration = lib.Acm_DaqAiZeroCalibration
        Acm_DaqAiZeroCalibration.argtypes = [c_void_p, c_uint16]
        Acm_DaqAiZeroCalibration.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiSpanCalibration = lib.Acm_DaqAiSpanCalibration
        Acm_DaqAiSpanCalibration.argtypes = [c_void_p, c_uint16]
        Acm_DaqAiSpanCalibration.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetChannelStatus = lib.Acm_DaqAiGetChannelStatus
        Acm_DaqAiGetChannelStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint32)]
        Acm_DaqAiGetChannelStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetRawData = lib.Acm_DaqAoSetRawData
        Acm_DaqAoSetRawData.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DaqAoSetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetEngData = lib.Acm_DaqAoSetEngData
        Acm_DaqAoSetEngData.argtypes = [c_void_p, c_uint16, c_float]
        Acm_DaqAoSetEngData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetVoltData = lib.Acm_DaqAoSetVoltData
        Acm_DaqAoSetVoltData.argtypes = [c_void_p, c_uint16, c_float]
        Acm_DaqAoSetVoltData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetCurrData = lib.Acm_DaqAoSetCurrData
        Acm_DaqAoSetCurrData.argtypes = [c_void_p, c_uint16, c_float]
        Acm_DaqAoSetCurrData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetRawData = lib.Acm_DaqAoGetRawData
        Acm_DaqAoGetRawData.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DaqAoGetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetEngData = lib.Acm_DaqAoGetEngData
        Acm_DaqAoGetEngData.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAoGetEngData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetVoltData = lib.Acm_DaqAoGetVoltData
        Acm_DaqAoGetVoltData.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAoGetVoltData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetCurrData = lib.Acm_DaqAoGetCurrData
        Acm_DaqAoGetCurrData.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAoGetCurrData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetCaliType = lib.Acm_DaqAoSetCaliType
        Acm_DaqAoSetCaliType.argtypes = [c_void_p, c_uint16, POINTER(c_float)]
        Acm_DaqAoSetCaliType.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetCaliValue = lib.Acm_DaqAoSetCaliValue
        Acm_DaqAoSetCaliValue.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DaqAoSetCaliValue.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoCaliDone = lib.Acm_DaqAoCaliDone
        Acm_DaqAoCaliDone.argtypes = [c_void_p, c_uint16, c_bool]
        Acm_DaqAoCaliDone.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoCaliDefault = lib.Acm_DaqAoCaliDefault
        Acm_DaqAoCaliDefault.argtypes = [c_void_p, c_uint16]
        Acm_DaqAoCaliDefault.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetChannelStatus = lib.Acm_DaqAoGetChannelStatus
        Acm_DaqAoGetChannelStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint32)]
        Acm_DaqAoGetChannelStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqSetScaledProperty = lib.Acm_DaqSetScaledProperty
        Acm_DaqSetScaledProperty.argtypes = [c_void_p, c_uint, c_uint16, c_float, c_float, c_uint16, c_int16]
        Acm_DaqSetScaledProperty.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetRawDataEx = lib.Acm_DaqAiGetRawDataEx
        Acm_DaqAiGetRawDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint16)]
        Acm_DaqAiGetRawDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetEngDataEx = lib.Acm_DaqAiGetEngDataEx
        Acm_DaqAiGetEngDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_float)]
        Acm_DaqAiGetEngDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetVoltDataEx = lib.Acm_DaqAiGetVoltDataEx
        Acm_DaqAiGetVoltDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_float)]
        Acm_DaqAiGetVoltDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetCurrDataEx = lib.Acm_DaqAiGetCurrDataEx
        Acm_DaqAiGetCurrDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_float)]
        Acm_DaqAiGetCurrDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAiGetChannelStatusEx = lib.Acm_DaqAiGetChannelStatusEx
        Acm_DaqAiGetChannelStatusEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint32)]
        Acm_DaqAiGetChannelStatusEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetRawDataEx = lib.Acm_DaqAoSetRawDataEx
        Acm_DaqAoSetRawDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16]
        Acm_DaqAoSetRawDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetEngDataEx = lib.Acm_DaqAoSetEngDataEx
        Acm_DaqAoSetEngDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_float]
        Acm_DaqAoSetEngDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetVoltDataEx = lib.Acm_DaqAoSetVoltDataEx
        Acm_DaqAoSetVoltDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_float]
        Acm_DaqAoSetVoltDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoSetCurrDataEx = lib.Acm_DaqAoSetCurrDataEx
        Acm_DaqAoSetCurrDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_float]
        Acm_DaqAoSetCurrDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetRawDataEx = lib.Acm_DaqAoGetRawDataEx
        Acm_DaqAoGetRawDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint16)]
        Acm_DaqAoGetRawDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetEngDataEx = lib.Acm_DaqAoGetEngDataEx
        Acm_DaqAoGetEngDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_float)]
        Acm_DaqAoGetEngDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetVoltDataEx = lib.Acm_DaqAoGetVoltDataEx
        Acm_DaqAoGetVoltDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_float)]
        Acm_DaqAoGetVoltDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqAoGetCurrDataEx = lib.Acm_DaqAoGetCurrDataEx
        Acm_DaqAoGetCurrDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_float)]
        Acm_DaqAoGetCurrDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqGetIOLinkStatus = lib.Acm_DaqGetIOLinkStatus
        Acm_DaqGetIOLinkStatus.argtypes = [c_void_p, POINTER(c_uint32)]
        Acm_DaqGetIOLinkStatus.restype = c_uint32
    except:
        pass
# Counter
    try:
        Acm_DaqCntTriggerCmp = lib.Acm_DaqCntTriggerCmp
        Acm_DaqCntTriggerCmp.argtypes = [c_void_p, c_uint16]
        Acm_DaqCntTriggerCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntTriggerLatch = lib.Acm_DaqCntTriggerLatch
        Acm_DaqCntTriggerLatch.argtypes = [c_void_p, c_uint16]
        Acm_DaqCntTriggerLatch.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntResetLatch = lib.Acm_DaqCntResetLatch
        Acm_DaqCntResetLatch.argtypes = [c_void_p, c_uint16]
        Acm_DaqCntResetLatch.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntResetCmp = lib.Acm_DaqCntResetCmp
        Acm_DaqCntResetCmp.argtypes = [c_void_p, c_uint16]
        Acm_DaqCntResetCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntResetCnt = lib.Acm_DaqCntResetCnt
        Acm_DaqCntResetCnt.argtypes = [c_void_p, c_uint16]
        Acm_DaqCntResetCnt.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetCounterData = lib.Acm_DaqCntGetCounterData
        Acm_DaqCntGetCounterData.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetCounterData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCounterData = lib.Acm_DaqCntSetCounterData
        Acm_DaqCntSetCounterData.argtypes = [c_void_p, c_uint16, c_double]
        Acm_DaqCntSetCounterData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetCounterFrequency = lib.Acm_DaqCntGetCounterFrequency
        Acm_DaqCntGetCounterFrequency.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetCounterFrequency.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetExtDriveData = lib.Acm_DaqCntGetExtDriveData
        Acm_DaqCntGetExtDriveData.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetExtDriveData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetExtDriveData = lib.Acm_DaqCntSetExtDriveData
        Acm_DaqCntSetExtDriveData.argtypes = [c_void_p, c_uint16, c_double]
        Acm_DaqCntSetExtDriveData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetLatchData = lib.Acm_DaqCntGetLatchData
        Acm_DaqCntGetLatchData.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetLatchData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetCmpData = lib.Acm_DaqCntGetCmpData
        Acm_DaqCntGetCmpData.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCmpData = lib.Acm_DaqCntSetCmpData
        Acm_DaqCntSetCmpData.argtypes = [c_void_p, c_uint16, c_double]
        Acm_DaqCntSetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCmpTable = lib.Acm_DaqCntSetCmpTable
        Acm_DaqCntSetCmpTable.argtypes = [c_void_p, c_uint16, POINTER(c_double), c_int32]
        Acm_DaqCntSetCmpTable.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCmpAuto = lib.Acm_DaqCntSetCmpAuto
        Acm_DaqCntSetCmpAuto.argtypes = [c_void_p, c_uint16, c_double, c_double, c_double]
        Acm_DaqCntSetCmpAuto.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetLatchBufferStatus = lib.Acm_DaqCntGetLatchBufferStatus
        Acm_DaqCntGetLatchBufferStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DaqCntGetLatchBufferStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntReadLatchBuffer = lib.Acm_DaqCntReadLatchBuffer
        Acm_DaqCntReadLatchBuffer.argtypes = [c_void_p, c_uint16, POINTER(c_double), POINTER(c_uint32)]
        Acm_DaqCntReadLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntTriggerCmpEx = lib.Acm_DaqCntTriggerCmpEx
        Acm_DaqCntTriggerCmpEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DaqCntTriggerCmpEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntTriggerLatchEx = lib.Acm_DaqCntTriggerLatchEx
        Acm_DaqCntTriggerLatchEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DaqCntTriggerLatchEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntResetLatchEx = lib.Acm_DaqCntResetLatchEx
        Acm_DaqCntResetLatchEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DaqCntResetLatchEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntResetCmpEx = lib.Acm_DaqCntResetCmpEx
        Acm_DaqCntResetCmpEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DaqCntResetCmpEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntResetCntEx = lib.Acm_DaqCntResetCntEx
        Acm_DaqCntResetCntEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DaqCntResetCntEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetCounterDataEx = lib.Acm_DaqCntGetCounterDataEx
        Acm_DaqCntGetCounterDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetCounterDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCounterDataEx = lib.Acm_DaqCntSetCounterDataEx
        Acm_DaqCntSetCounterDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_double]
        Acm_DaqCntSetCounterDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetCounterFrequencyEx = lib.Acm_DaqCntGetCounterFrequencyEx
        Acm_DaqCntGetCounterFrequencyEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetCounterFrequencyEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetExtDriveDataEx = lib.Acm_DaqCntGetExtDriveDataEx
        Acm_DaqCntGetExtDriveDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetExtDriveDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetExtDriveDataEx = lib.Acm_DaqCntSetExtDriveDataEx
        Acm_DaqCntSetExtDriveDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_double]
        Acm_DaqCntSetExtDriveDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetLatchDataEx = lib.Acm_DaqCntGetLatchDataEx
        Acm_DaqCntGetLatchDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetLatchDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetCmpDataEx = lib.Acm_DaqCntGetCmpDataEx
        Acm_DaqCntGetCmpDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double)]
        Acm_DaqCntGetCmpDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCmpDataEx = lib.Acm_DaqCntSetCmpDataEx
        Acm_DaqCntSetCmpDataEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_double]
        Acm_DaqCntSetCmpDataEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCmpTableEx = lib.Acm_DaqCntSetCmpTableEx
        Acm_DaqCntSetCmpTableEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double), c_int32]
        Acm_DaqCntSetCmpTableEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntSetCmpAutoEx = lib.Acm_DaqCntSetCmpAutoEx
        Acm_DaqCntSetCmpAutoEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_double, c_double, c_double]
        Acm_DaqCntSetCmpAutoEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntGetLatchBufferStatusEx = lib.Acm_DaqCntGetLatchBufferStatusEx
        Acm_DaqCntGetLatchBufferStatusEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DaqCntGetLatchBufferStatusEx.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqCntReadLatchBufferEx = lib.Acm_DaqCntReadLatchBufferEx
        Acm_DaqCntReadLatchBufferEx.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_double), POINTER(c_uint32)]
        Acm_DaqCntReadLatchBufferEx.restype = c_uint32
    except:
        pass
# PWM
    try:
        Acm_AxPWMOut = lib.Acm_AxPWMOut
        Acm_AxPWMOut.argtypes = [c_void_p, c_uint32, c_uint32]
        Acm_AxPWMOut.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetPWMOutState = lib.Acm_AxGetPWMOutState
        Acm_AxGetPWMOutState.argtypes = [c_void_p, POINTER(c_uint32)]
        Acm_AxGetPWMOutState.restype = c_uint32
    except:
        pass
# MDAQ
    try:
        Acm_DevMDaqConfig = lib.Acm_DevMDaqConfig
        Acm_DevMDaqConfig.argtypes = [c_void_p, c_uint16, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32]
        Acm_DevMDaqConfig.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMDaqStart = lib.Acm_DevMDaqStart
        Acm_DevMDaqStart.argtypes = [c_void_p]
        Acm_DevMDaqStart.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMDaqStop = lib.Acm_DevMDaqStop
        Acm_DevMDaqStop.argtypes = [c_void_p]
        Acm_DevMDaqStop.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMDaqReset = lib.Acm_DevMDaqReset
        Acm_DevMDaqReset.argtypes = [c_void_p, c_uint16]
        Acm_DevMDaqReset.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMDaqGetStatus = lib.Acm_DevMDaqGetStatus
        Acm_DevMDaqGetStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint16), POINTER(c_uint8)]
        Acm_DevMDaqGetStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMDaqGetData = lib.Acm_DevMDaqGetData
        Acm_DevMDaqGetData.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_int32)]
        Acm_DevMDaqGetData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMDaqGetConfig = lib.Acm_DevMDaqGetConfig
        Acm_DevMDaqGetConfig.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32),
                                         POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DevMDaqGetConfig.restype = c_uint32
    except:
        pass

    try:
        Acm_RegCallBackFunc = lib.Acm_RegCallBackFunc
        Acm_RegCallBackFunc.argtypes = [c_void_p, CALLBACK_FUNC, c_void_p]
        Acm_RegCallBackFunc.restype = c_uint32
    except:
        pass

    try:
        Acm_EnableEventCallBack = lib.Acm_EnableEventCallBack
        Acm_EnableEventCallBack.argtypes = [c_void_p]
        Acm_EnableEventCallBack.restype = c_uint32
    except:
        pass

    try:
        Acm_RegCallBackFuncForOneEvent = lib.Acm_RegCallBackFuncForOneEvent
        Acm_RegCallBackFuncForOneEvent.argtypes = [c_void_p, c_uint32, CALLBACK_FUNC, c_void_p]
        Acm_RegCallBackFuncForOneEvent.restype = c_uint32
    except:
        pass

    try:
        Acm_DevEnableMotionEvent = lib.Acm_DevEnableMotionEvent
        Acm_DevEnableMotionEvent.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), c_uint32, c_uint32]
        Acm_DevEnableMotionEvent.restype = c_uint32
    except:
        pass
# Robot
    # try:
    #     Acm_GpRbSetMode = lib.Acm_GpRbSetMode
    #     Acm_GpRbSetMode.argtypes = [c_void_p, c_uint16, POINTER(c_int32), c_uint32]
    #     Acm_GpRbSetMode.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GpRbGetCmdPosition = lib.Acm_GpRbGetCmdPosition
    #     Acm_GpRbGetCmdPosition.argtypes = [c_void_p, POINTER(c_double), c_uint32]
    #     Acm_GpRbGetCmdPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GpRbGetActualPosition = lib.Acm_GpRbGetActualPosition
    #     Acm_GpRbGetActualPosition.argtypes = [c_void_p, POINTER(c_double), c_uint32]
    #     Acm_GpRbGetActualPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GpRbGetArmCmdPosition = lib.Acm_GpRbGetArmCmdPosition
    #     Acm_GpRbGetArmCmdPosition.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
    #     Acm_GpRbGetArmCmdPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GpRbGetArmActualPosition = lib.Acm_GpRbGetArmActualPosition
    #     Acm_GpRbGetArmActualPosition.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
    #     Acm_GpRbGetArmActualPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetActualPosition = lib.Acm_RbGetActualPosition
    #     Acm_RbGetActualPosition.argtypes = [c_void_p, POINTER(c_double), c_uint32]
    #     Acm_RbGetActualPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetCmdPosition = lib.Acm_RbGetCmdPosition
    #     Acm_RbGetCmdPosition.argtypes = [c_void_p, POINTER(c_double), c_uint32]
    #     Acm_RbGetCmdPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetArmActualPosition = lib.Acm_RbGetArmActualPosition
    #     Acm_RbGetArmActualPosition.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
    #     Acm_RbGetArmActualPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetArmCmdPosition = lib.Acm_RbGetArmCmdPosition
    #     Acm_RbGetArmCmdPosition.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
    #     Acm_RbGetArmCmdPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbOpen = lib.Acm_RbOpen
    #     Acm_RbOpen.argtypes = [c_void_p, POINTER(c_void_p)]
    #     Acm_RbOpen.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbInitial = lib.Acm_RbInitial
    #     Acm_RbInitial.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double),
    #                               POINTER(c_int32), c_uint32]
    #     Acm_RbInitial.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbClose = lib.Acm_RbClose
    #     Acm_RbClose.argtypes = [POINTER(c_void_p)]
    #     Acm_RbClose.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbResetError = lib.Acm_RbResetError
    #     Acm_RbResetError.argtypes = [c_void_p]
    #     Acm_RbResetError.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetState = lib.Acm_RbGetState
    #     Acm_RbGetState.argtypes = [c_void_p, POINTER(c_uint16)]
    #     Acm_RbGetState.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbSetActPosition = lib.Acm_RbSetActPosition
    #     Acm_RbSetActPosition.argtypes = [c_void_p, POINTER(c_double), c_uint32]
    #     Acm_RbSetActPosition.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveRel = lib.Acm_RbMoveRel
    #     Acm_RbMoveRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbMoveRel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveAbs = lib.Acm_RbMoveAbs
    #     Acm_RbMoveAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbMoveAbs.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveDirectRel = lib.Acm_RbMoveDirectRel
    #     Acm_RbMoveDirectRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbMoveDirectRel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveDirectAbs = lib.Acm_RbMoveDirectAbs
    #     Acm_RbMoveDirectAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbMoveDirectAbs.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveLinearRel = lib.Acm_RbMoveLinearRel
    #     Acm_RbMoveLinearRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbMoveLinearRel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveLinearAbs = lib.Acm_RbMoveLinearAbs
    #     Acm_RbMoveLinearAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbMoveLinearAbs.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveArcRel = lib.Acm_RbMoveArcRel
    #     Acm_RbMoveArcRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMoveArcRel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveArcAbs = lib.Acm_RbMoveArcAbs
    #     Acm_RbMoveArcAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMoveArcAbs.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveArcRel_3P = lib.Acm_RbMoveArcRel_3P
    #     Acm_RbMoveArcRel_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMoveArcRel_3P.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveArcAbs_3P = lib.Acm_RbMoveArcAbs_3P
    #     Acm_RbMoveArcAbs_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMoveArcAbs_3P.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveArcRel_Angle = lib.Acm_RbMoveArcRel_Angle
    #     Acm_RbMoveArcRel_Angle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMoveArcRel_Angle.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveArcAbs_Angle = lib.Acm_RbMoveArcAbs_Angle
    #     Acm_RbMoveArcAbs_Angle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMoveArcAbs_Angle.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcAbs = lib.Acm_RbMove3DArcAbs
    #     Acm_RbMove3DArcAbs.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMove3DArcAbs.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcRel = lib.Acm_RbMove3DArcRel
    #     Acm_RbMove3DArcRel.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16]
    #     Acm_RbMove3DArcRel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcAbs_V = lib.Acm_RbMove3DArcAbs_V
    #     Acm_RbMove3DArcAbs_V.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double),
    #                                      c_double, POINTER(c_uint32), c_int16]
    #     Acm_RbMove3DArcAbs_V.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcRel_V = lib.Acm_RbMove3DArcRel_V
    #     Acm_RbMove3DArcRel_V.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_double),
    #                                      c_double, POINTER(c_uint32), c_int16]
    #     Acm_RbMove3DArcRel_V.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcAbs_3P = lib.Acm_RbMove3DArcAbs_3P
    #     Acm_RbMove3DArcAbs_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_uint16]
    #     Acm_RbMove3DArcAbs_3P.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcRel_3P = lib.Acm_RbMove3DArcRel_3P
    #     Acm_RbMove3DArcRel_3P.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_uint16]
    #     Acm_RbMove3DArcRel_3P.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcAbs_3PAngle = lib.Acm_RbMove3DArcAbs_3PAngle
    #     Acm_RbMove3DArcAbs_3PAngle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_double]
    #     Acm_RbMove3DArcAbs_3PAngle.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMove3DArcRel_3PAngle = lib.Acm_RbMove3DArcRel_3PAngle
    #     Acm_RbMove3DArcRel_3PAngle.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double), POINTER(c_uint32), c_int16, c_double]
    #     Acm_RbMove3DArcRel_3PAngle.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbAddPath = lib.Acm_RbAddPath
    #     Acm_RbAddPath.argtypes = [c_void_p, c_uint16, c_uint16, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbAddPath.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbResetPath = lib.Acm_RbResetPath
    #     Acm_RbResetPath.argtypes = [POINTER(c_void_p)]
    #     Acm_RbResetPath.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetPathStatus = lib.Acm_RbGetPathStatus
    #     Acm_RbGetPathStatus.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
    #     Acm_RbGetPathStatus.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMovePath = lib.Acm_RbMovePath
    #     Acm_RbMovePath.argtypes = [c_void_p, c_void_p]
    #     Acm_RbMovePath.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbChangeVel = lib.Acm_RbChangeVel
    #     Acm_RbChangeVel.argtypes = [c_void_p, c_double]
    #     Acm_RbChangeVel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbChangeVelByRate = lib.Acm_RbChangeVelByRate
    #     Acm_RbChangeVelByRate.argtypes = [c_void_p, c_uint32]
    #     Acm_RbChangeVelByRate.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetCmdVel = lib.Acm_RbGetCmdVel
    #     Acm_RbGetCmdVel.argtypes = [c_void_p, POINTER(c_double)]
    #     Acm_RbGetCmdVel.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbStopDec = lib.Acm_RbStopDec
    #     Acm_RbStopDec.argtypes = [c_void_p]
    #     Acm_RbStopDec.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbStopEmg = lib.Acm_RbStopEmg
    #     Acm_RbStopEmg.argtypes = [c_void_p]
    #     Acm_RbStopEmg.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbPauseMotion = lib.Acm_RbPauseMotion
    #     Acm_RbPauseMotion.argtypes = [c_void_p]
    #     Acm_RbPauseMotion.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbResumeMotion = lib.Acm_RbResumeMotion
    #     Acm_RbResumeMotion.argtypes = [c_void_p]
    #     Acm_RbResumeMotion.restype = c_uint32
    # except:
    #     pass

    # try:
    #     IsGMSHandleValid = lib.IsGMSHandleValid
    #     IsGMSHandleValid.argtypes = [c_void_p]
    #     IsGMSHandleValid.restype = c_bool
    # except:
    #     pass

    # try:
    #     Acm_RbLoadPath = lib.Acm_RbLoadPath
    #     Acm_RbLoadPath.argtypes = [c_void_p, c_char_p, POINTER(c_void_p), POINTER(c_uint32)]
    #     Acm_RbLoadPath.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbUnloadPath = lib.Acm_RbUnloadPath
    #     Acm_RbUnloadPath.argtypes = [c_void_p, POINTER(c_void_p)]
    #     Acm_RbUnloadPath.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbMoveSelPath = lib.Acm_RbMoveSelPath
    #     Acm_RbMoveSelPath.argtypes = [c_void_p, c_void_p, c_uint32, c_uint32, c_uint8]
    #     Acm_RbMoveSelPath.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetPathIndexStatus = lib.Acm_RbGetPathIndexStatus
    #     Acm_RbGetPathIndexStatus.argtypes = [c_void_p, c_uint32, POINTER(c_uint16), POINTER(c_uint16),
    #                                          POINTER(c_double), POINTER(c_double), POINTER(c_double),
    #                                          POINTER(c_double), POINTER(c_uint32)]
    #     Acm_RbGetPathIndexStatus.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbSetExtDrive = lib.Acm_RbSetExtDrive
    #     Acm_RbSetExtDrive.argtypes = [c_void_p, c_uint16]
    #     Acm_RbSetExtDrive.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbJog = lib.Acm_RbJog
    #     Acm_RbJog.argtypes = [c_void_p, c_uint16]
    #     Acm_RbJog.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_RbGetWorldPosFromJoint = lib.Acm_RbGetWorldPosFromJoint
    #     Acm_RbGetWorldPosFromJoint.argtypes = [c_void_p, POINTER(c_double), POINTER(c_double)]
    #     Acm_RbGetWorldPosFromJoint.restype = c_uint32
    # except:
    #     pass
# GM code
    # try:
    #     Acm_GmOpen = lib.Acm_GmOpen
    #     Acm_GmOpen.argtypes = [c_void_p, POINTER(c_void_p)]
    #     Acm_GmOpen.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmClose = lib.Acm_GmClose
    #     Acm_GmClose.argtypes = [c_void_p]
    #     Acm_GmClose.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmLoadJob = lib.Acm_GmLoadJob
    #     Acm_GmLoadJob.argtypes = [c_void_p, c_char_p, POINTER(c_uint32)]
    #     Acm_GmLoadJob.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmUploadJob = lib.Acm_GmUploadJob
    #     Acm_GmUploadJob.argtypes = [c_void_p, c_char_p, POINTER(c_uint32)]
    #     Acm_GmUploadJob.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmResetJob = lib.Acm_GmResetJob
    #     Acm_GmResetJob.argtypes = [c_void_p]
    #     Acm_GmResetJob.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmCommand = lib.Acm_GmCommand
    #     Acm_GmCommand.argtypes = [c_void_p, c_char_p]
    #     Acm_GmCommand.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmRemoveAxisFromSystem = lib.Acm_GmRemoveAxisFromSystem
    #     Acm_GmRemoveAxisFromSystem.argtypes = [c_void_p, c_uint32]
    #     Acm_GmRemoveAxisFromSystem.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmSetCompensationRadius = lib.Acm_GmSetCompensationRadius
    #     Acm_GmSetCompensationRadius.argtypes = [c_void_p, c_uint32, c_double]
    #     Acm_GmSetCompensationRadius.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmGetCompensationRadius = lib.Acm_GmGetCompensationRadius
    #     Acm_GmGetCompensationRadius.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32)]
    #     Acm_GmGetCompensationRadius.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmSetCurrentCompensationRadius = lib.Acm_GmSetCurrentCompensationRadius
    #     Acm_GmSetCurrentCompensationRadius.argtypes = [c_void_p, c_double]
    #     Acm_GmSetCurrentCompensationRadius.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmGetCurrentCompensationRadius = lib.Acm_GmGetCurrentCompensationRadius
    #     Acm_GmGetCurrentCompensationRadius.argtypes = [c_void_p, POINTER(c_double)]
    #     Acm_GmGetCurrentCompensationRadius.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmSetToolLengthOffset = lib.Acm_GmSetToolLengthOffset
    #     Acm_GmSetToolLengthOffset.argtypes = [c_void_p, c_uint32, c_double]
    #     Acm_GmSetToolLengthOffset.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmGetToolLengthOffset = lib.Acm_GmGetToolLengthOffset
    #     Acm_GmGetToolLengthOffset.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32)]
    #     Acm_GmGetToolLengthOffset.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmSetCurrentToolLengthOffset = lib.Acm_GmSetCurrentToolLengthOffset
    #     Acm_GmSetCurrentToolLengthOffset.argtypes = [c_void_p, c_double]
    #     Acm_GmSetCurrentToolLengthOffset.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmGetCurrentToolLengthOffset = lib.Acm_GmGetCurrentToolLengthOffset
    #     Acm_GmGetCurrentToolLengthOffset.argtypes = [c_void_p, POINTER(c_double)]
    #     Acm_GmGetCurrentToolLengthOffset.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmSetMacro = lib.Acm_GmSetMacro
    #     Acm_GmSetMacro.argtypes = [c_void_p, c_uint32, c_char_p]
    #     Acm_GmSetMacro.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmGetMacro = lib.Acm_GmGetMacro
    #     Acm_GmGetMacro.argtypes = [c_void_p, c_uint32, c_char_p, POINTER(c_uint32)]
    #     Acm_GmGetMacro.restype = c_uint32
    # except:
    #     pass

    # try:
    #     Acm_GmGetMacroArray = lib.Acm_GmGetMacroArray
    #     Acm_GmGetMacroArray.argtypes = [c_void_p, POINTER(c_uint32), POINTER(c_uint32)]
    #     Acm_GmGetMacroArray.restype = c_uint32
    # except:
    #     pass

    try:
        Acm_ServoSetCom = lib.Acm_ServoSetCom
        Acm_ServoSetCom.argtypes = [c_uint32, c_uint32, c_uint32]
        Acm_ServoSetCom.restype = c_uint32
    except:
        pass

    try:
        Acm_ServoGetAbsPosition = lib.Acm_ServoGetAbsPosition
        Acm_ServoGetAbsPosition.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32, POINTER(c_double)]
        Acm_ServoGetAbsPosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCmdPosi_Pulse = lib.Acm_AxSetCmdPosi_Pulse
        Acm_AxSetCmdPosi_Pulse.argtypes = [c_void_p, c_double]
        Acm_AxSetCmdPosi_Pulse.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSpecialDiSetBit = lib.Acm_AxSpecialDiSetBit
        Acm_AxSpecialDiSetBit.argtypes = [c_void_p, c_uint16, c_uint8]
        Acm_AxSpecialDiSetBit.restype = c_uint32
    except:
        pass

    try:
        Acm_DevEnableLTC = lib.Acm_DevEnableLTC
        Acm_DevEnableLTC.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DevEnableLTC.restype = c_uint32
    except:
        pass

    try:
        Acm_DevLTCSaftyDist = lib.Acm_DevLTCSaftyDist
        Acm_DevLTCSaftyDist.argtypes = [c_void_p, c_uint16, c_double]
        Acm_DevLTCSaftyDist.restype = c_uint32
    except:
        pass

    try:
        Acm_DevEnableCmp = lib.Acm_DevEnableCmp
        Acm_DevEnableCmp.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DevEnableCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_DevLtcLinkCmp = lib.Acm_DevLtcLinkCmp
        Acm_DevLtcLinkCmp.argtypes = [c_void_p, c_void_p, c_uint16, c_uint16, c_uint16, c_double]
        Acm_DevLtcLinkCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetCmp = lib.Acm_DevSetCmp
        Acm_DevSetCmp.argtypes = [c_void_p, c_uint16, c_uint32, c_uint32, c_uint32, c_uint32, c_uint32]
        Acm_DevSetCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetCmpDO = lib.Acm_DevSetCmpDO
        Acm_DevSetCmpDO.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DevSetCmpDO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetCmpData = lib.Acm_DevSetCmpData
        Acm_DevSetCmpData.argtypes = [c_void_p, c_uint16, c_double]
        Acm_DevSetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetCmpAuto = lib.Acm_DevSetCmpAuto
        Acm_DevSetCmpAuto.argtypes = [c_void_p, c_uint16, c_double, c_double, c_double]
        Acm_DevSetCmpAuto.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetCmpData = lib.Acm_DevGetCmpData
        Acm_DevGetCmpData.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DevGetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevEnableCmpFIFO = lib.Acm_DevEnableCmpFIFO
        Acm_DevEnableCmpFIFO.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DevEnableCmpFIFO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetCmpFIFOCount = lib.Acm_DevGetCmpFIFOCount
        Acm_DevGetCmpFIFOCount.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DevGetCmpFIFOCount.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetCmpCounter = lib.Acm_DevGetCmpCounter
        Acm_DevGetCmpCounter.argtypes = [c_void_p, c_uint16, POINTER(c_uint32)]
        Acm_DevGetCmpCounter.restype = c_uint32
    except:
        pass

    try:
        Acm_DevResetCmpFIFO = lib.Acm_DevResetCmpFIFO
        Acm_DevResetCmpFIFO.argtypes = [c_void_p, c_uint16]
        Acm_DevResetCmpFIFO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetLTCInEdge = lib.Acm_DevSetLTCInEdge
        Acm_DevSetLTCInEdge.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DevSetLTCInEdge.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCData = lib.Acm_DevGetLTCData
        Acm_DevGetLTCData.argtypes = [c_void_p, c_uint16, POINTER(c_double), POINTER(c_double)]
        Acm_DevGetLTCData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCFlag = lib.Acm_DevGetLTCFlag
        Acm_DevGetLTCFlag.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_DevGetLTCFlag.restype = c_uint32
    except:
        pass

    try:
        Acm_DevResetLTC = lib.Acm_DevResetLTC
        Acm_DevResetLTC.argtypes = [c_void_p, c_uint16]
        Acm_DevResetLTC.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetCmpFlag = lib.Acm_DevGetCmpFlag
        Acm_DevGetCmpFlag.argtypes = [c_void_p, c_uint16, POINTER(c_uint8)]
        Acm_DevGetCmpFlag.restype = c_uint32
    except:
        pass

    try:
        Acm_DevResetCmpFlag = lib.Acm_DevResetCmpFlag
        Acm_DevResetCmpFlag.argtypes = [c_void_p, c_uint16]
        Acm_DevResetCmpFlag.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLtcLinkCmpStatus = lib.Acm_DevGetLtcLinkCmpStatus
        Acm_DevGetLtcLinkCmpStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DevGetLtcLinkCmpStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DevResetCmpData = lib.Acm_DevResetCmpData
        Acm_DevResetCmpData.argtypes = [c_void_p, c_uint16]
        Acm_DevResetCmpData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCInEdge = lib.Acm_DevGetLTCInEdge
        Acm_DevGetLTCInEdge.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DevGetLTCInEdge.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCInPol = lib.Acm_DevGetLTCInPol
        Acm_DevGetLTCInPol.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DevGetLTCInPol.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCSaftyDist = lib.Acm_DevGetLTCSaftyDist
        Acm_DevGetLTCSaftyDist.argtypes = [c_void_p, c_uint16, POINTER(c_double)]
        Acm_DevGetLTCSaftyDist.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCInSource = lib.Acm_DevGetLTCInSource
        Acm_DevGetLTCInSource.argtypes = [c_void_p, c_uint16, POINTER(c_uint16)]
        Acm_DevGetLTCInSource.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetLTCInSource = lib.Acm_DevSetLTCInSource
        Acm_DevSetLTCInSource.argtypes = [c_void_p, c_uint16, c_uint16]
        Acm_DevSetLTCInSource.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetCmp = lib.Acm_DevGetCmp
        Acm_DevGetCmp.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32),
                                  POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DevGetCmp.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReadLatchBuffer = lib.Acm_DevReadLatchBuffer
        Acm_DevReadLatchBuffer.argtypes = [c_void_p, c_uint16, POINTER(c_double), POINTER(c_double), POINTER(c_uint32)]
        Acm_DevReadLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLatchBufferStatus = lib.Acm_DevGetLatchBufferStatus
        Acm_DevGetLatchBufferStatus.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DevGetLatchBufferStatus.restype = c_uint32
    except:
        pass

    try:
        Acm_DevResetLatchBuffer = lib.Acm_DevResetLatchBuffer
        Acm_DevResetLatchBuffer.argtypes = [c_void_p, c_uint16]
        Acm_DevResetLatchBuffer.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetLTCInAxisID = lib.Acm_DevSetLTCInAxisID
        Acm_DevSetLTCInAxisID.argtypes = [c_void_p, c_uint16, c_uint32]
        Acm_DevSetLTCInAxisID.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetLTCInAxisID = lib.Acm_DevGetLTCInAxisID
        Acm_DevGetLTCInAxisID.argtypes = [c_void_p, c_uint16, POINTER(c_uint32)]
        Acm_DevGetLTCInAxisID.restype = c_uint32
    except:
        pass

    try:
        Acm_DevSetCmpAxisID = lib.Acm_DevSetCmpAxisID
        Acm_DevSetCmpAxisID.argtypes = [c_void_p, c_uint16, c_uint32]
        Acm_DevSetCmpAxisID.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetCmpAxisID = lib.Acm_DevGetCmpAxisID
        Acm_DevGetCmpAxisID.argtypes = [c_void_p, c_uint16, POINTER(c_uint32)]
        Acm_DevGetCmpAxisID.restype = c_uint32
    except:
        pass

    try:
        Acm_GetDevNum = lib.Acm_GetDevNum
        Acm_GetDevNum.argtypes = [c_uint32, c_uint32, POINTER(c_uint32)]
        Acm_GetDevNum.restype = c_uint32
    except:
        pass
# Mapping
    try:
        Acm_DevSaveMapFile = lib.Acm_DevSaveMapFile
        Acm_DevSaveMapFile.argtypes = [c_void_p, c_char_p]
        Acm_DevSaveMapFile.restype = c_uint32
    except:
        pass

    try:
        Acm_DevLoadMapFile = lib.Acm_DevLoadMapFile
        Acm_DevLoadMapFile.argtypes = [c_void_p, c_char_p]
        Acm_DevLoadMapFile.restype = c_uint32
    except:
        pass

    try:
        Acm_DevUpLoadMapInfo = lib.Acm_DevUpLoadMapInfo
        Acm_DevUpLoadMapInfo.argtypes = [c_void_p, c_uint16, POINTER(DEV_IO_MAP_INFO), POINTER(c_uint32)]
        Acm_DevUpLoadMapInfo.restype = c_uint32
    except:
        pass

    try:
        Acm_DevDownLoadMapInfo = lib.Acm_DevDownLoadMapInfo
        Acm_DevDownLoadMapInfo.argtypes = [c_void_p, c_uint16, POINTER(DEV_IO_MAP_INFO), c_uint32]
        Acm_DevDownLoadMapInfo.restype = c_uint32
    except:
        pass
# EtherCAT
    try:
        Acm_DevSetSlaveStates = lib.Acm_DevSetSlaveStates
        Acm_DevSetSlaveStates.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16]
        Acm_DevSetSlaveStates.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveStates = lib.Acm_DevGetSlaveStates
        Acm_DevGetSlaveStates.argtypes = [c_void_p, c_uint16, c_uint16, POINTER(c_uint16)]
        Acm_DevGetSlaveStates.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveTxPDO = lib.Acm_DevGetSlaveTxPDO
        Acm_DevGetSlaveTxPDO.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DevGetSlaveTxPDO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveRxPDO = lib.Acm_DevGetSlaveRxPDO
        Acm_DevGetSlaveRxPDO.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DevGetSlaveRxPDO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevGetSlaveRxTxPDO = lib.Acm_DevGetSlaveRxTxPDO
        Acm_DevGetSlaveRxTxPDO.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DevGetSlaveRxTxPDO.restype = c_uint32
    except:
        pass

    try:
        Acm_DevWriteSDOComplete = lib.Acm_DevWriteSDOComplete
        Acm_DevWriteSDOComplete.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_void_p)]
        Acm_DevWriteSDOComplete.restype = c_uint32
    except:
        pass

    try:
        Acm_DevWriteSDOData = lib.Acm_DevWriteSDOData
        Acm_DevWriteSDOData.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_void_p)]
        Acm_DevWriteSDOData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReadSDOData = lib.Acm_DevReadSDOData
        Acm_DevReadSDOData.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_void_p)]
        Acm_DevReadSDOData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevWriteRegData = lib.Acm_DevWriteRegData
        Acm_DevWriteRegData.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_void_p)]
        Acm_DevWriteRegData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReadRegData = lib.Acm_DevReadRegData
        Acm_DevReadRegData.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint16, c_uint16, POINTER(c_void_p)]
        Acm_DevReadRegData.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReadEmgMessage = lib.Acm_DevReadEmgMessage
        Acm_DevReadEmgMessage.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, POINTER(c_uint8)]
        Acm_DevReadEmgMessage.restype = c_uint32
    except:
        pass

    try:
        Acm_DevReadSlvCommErrCnt = lib.Acm_DevReadSlvCommErrCnt
        Acm_DevReadSlvCommErrCnt.argtypes = [c_void_p, c_uint16, POINTER(c_uint32), POINTER(c_uint32)]
        Acm_DevReadSlvCommErrCnt.restype = c_uint32
    except:
        pass

    try:
        Acm_DaqLinkPDO = lib.Acm_DaqLinkPDO
        Acm_DaqLinkPDO.argtypes = [c_void_p, c_uint, c_uint16, c_uint32, c_uint32, c_uint32, c_uint32]
        Acm_DaqLinkPDO.restype = c_uint32
    except:
        pass

    try:
        Acm_AxMoveTorque = lib.Acm_AxMoveTorque
        Acm_AxMoveTorque.argtypes = [c_void_p, c_double, c_double, c_double, c_double, c_uint8]
        Acm_AxMoveTorque.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetActTorque = lib.Acm_AxGetActTorque
        Acm_AxGetActTorque.argtypes = [c_void_p, POINTER(c_int32)]
        Acm_AxGetActTorque.restype = c_uint32
    except:
        pass

    try:
        Acm_Ax2DCompensateInAx = lib.Acm_Ax2DCompensateInAx
        Acm_Ax2DCompensateInAx.argtypes = [c_void_p, c_void_p, POINTER(c_double), POINTER(c_double), c_uint32]
        Acm_Ax2DCompensateInAx.restype = c_uint32
    except:
        pass

    try:
        Acm_Ax1DCompensateTable = lib.Acm_Ax1DCompensateTable
        Acm_Ax1DCompensateTable.argtypes = [c_void_p, c_double, c_double, POINTER(c_double), c_uint32, c_uint32]
        Acm_Ax1DCompensateTable.restype = c_uint32
    except:
        pass

    try:
        Acm_DevZAxisCompensateTable = lib.Acm_DevZAxisCompensateTable
        Acm_DevZAxisCompensateTable.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_double, c_double, c_double,
                                                c_double, POINTER(c_double), c_uint32, c_uint32]
        Acm_DevZAxisCompensateTable.restype = c_uint32
    except:
        pass

    try:
        Acm_Dev2DCompensateTable = lib.Acm_Dev2DCompensateTable
        Acm_Dev2DCompensateTable.argtypes = [c_void_p, c_void_p, c_void_p, c_double, c_double, c_double, c_double,
                                             POINTER(c_double), POINTER(c_double), c_uint32, c_uint32]
        Acm_Dev2DCompensateTable.restype = c_uint32
    except:
        pass

    try:
        Acm_DevZAxisCompensateTableEx = lib.Acm_DevZAxisCompensateTableEx
        Acm_DevZAxisCompensateTableEx.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_double, c_double, c_double, c_double,
                                                  POINTER(c_double), c_uint32, c_uint32, c_uint32]
        Acm_DevZAxisCompensateTableEx.restype = c_uint32
    except:
        pass

    try:
        Acm_Dev2DCompensateTableEx = lib.Acm_Dev2DCompensateTableEx
        Acm_Dev2DCompensateTableEx.argtypes = [c_void_p, c_void_p, c_void_p, c_double, c_double, c_double, c_double,
                                               POINTER(c_double), POINTER(c_double), c_uint32, c_uint32, c_uint32]
        Acm_Dev2DCompensateTableEx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCompensatePosition = lib.Acm_AxGetCompensatePosition
        Acm_AxGetCompensatePosition.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetCompensatePosition.restype = c_uint32
    except:
        pass

    try:
        Acm_DevMultiTrigInitial = lib.Acm_DevMultiTrigInitial
        Acm_DevMultiTrigInitial.argtypes = [c_void_p, c_uint16, c_uint16, c_uint16, c_uint8, c_uint8, c_uint8]
        Acm_DevMultiTrigInitial.restype = c_uint32
    except:
        pass

    try:
        Acm_EnableOneDevEventCallBack = lib.Acm_EnableOneDevEventCallBack
        Acm_EnableOneDevEventCallBack.argtypes = [c_void_p, c_ulong]
        Acm_EnableOneDevEventCallBack.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetRawData = lib.Acm_AxGetRawData
        Acm_AxGetRawData.argtypes = [c_void_p, c_uint8, POINTER(c_double)]
        Acm_AxGetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetRawData = lib.Acm_AxSetRawData
        Acm_AxSetRawData.argtypes = [c_void_p, c_uint8, c_double]
        Acm_AxSetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetRawData = lib.Acm_GpGetRawData
        Acm_GpGetRawData.argtypes = [c_void_p, c_uint8, POINTER(c_double)]
        Acm_GpGetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_GpSetRawData = lib.Acm_GpSetRawData
        Acm_GpSetRawData.argtypes = [c_void_p, c_uint8, c_double]
        Acm_GpSetRawData.restype = c_uint32
    except:
        pass

    try:
        Acm_GpGetPausePosition = lib.Acm_GpGetPausePosition
        Acm_GpGetPausePosition.argtypes = [c_void_p, POINTER(c_double)]
        Acm_GpGetPausePosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxReturnPausePosition = lib.Acm_AxReturnPausePosition
        Acm_AxReturnPausePosition.argtypes = [c_void_p]
        Acm_AxReturnPausePosition.restype = c_uint32
    except:
        pass

    try:
        Acm_AxAddOnAx = lib.Acm_AxAddOnAx
        Acm_AxAddOnAx.argtypes = [c_void_p, c_void_p]
        Acm_AxAddOnAx.restype = c_uint32
    except:
        pass

    try:
        Acm_AxAddRemove = lib.Acm_AxAddRemove
        Acm_AxAddRemove.argtypes = [c_void_p, c_void_p]
        Acm_AxAddRemove.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetAddOnNum = lib.Acm_AxGetAddOnNum
        Acm_AxGetAddOnNum.argtypes = [c_void_p, POINTER(c_int32)]
        Acm_AxGetAddOnNum.restype = c_uint32
    except:
        pass

    try:
        Acm_AxSetCompensateDistance = lib.Acm_AxSetCompensateDistance
        Acm_AxSetCompensateDistance.argtypes = [c_void_p, c_double]
        Acm_AxSetCompensateDistance.restype = c_uint32
    except:
        pass

    try:
        Acm_AxGetCompensateDistance = lib.Acm_AxGetCompensateDistance
        Acm_AxGetCompensateDistance.argtypes = [c_void_p, POINTER(c_double)]
        Acm_AxGetCompensateDistance.restype = c_uint32
    except:
        pass