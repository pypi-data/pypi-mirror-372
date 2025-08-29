import numpy as np
from dagsim.base import Graph, Node
from src.simcalibration.dg_models.DagsimModel import DagsimModel

def get_asia():
    if np.random.binomial(n=1, p=0.01):
        return 0
    else:
        return 1

def get_tub(asia):
    if asia == 0:
        if np.random.binomial(n=1, p=0.05):
            return 0
        else:
            return 1
    elif asia == 1:
        if np.random.binomial(n=1, p=0.01):
            return 0
        else:
            return 1

def get_smoker_truth():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_lung_truth(smoke):
    if smoke == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif smoke == 1:
        if np.random.binomial(n=1, p=0.01):
            return 0
        else:
            return 1

def get_bronc_truth(smoke):
    if smoke == 0:
        if np.random.binomial(n=1, p=0.6):
            return 0
        else:
            return 1
    elif smoke == 1:
        if np.random.binomial(n=1, p=0.3):
            return 0
        else:
            return 1

def get_either_truth(lung, tub):
    if lung == 0 or tub == 0:
            return 0
    else:
        return 1

def get_xray_truth(either):
    if either == 0:
        if np.random.binomial(n=1, p=0.98):
            return 0
        else:
            return 1
    elif either == 1:
        if np.random.binomial(n=1, p=0.05):
            return 0
        else:
            return 1

def get_dyspnoea_truth(bronc, either):
    if bronc == 0 and either == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif bronc == 1 and either == 0:
        if np.random.binomial(n=1, p=0.7):
            return 0
        else:
            return 1
    elif bronc == 0 and either == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif bronc == 1 and either == 1:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1

def get_AppOK():
    if np.random.binomial(n=1, p=0.995):
        return 0
    else:
        return 1

def get_DataFile():
    if np.random.binomial(n=1, p=0.995):
        return 0
    else:
        return 1

def get_DskLocal():
    if np.random.binomial(n=1, p=0.97):
        return 0
    else:
        return 1

def get_PrtSpool():
    if np.random.binomial(n=1, p=0.95):
        return 0
    else:
        return 1

def get_PrtOn():
    if np.random.binomial(n=1, p=0.9):
        return 0
    else:
        return 1

def get_PrtPaper():
    if np.random.binomial(n=1, p=0.98):
        return 0
    else:
        return 1

def get_NetPrint():
    if np.random.binomial(n=1, p=0.8):
        return 0
    else:
        return 1

def get_PrtDriver():
    if np.random.binomial(n=1, p=0.9):
        return 0
    else:
        return 1

def get_PrtThread():
    if np.random.binomial(n=1, p=0.9999):
        return 0
    else:
        return 1

def get_DrvSet():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_DrvOK():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_PrtSel():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_PrtPath():
    if np.random.binomial(n=1, p=0.97):
        return 0
    else:
        return 1

def get_NtwrkCnfg():
    if np.random.binomial(n=1, p=0.98):
        return 0
    else:
        return 1

def get_PTROFFLINE():
    if np.random.binomial(n=1, p=0.7):
        return 0
    else:
        return 1

def get_PrtCbl():
    if np.random.binomial(n=1, p=0.98):
        return 0
    else:
        return 1

def get_PrtPort():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_CblPrtHrdwrOK():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_DSApplctn():
    if np.random.binomial(n=1, p=0.15):
        return 0
    else:
        return 1

def get_PrtMpTPth():
    if np.random.binomial(n=1, p=0.8):
        return 0
    else:
        return 1

def get_PrtMem():
    if np.random.binomial(n=1, p=0.95):
        return 0
    else:
        return 1

def get_PrtTimeOut():
    if np.random.binomial(n=1, p=0.94):
        return 0
    else:
        return 1

def get_FllCrrptdBffr():
    if np.random.binomial(n=1, p=0.85):
        return 0
    else:
        return 1

def get_TnrSpply():
    if np.random.binomial(n=1, p=0.995):
        return 0
    else:
        return 1



def get_PgOrnttnOK():
    if np.random.binomial(n=1, p=0.95):
        return 0
    else:
        return 1

def get_PrntngArOK():
    if np.random.binomial(n=1, p=0.98):
        return 0
    else:
        return 1

def get_ScrnFntNtPrntrFnt():
    if np.random.binomial(n=1, p=0.95):
        return 0
    else:
        return 1

def get_GrphcsRltdDrvrSttngs():
    if np.random.binomial(n=1, p=0.95):
        return 0
    else:
        return 1

def get_EPSGrphc():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_PrtPScript():
    if np.random.binomial(n=1, p=0.4):
        return 0
    else:
        return 1

def get_TrTypFnts():
    if np.random.binomial(n=1, p=0.9):
        return 0
    else:
        return 1

def get_FntInstlltn():
    if np.random.binomial(n=1, p=0.98):
        return 0
    else:
        return 1

def get_PrntrAccptsTrtyp():
    if np.random.binomial(n=1, p=0.9):
        return 0
    else:
        return 1

def get_PrtQueue():
    if np.random.binomial(n=1, p=0.99):
        return 0
    else:
        return 1

def get_AppData(AppOK, DataFile):
    if AppOK == 0 and DataFile == 0:
        if np.random.binomial(n=1, p=0.9999):
            return 0
        else:
            return 1
    elif AppOK == 1 and DataFile == 0:
        return 1
    elif AppOK == 0 and DataFile == 1:
        return 1
    elif AppOK == 1 and DataFile == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_EMFOK(AppData, DskLocal, PrtThread):
    if AppData == 0 and DskLocal == 0 and PrtThread == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif AppData == 1 and DskLocal == 0 and PrtThread == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif AppData == 0 and DskLocal == 1 and PrtThread == 0:
            return 1
    elif AppData == 1 and DskLocal == 1 and PrtThread == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and DskLocal == 0 and PrtThread == 1:
        if np.random.binomial(n=1, p=0.05):
            return 0
        else:
            return 1
    elif AppData == 1 and DskLocal == 0 and PrtThread == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and DskLocal == 1 and PrtThread == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and DskLocal == 1 and PrtThread == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_GDIIN(AppData, PrtSpool, EMFOK):
    if AppData == 0 and PrtSpool == 0 and EMFOK == 0:
        return 0
    elif AppData == 1 and PrtSpool == 0 and EMFOK == 0:
        return 1
    elif AppData == 0 and PrtSpool == 1 and EMFOK == 0:
        return 0
    elif AppData == 1 and PrtSpool == 1 and EMFOK == 0:
        return 1
    elif AppData == 0 and PrtSpool == 0 and EMFOK == 1:
        return 1
    elif AppData == 1 and PrtSpool == 0 and EMFOK == 1:
        return 1
    elif AppData == 0 and PrtSpool == 1 and EMFOK == 1:
        return 0
    elif AppData == 1 and PrtSpool == 1 and EMFOK == 1:
        return 1

def get_GDIOUT(PrtDriver, GDIIN, DrvSet, DrvOK):
    if PrtDriver == 0 and GDIIN == 0 and DrvSet == 0 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 0 and DrvSet == 0 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 1 and DrvSet == 0 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 1 and DrvSet == 0 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 0 and DrvSet == 1 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 0 and DrvSet == 1 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 1 and DrvSet == 1 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 1 and DrvSet == 1 and DrvOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 0 and DrvSet == 0 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 0 and DrvSet == 0 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 1 and DrvSet == 0 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 1 and DrvSet == 0 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 0 and DrvSet == 1 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 0 and DrvSet == 1 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 0 and GDIIN == 1 and DrvSet == 1 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtDriver == 1 and GDIIN == 1 and DrvSet == 1 and DrvOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_PrtDataOut(GDIOUT, PrtSel):
    if GDIOUT == 0 and PrtSel == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif GDIOUT == 1 and PrtSel == 0:
        return 1
    elif GDIOUT == 0 and PrtSel == 1:
        return 1
    elif GDIOUT == 1 and PrtSel == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_NetOK(PrtPath, NtwrkCnfg, PTROFFLINE):
    if PrtPath == 0 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif PrtPath == 1 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        return 1
    elif PrtPath == 0 and NtwrkCnfg == 1 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtPath == 1 and NtwrkCnfg == 1 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtPath == 0 and NtwrkCnfg == 0 and PTROFFLINE == 1:
        return 1
    elif PrtPath == 1 and NtwrkCnfg == 0 and PTROFFLINE == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtPath == 0 and NtwrkCnfg == 1 and PTROFFLINE == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtPath == 1 and NtwrkCnfg == 1 and PTROFFLINE == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_LclOK(PrtCbl, PrtPort, CblPrtHrdwrOK):
    if PrtCbl == 0 and PrtPort == 0 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.999):
            return 0
        else:
            return 1
    elif PrtCbl == 1 and PrtPort == 0 and CblPrtHrdwrOK == 0:
        return 1
    elif PrtCbl == 0 and PrtPort == 1 and CblPrtHrdwrOK == 0:
        return 1
    elif PrtCbl == 1 and PrtPort == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtCbl == 0 and PrtPort == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.01):
            return 0
        else:
            return 1
    elif PrtCbl == 1 and PrtPort == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtCbl == 0 and PrtPort == 1 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtCbl == 1 and PrtPort == 1 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_DS_NTOK(AppData, PrtPath, PrtMpTPth, NtwrkCnfg, PTROFFLINE):
    if AppData == 0 and PrtPath == 0 and PrtMpTPth == 0 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtPath == 0 and PrtMpTPth == 0 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtPath == 1 and PrtMpTPth == 0 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        return 1
    elif AppData == 1 and PrtPath == 1 and PrtMpTPth == 0 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtPath == 0 and PrtMpTPth == 1 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        return 1
    elif AppData == 1 and PrtPath == 0 and PrtMpTPth == 1 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtPath == 1 and PrtMpTPth == 1 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtPath == 1 and PrtMpTPth == 1 and NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtPath == 0 and PrtMpTPth == 0 and NtwrkCnfg == 1 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtPath == 0 and PrtMpTPth == 0 and NtwrkCnfg == 1 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtPath == 0 and PrtMpTPth == 0 and NtwrkCnfg == 0 and PTROFFLINE == 1:
        return 1
    else:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_DS_LCLOK(AppData, PrtCbl, PrtPort, CblPrtHrdwrOK):
    if AppData == 0 and PrtCbl == 0 and PrtPort == 0 and CblPrtHrdwrOK == 0:
        return 0
    elif AppData == 1 and PrtCbl == 0 and PrtPort == 0 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtCbl == 1 and PrtPort == 0 and CblPrtHrdwrOK == 0:
        return 1
    elif AppData == 1 and PrtCbl == 1 and PrtPort == 0 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtCbl == 0 and PrtPort == 1 and CblPrtHrdwrOK == 0:
        return 1
    elif AppData == 1 and PrtCbl == 0 and PrtPort == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtCbl == 1 and PrtPort == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtCbl == 1 and PrtPort == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtCbl == 0 and PrtPort == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_PC2PRT(NetPrint, PrtDataOut, NetOK, LclOK, DSApplctn, DS_NTOK, DS_LCLOK):
    if NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 1 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 1 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 0:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 0 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 1 and LclOK == 0 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 0 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 1 and NetOK == 1 and LclOK == 1 and DSApplctn == 0 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 1 and DSApplctn == 1 and DS_NTOK == 0 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 1 and PrtDataOut == 0 and NetOK == 0 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 1:
        return 0
    elif NetPrint == 0 and PrtDataOut == 0 and NetOK == 1 and LclOK == 0 and DSApplctn == 1 and DS_NTOK == 1 and DS_LCLOK == 1:
        return 0
    else:
        return 1

def get_PrtData(PrtOn, PrtPaper, PC2PRT, PrtMem, PrtTimeOut, FllCrrptdBffr, TnrSpply):
    if PrtOn == 0 and PrtPaper == 0 and PC2PRT == 0 and PrtMem == 0 and PrtTimeOut == 0 and FllCrrptdBffr == 0 and TnrSpply == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif PrtOn == 1 and PrtPaper == 0 and PC2PRT == 0 and PrtMem == 0 and PrtTimeOut == 0 and FllCrrptdBffr == 0 and TnrSpply == 0:
        return 1
    elif PrtOn == 0 and PrtPaper == 1 and PC2PRT == 0 and PrtMem == 0 and PrtTimeOut == 0 and FllCrrptdBffr == 0 and TnrSpply == 0:
        return 1
    elif PrtOn == 0 and PrtPaper == 0 and PC2PRT == 1 and PrtMem == 0 and PrtTimeOut == 0 and FllCrrptdBffr == 0 and TnrSpply == 0:
        return 1
    elif PrtOn == 0 and PrtPaper == 0 and PC2PRT == 0 and PrtMem == 1 and PrtTimeOut == 0 and FllCrrptdBffr == 0 and TnrSpply == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtOn == 0 and PrtPaper == 0 and PC2PRT == 0 and PrtMem == 0 and PrtTimeOut == 1 and FllCrrptdBffr == 0 and TnrSpply == 0:
        return 1
    elif PrtOn == 0 and PrtPaper == 0 and PC2PRT == 0 and PrtMem == 0 and PrtTimeOut == 0 and FllCrrptdBffr == 1 and TnrSpply == 0:
        if np.random.binomial(n=1, p=0.02):
            return 0
        else:
            return 1
    elif PrtOn == 0 and PrtPaper == 0 and PC2PRT == 0 and PrtMem == 0 and PrtTimeOut == 0 and FllCrrptdBffr == 0 and TnrSpply == 1:
        if np.random.binomial(n=1, p=0.01):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_Problem1(PrtData):
    if PrtData == 0:
        return 0
    else:
        return 1

def get_AppDtGnTm(PrtSpool):
    if PrtSpool == 0:
        return 0
    else:
        if np.random.binomial(n=1, p=0.99000001):
            return 0
        else:
            return 1

def get_PrntPrcssTm(PrtSpool):
    if PrtSpool == 0:
        if np.random.binomial(n=1, p=0.99000001):
            return 0
        else:
            return 1
    else:
        return 0

def get_DeskPrntSpd(PrtMem, AppDtGnTm, PrntPrcssTm):
    if PrtMem == 0 and AppDtGnTm == 0 and PrntPrcssTm == 0:
        if np.random.binomial(n=1, p=0.99900001):
            return 0
        else:
            return 1
    elif PrtMem == 1 and AppDtGnTm == 0 and PrntPrcssTm == 0:
        if np.random.binomial(n=1, p=0.25):
            return 0
        else:
            return 1
    elif PrtMem == 0 and AppDtGnTm == 1 and PrntPrcssTm == 0:
        if np.random.binomial(n=1, p=0.00099999):
            return 0
        else:
            return 1
    elif PrtMem == 1 and AppDtGnTm == 1 and PrntPrcssTm == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and AppDtGnTm == 0 and PrntPrcssTm == 1:
        if np.random.binomial(n=1, p=0.00099999):
            return 0
        else:
            return 1
    elif PrtMem == 1 and AppDtGnTm == 0 and PrntPrcssTm == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and AppDtGnTm == 1 and PrntPrcssTm == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 1 and AppDtGnTm == 1 and PrntPrcssTm == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_CmpltPgPrntd(PrtMem, PgOrnttnOK, PrntngArOK):
    if PrtMem == 0 and PgOrnttnOK == 0 and PrntngArOK == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    elif PrtMem == 1 and PgOrnttnOK == 0 and PrntngArOK == 0:
        if np.random.binomial(n=1, p=0.3):
            return 0
        else:
            return 1
    elif PrtMem == 0 and PgOrnttnOK == 1 and PrntngArOK == 0:
        if np.random.binomial(n=1, p=0.00999999):
            return 0
        else:
            return 1
    elif PrtMem == 1 and PgOrnttnOK == 1 and PrntngArOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and PgOrnttnOK == 0 and PrntngArOK == 1:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtMem == 1 and PgOrnttnOK == 0 and PrntngArOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and PgOrnttnOK == 1 and PrntngArOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 1 and PgOrnttnOK == 1 and PrntngArOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_NnPSGrphc(PrtMem, GrphcsRltdDrvrSttngs, EPSGrphc):
    if PrtMem == 0 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.999):
            return 0
        else:
            return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.25):
            return 0
        else:
            return 1
    elif PrtMem == 0 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 1:
        return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_PSGRAPHIC(PrtMem, GrphcsRltdDrvrSttngs, EPSGrphc):
    if PrtMem == 0 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.999):
            return 0
        else:
            return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.25):
            return 0
        else:
            return 1
    elif PrtMem == 0 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 1:
        return 0
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 0 and EPSGrphc == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 1 and GrphcsRltdDrvrSttngs == 1 and EPSGrphc == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_Problem4(NnPSGrphc, PrtPScript, PSGRAPHIC):
    if NnPSGrphc == 0 and PrtPScript == 0 and PSGRAPHIC == 0:
        return 1
    elif NnPSGrphc == 1 and PrtPScript == 0 and PSGRAPHIC == 0:
        return 1
    elif NnPSGrphc == 0 and PrtPScript == 1 and PSGRAPHIC == 0:
        return 1
    elif NnPSGrphc == 1 and PrtPScript == 1 and PSGRAPHIC == 0:
        return 0
    elif NnPSGrphc == 0 and PrtPScript == 0 and PSGRAPHIC == 1:
        return 0
    elif NnPSGrphc == 1 and PrtPScript == 0 and PSGRAPHIC == 1:
        return 0
    elif NnPSGrphc == 0 and PrtPScript == 1 and PSGRAPHIC == 1:
        return 1
    elif NnPSGrphc == 1 and PrtPScript == 1 and PSGRAPHIC == 1:
        return 0

def get_TTOK(PrtMem, FntInstlltn, PrntrAccptsTrtyp):
    if PrtMem == 0 and FntInstlltn == 0 and PrntrAccptsTrtyp == 0:
        if np.random.binomial(n=1, p=0.99000001):
            return 0
        else:
            return 1
    elif PrtMem == 1 and FntInstlltn == 0 and PrntrAccptsTrtyp == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and FntInstlltn == 1 and PrntrAccptsTrtyp == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtMem == 1 and FntInstlltn == 1 and PrntrAccptsTrtyp == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and FntInstlltn == 0 and PrntrAccptsTrtyp == 1:
        return 1
    elif PrtMem == 1 and FntInstlltn == 0 and PrntrAccptsTrtyp == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and FntInstlltn == 1 and PrntrAccptsTrtyp == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 1 and FntInstlltn == 1 and PrntrAccptsTrtyp == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_NnTTOK(PrtMem, ScrnFntNtPrntrFnt, FntInstlltn):
    if PrtMem == 0 and ScrnFntNtPrntrFnt == 0 and FntInstlltn == 0:
        if np.random.binomial(n=1, p=0.99000001):
            return 0
        else:
            return 1
    elif PrtMem == 1 and ScrnFntNtPrntrFnt == 0 and FntInstlltn == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and ScrnFntNtPrntrFnt == 1 and FntInstlltn == 0:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtMem == 1 and ScrnFntNtPrntrFnt == 1 and FntInstlltn == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and ScrnFntNtPrntrFnt == 0 and FntInstlltn == 1:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif PrtMem == 1 and ScrnFntNtPrntrFnt == 0 and FntInstlltn == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 0 and ScrnFntNtPrntrFnt == 1 and FntInstlltn == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif PrtMem == 1 and ScrnFntNtPrntrFnt == 1 and FntInstlltn == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_Problem5(TrTypFnts, TTOK, NnTTOK):
    if TrTypFnts == 0 and TTOK == 0 and NnTTOK == 0:
        return 1
    elif TrTypFnts == 1 and TTOK == 0 and NnTTOK == 0:
        return 1
    elif TrTypFnts == 0 and TTOK == 1 and NnTTOK == 0:
        return 0
    elif TrTypFnts == 1 and TTOK == 1 and NnTTOK == 0:
        return 1
    elif TrTypFnts == 0 and TTOK == 0 and NnTTOK == 1:
        return 1
    elif TrTypFnts == 1 and TTOK == 0 and NnTTOK == 1:
        return 0
    elif TrTypFnts == 0 and TTOK == 1 and NnTTOK == 1:
        return 0
    elif TrTypFnts == 1 and TTOK == 1 and NnTTOK == 1:
        return 0

def get_LclGrbld(AppData, PrtDriver, PrtMem, CblPrtHrdwrOK):
    if AppData == 0 and PrtDriver == 0 and PrtMem == 0 and CblPrtHrdwrOK == 0:
        return 0
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 0 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 0 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.4):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 0 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 0 and PrtMem == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 1 and CblPrtHrdwrOK == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 0 and PrtMem == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 0 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 0 and PrtMem == 1 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 1 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 1 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 1 and CblPrtHrdwrOK == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_NtGrbld(AppData, PrtDriver, PrtMem, NtwrkCnfg):
    if AppData == 0 and PrtDriver == 0 and PrtMem == 0 and NtwrkCnfg == 0:
        return 0
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 0 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.3):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 0 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.4):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 0 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 0 and PrtMem == 1 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 1 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 1 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 1 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 0 and PrtMem == 0 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.4):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 0 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 0 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 0 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 0 and PrtMem == 1 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 0 and PrtMem == 1 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 0 and PrtDriver == 1 and PrtMem == 1 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif AppData == 1 and PrtDriver == 1 and PrtMem == 1 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_GrbldOtpt(NetPrint, LclGrbld, NtGrbld):
    if NetPrint == 0 and LclGrbld == 0 and NtGrbld == 0:
        return 0
    elif NetPrint == 1 and LclGrbld == 0 and NtGrbld == 0:
        return 0
    elif NetPrint == 0 and LclGrbld == 1 and NtGrbld == 0:
        return 1
    elif NetPrint == 1 and LclGrbld == 1 and NtGrbld == 0:
        return 0
    elif NetPrint == 0 and LclGrbld == 0 and NtGrbld == 1:
        return 0
    elif NetPrint == 1 and LclGrbld == 0 and NtGrbld == 1:
        return 1
    elif NetPrint == 0 and LclGrbld == 1 and NtGrbld == 1:
        return 1
    elif NetPrint == 1 and LclGrbld == 1 and NtGrbld == 1:
        return 1

def get_HrglssDrtnAftrPrnt(AppDtGnTm):
    if AppDtGnTm == 0:
        if np.random.binomial(n=1, p=0.99):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1

def get_REPEAT(CblPrtHrdwrOK, NtwrkCnfg):
    if CblPrtHrdwrOK == 0 and NtwrkCnfg == 0:
        return 0
    elif CblPrtHrdwrOK == 1 and NtwrkCnfg == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif CblPrtHrdwrOK == 0 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif CblPrtHrdwrOK == 1 and NtwrkCnfg == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_AvlblVrtlMmry(PrtPScript):
    if PrtPScript == 0:
        if np.random.binomial(n=1, p=0.98):
            return 0
        else:
            return 1
    else:
        return 0

def get_PSERRMEM(PrtPScript, AvlblVrtlMmry):
    if PrtPScript == 0 and AvlblVrtlMmry == 0:
        return 0
    elif PrtPScript == 1 and AvlblVrtlMmry == 0:
        return 0
    elif PrtPScript == 0 and AvlblVrtlMmry == 1:
        if np.random.binomial(n=1, p=0.05):
            return 0
        else:
            return 1
    elif PrtPScript == 1 and AvlblVrtlMmry == 1:
        return 0

def get_TstpsTxt(PrtPScript, AvlblVrtlMmry):
    if PrtPScript == 0 and AvlblVrtlMmry == 0:
        if np.random.binomial(n=1, p=0.99900001):
            return 0
        else:
            return 1
    elif PrtPScript == 1 and AvlblVrtlMmry == 0:
        return 0
    elif PrtPScript == 0 and AvlblVrtlMmry == 1:
        if np.random.binomial(n=1, p=0.00099999):
            return 0
        else:
            return 1
    elif PrtPScript == 1 and AvlblVrtlMmry == 1:
        return 0

def get_GrbldPS(GrbldOtpt, AvlblVrtlMmry):
    if GrbldOtpt == 0 and AvlblVrtlMmry == 0:
        return 0
    elif GrbldOtpt == 1 and AvlblVrtlMmry == 0:
        return 1
    elif GrbldOtpt == 0 and AvlblVrtlMmry == 1:
        if np.random.binomial(n=1, p=0.1):
            return 0
        else:
            return 1
    elif GrbldOtpt == 1 and AvlblVrtlMmry == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_IncmpltPS(CmpltPgPrntd, AvlblVrtlMmry):
    if CmpltPgPrntd == 0 and AvlblVrtlMmry == 0:
        return 0
    elif CmpltPgPrntd == 1 and AvlblVrtlMmry == 0:
        return 1
    elif CmpltPgPrntd == 0 and AvlblVrtlMmry == 1:
        if np.random.binomial(n=1, p=0.3):
            return 0
        else:
            return 1
    elif CmpltPgPrntd == 1 and AvlblVrtlMmry == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_PrtFile(PrtDataOut):
    if PrtDataOut == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1

def get_PrtIcon(NtwrkCnfg, PTROFFLINE):
    if NtwrkCnfg == 0 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.9999):
            return 0
        else:
            return 1
    elif NtwrkCnfg == 1 and PTROFFLINE == 0:
        if np.random.binomial(n=1, p=0.25):
            return 0
        else:
            return 1
    elif NtwrkCnfg == 0 and PTROFFLINE == 1:
        if np.random.binomial(n=1, p=0.7):
            return 0
        else:
            return 1
    elif NtwrkCnfg == 1 and PTROFFLINE == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_Problem6(GrbldOtpt, PrtPScript, GrbldPS):
    if GrbldOtpt == 0 and PrtPScript == 0 and GrbldPS == 0:
        return 0
    elif GrbldOtpt == 1 and PrtPScript == 0 and GrbldPS == 0:
        return 0
    elif GrbldOtpt == 0 and PrtPScript == 1 and GrbldPS == 0:
        return 0
    elif GrbldOtpt == 1 and PrtPScript == 1  and GrbldPS == 0:
        return 1
    elif GrbldOtpt == 0 and PrtPScript == 0 and GrbldPS == 1:
        return 1
    elif GrbldOtpt == 1 and PrtPScript == 0 and GrbldPS == 1:
        return 1
    elif GrbldOtpt == 0 and PrtPScript == 1 and GrbldPS == 1:
        return 0
    elif GrbldOtpt == 1 and PrtPScript == 1 and GrbldPS == 1:
        return 1

def get_Problem3(CmpltPgPrntd, PrtPScript, IncmpltPS):
    if CmpltPgPrntd == 0 and PrtPScript == 0 and IncmpltPS == 0:
        return 1
    elif CmpltPgPrntd == 1 and PrtPScript == 0 and IncmpltPS == 0:
        return 1
    elif CmpltPgPrntd == 0 and PrtPScript == 1 and IncmpltPS == 0:
        return 1
    elif CmpltPgPrntd == 1 and PrtPScript == 1  and IncmpltPS == 0:
        return 0
    elif CmpltPgPrntd == 0 and PrtPScript == 0 and IncmpltPS == 1:
        return 0
    elif CmpltPgPrntd == 1 and PrtPScript == 0 and IncmpltPS == 1:
        return 0
    elif CmpltPgPrntd == 0 and PrtPScript == 1 and IncmpltPS == 1:
        return 1
    elif CmpltPgPrntd == 1 and PrtPScript == 1 and IncmpltPS == 1:
        return 0

def get_NtSpd(DeskPrntSpd, NtwrkCnfg, PrtQueue):
    if DeskPrntSpd == 0 and NtwrkCnfg == 0 and PrtQueue == 0:
        if np.random.binomial(n=1, p=0.99900001):
            return 0
        else:
            return 1
    elif DeskPrntSpd == 1 and NtwrkCnfg == 0 and PrtQueue == 0:
        return 1
    elif DeskPrntSpd == 0 and NtwrkCnfg == 1 and PrtQueue == 0:
        if np.random.binomial(n=1, p=0.25):
            return 0
        else:
            return 1
    elif DeskPrntSpd == 1 and NtwrkCnfg == 1 and PrtQueue == 0:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif DeskPrntSpd == 0 and NtwrkCnfg == 0 and PrtQueue == 1:
        if np.random.binomial(n=1, p=0.25):
            return 0
        else:
            return 1
    elif DeskPrntSpd == 1 and NtwrkCnfg == 0 and PrtQueue == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif DeskPrntSpd == 0 and NtwrkCnfg == 1 and PrtQueue == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1
    elif DeskPrntSpd == 1 and NtwrkCnfg == 1 and PrtQueue == 1:
        if np.random.binomial(n=1, p=0.5):
            return 0
        else:
            return 1

def get_Problem2(NetPrint, DeskPrntSpd, NtSpd):
    if NetPrint == 0 and DeskPrntSpd == 0 and NtSpd == 0:
        return 0
    elif NetPrint == 1 and DeskPrntSpd == 0 and NtSpd == 0:
        return 0
    elif NetPrint == 0 and DeskPrntSpd == 1 and NtSpd == 0:
        return 1
    elif NetPrint == 1 and DeskPrntSpd == 1 and NtSpd == 0:
        return 0
    elif NetPrint == 0 and DeskPrntSpd == 0 and NtSpd == 1:
        return 0
    elif NetPrint == 1 and DeskPrntSpd == 0 and NtSpd == 1:
        return 1
    elif NetPrint == 0 and DeskPrntSpd == 1 and NtSpd == 1:
        return 1
    elif NetPrint == 1 and DeskPrntSpd == 1 and NtSpd == 1:
        return 1

def get_PrtStatPaper(PrtPaper):
    if PrtPaper == 0:
        if np.random.binomial(n=1, p=0.99900001):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.00099999):
            return 0
        else:
            return 1

def get_PrtStatToner(TnrSpply):
    if TnrSpply == 0:
        if np.random.binomial(n=1, p=0.99900001):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.00099999):
            return 0
        else:
            return 1

def get_PrtStatMem(PrtMem):
    if PrtMem == 0:
        if np.random.binomial(n=1, p=0.99900001):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1

def get_PrtStatOff(PrtOn):
    if PrtOn == 0:
        if np.random.binomial(n=1, p=0.99000001):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.00999999):
            return 0
        else:
            return 1

def get_printer():
    # DAG Example 2 - Windows 95 Printer, Y=PrtPath (https://www.bnlearn.com/bnrepository/discrete-large.html#win95pts)
    Prior1 = Node(name="AppOK", function=get_AppOK)
    Prior2 = Node(name="DataFile", function=get_DataFile)
    Prior3 = Node(name="AppData", function=get_AppData, args=[Prior1, Prior2])
    Prior4 = Node(name="DskLocal", function=get_DskLocal)
    Prior5 = Node(name="PrtSpool", function=get_PrtSpool)
    Prior6 = Node(name="PrtOn", function=get_PrtOn)
    Prior7 = Node(name="PrtPaper", function=get_PrtPaper)
    Prior8 = Node(name="NetPrint", function=get_NetPrint)
    Prior9 = Node(name="PrtDriver", function=get_PrtDriver)
    Prior10 = Node(name="PrtThread", function=get_PrtThread)
    Prior11 = Node(name="EMFOK", function=get_EMFOK, args=[Prior3, Prior4, Prior10])
    Prior12 = Node(name="GDIIN", function=get_GDIIN, args=[Prior3, Prior5, Prior11])
    Prior13 = Node(name="DrYvSet", function=get_DrvSet)
    Prior14 = Node(name="DrvOK", function=get_DrvOK)
    Prior15 = Node(name="GDIOUT", function=get_GDIOUT, args=[Prior9, Prior12, Prior13, Prior14])
    Prior16 = Node(name="PrtSel", function=get_PrtSel)
    Prior17 = Node(name="PrtDataOut", function=get_PrtDataOut, args=[Prior15, Prior16])
    Prior18 = Node(name="Y", function=get_PrtPath)
    Prior19 = Node(name="NtwrkCnfg", function=get_NtwrkCnfg)
    Prior20 = Node(name="PTROFFLINE", function=get_PTROFFLINE)
    Prior21 = Node(name="NetOK", function=get_NetOK, args=[Prior18, Prior19, Prior20])
    Prior22 = Node(name="PrtCbl", function=get_PrtCbl)
    Prior23 = Node(name="PrtPort", function=get_PrtPort)
    Prior24 = Node(name="CblPrtHrdwrOK", function=get_CblPrtHrdwrOK)
    Prior25 = Node(name="LclOK", function=get_LclOK, args=[Prior22, Prior23, Prior24])
    Prior26 = Node(name="DS_Application", function=get_DSApplctn)
    Prior27 = Node(name="PrtMpTPth", function=get_PrtMpTPth)
    Prior28 = Node(name="DS_NTOK", function=get_DS_NTOK, args=[Prior3, Prior18, Prior27, Prior19, Prior20])
    Prior29 = Node(name="DS_LCLOK", function=get_DS_LCLOK, args=[Prior3, Prior22, Prior23, Prior24])
    Prior30 = Node(name="PC2PRT", function=get_PC2PRT,
                   args=[Prior8, Prior17, Prior21, Prior25, Prior26, Prior28, Prior29])
    Prior31 = Node(name="PrtMem", function=get_PrtMem)
    Prior32 = Node(name="PrtTimeOut", function=get_PrtTimeOut)
    Prior33 = Node(name="FllCrrptdBffr", function=get_FllCrrptdBffr)
    Prior34 = Node(name="TnrSpply", function=get_TnrSpply)
    Prior35 = Node(name="PrtData", function=get_PrtData,
                   args=[Prior6, Prior7, Prior30, Prior31, Prior32, Prior33, Prior34])
    Prior36 = Node(name="Problem1", function=get_Problem1, args=[Prior35])
    Prior37 = Node(name="AppDtGnTm", function=get_AppDtGnTm, args=[Prior5])
    Prior38 = Node(name="PrntPrcssTm", function=get_PrntPrcssTm, args=[Prior5])
    Prior39 = Node(name="DeskPrntSpd", function=get_DeskPrntSpd, args=[Prior31, Prior37, Prior38])
    Prior40 = Node(name="PgOrnttnOK", function=get_PgOrnttnOK)
    Prior41 = Node(name="PrntngArOK", function=get_PrntngArOK)
    Prior42 = Node(name="ScrnFntNtPrntrFnt", function=get_ScrnFntNtPrntrFnt)
    Prior43 = Node(name="CmpltPgPrntd", function=get_CmpltPgPrntd, args=[Prior31, Prior40, Prior41])
    Prior44 = Node(name="GrphcsRltdDrvrSttngs", function=get_GrphcsRltdDrvrSttngs)
    Prior45 = Node(name="EPSGrphc", function=get_EPSGrphc)
    Prior46 = Node(name="NnPSGrphc", function=get_NnPSGrphc, args=[Prior31, Prior44, Prior45])
    Prior47 = Node(name="PrtPScript", function=get_PrtPScript)
    Prior48 = Node(name="PSGRAPHIC", function=get_PSGRAPHIC, args=[Prior31, Prior44, Prior45])
    Prior49 = Node(name="Problem4", function=get_Problem4, args=[Prior46, Prior47, Prior48])
    Prior50 = Node(name="TrTypFnts", function=get_TrTypFnts)
    Prior51 = Node(name="FntInstlltn", function=get_FntInstlltn)
    Prior52 = Node(name="PrntrAccptsTrtyp", function=get_PrntrAccptsTrtyp)
    Prior53 = Node(name="TTOK", function=get_TTOK, args=[Prior31, Prior51, Prior52])
    Prior54 = Node(name="NnTTOK", function=get_NnTTOK, args=[Prior31, Prior42, Prior51])
    Prior55 = Node(name="Problem5", function=get_Problem5, args=[Prior50, Prior53, Prior54])
    Prior56 = Node(name="LclGrbld", function=get_LclGrbld, args=[Prior3, Prior9, Prior31, Prior24])
    Prior57 = Node(name="NtGrbld", function=get_LclGrbld, args=[Prior3, Prior9, Prior31, Prior19])
    Prior58 = Node(name="GrbldOtpt", function=get_GrbldOtpt, args=[Prior8, Prior56, Prior57])
    Prior59 = Node(name="HrglssDrtnAftrPrnt", function=get_HrglssDrtnAftrPrnt, args=[Prior38])
    Prior60 = Node(name="REPEAT", function=get_REPEAT, args=[Prior24, Prior19])
    Prior61 = Node(name="AvlblVrtlMmry", function=get_AvlblVrtlMmry, args=[Prior47])
    Prior62 = Node(name="PSERRMEM", function=get_PSERRMEM, args=[Prior47, Prior61])
    Prior63 = Node(name="TstpsTxt", function=get_TstpsTxt, args=[Prior47, Prior61])
    Prior64 = Node(name="GrbldPS", function=get_GrbldPS, args=[Prior58, Prior61])
    Prior65 = Node(name="IncmpltPS", function=get_IncmpltPS, args=[Prior43, Prior61])
    Prior66 = Node(name="PrtFile", function=get_PrtFile, args=[Prior17])
    Prior67 = Node(name="PrtIcon", function=get_PrtIcon, args=[Prior19, Prior20])
    Prior68 = Node(name="Problem6", function=get_Problem6, args=[Prior58, Prior47, Prior64])
    Prior69 = Node(name="Problem3", function=get_Problem3, args=[Prior43, Prior47, Prior65])
    Prior70 = Node(name="PrtQueue", function=get_PrtQueue)
    Prior71 = Node(name="NtSpd", function=get_NtSpd, args=[Prior39, Prior19, Prior70])
    Prior72 = Node(name="Problem2", function=get_Problem2, args=[Prior8, Prior39, Prior71])
    Prior73 = Node(name="PrtStatPaper", function=get_PrtStatPaper, args=[Prior7])
    Prior74 = Node(name="PrtStatToner", function=get_PrtStatToner, args=[Prior34])
    Prior75 = Node(name="PrtStatMem", function=get_PrtStatMem, args=[Prior31])
    Prior76 = Node(name="PrtStatOff", function=get_PrtStatOff, args=[Prior6])

    listNodes = [Prior1, Prior2, Prior3, Prior4, Prior5, Prior6, Prior7, Prior8, Prior9, Prior10, Prior11, Prior12,
                 Prior13, Prior14, Prior15, Prior16, Prior17, Prior18, Prior19, Prior20, Prior21, Prior22, Prior23,
                 Prior24, Prior25, Prior26, Prior27, Prior28, Prior29, Prior30, Prior31, Prior32, Prior33, Prior34,
                 Prior35, Prior36, Prior37, Prior38, Prior39, Prior40, Prior41, Prior42, Prior43, Prior44, Prior45,
                 Prior46, Prior47, Prior48, Prior49, Prior50, Prior51, Prior52, Prior53, Prior54, Prior55, Prior56,
                 Prior57, Prior58, Prior59, Prior60, Prior61, Prior62, Prior63, Prior64, Prior65, Prior66, Prior67,
                 Prior68, Prior69, Prior70, Prior71, Prior72, Prior73, Prior74, Prior75, Prior76]
    printer = Graph(name="Windows 95 Printer Example - Real-world", list_nodes=listNodes)
    ds_model = DagsimModel("Real-world", printer)
    return ds_model

def get_asia():
    # DAG Example 1 - Asia Cancer, Y=Dysponea (https://www.bnlearn.com/bnrepository/discrete-small.html#asia)
    Prior1 = Node(name="Asia", function=get_asia)
    Prior2 = Node(name="Tub", function=get_tub, args=[Prior1])
    Prior3 = Node(name="Smoke", function=get_smoker_truth)
    Prior4 = Node(name="Lung", function=get_lung_truth, args=[Prior3])
    Prior5 = Node(name="Bronc", function=get_bronc_truth, args=[Prior3])
    Prior6 = Node(name="Either", function=get_either_truth, args=[Prior2, Prior4])
    Prior7 = Node(name="Xray", function=get_xray_truth, args=[Prior6])
    Prior8 = Node(name="Y", function=get_dyspnoea_truth, args=[Prior5, Prior6])

    listNodes = [Prior1, Prior2, Prior3, Prior4, Prior5, Prior6, Prior7, Prior8]
    asia = Graph(name="Asia Cancer Dysponea Example - Real-world", list_nodes=listNodes)
    ds_model = DagsimModel("Real-world", asia)
    return ds_model


































