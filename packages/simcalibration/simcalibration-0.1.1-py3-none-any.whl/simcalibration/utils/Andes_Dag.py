import numpy as np
from dagsim.base import Graph, Node
from src.simcalibration.dg_models.DagsimModel import DagsimModel

def get_GOAL_2():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_3():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_4():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_5():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_6():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_7():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_DISPLACEM0():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_RApp1(DISPLACEM0, SNode_3):
    if DISPLACEM0 == 0 and SNode_3 == 0:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif DISPLACEM0 == 1 and SNode_3 == 0:
        return 1
    elif DISPLACEM0 == 0 and SNode_3 == 1:
        return 1
    elif DISPLACEM0 == 1 and SNode_3 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1

def get_GIVEN_1():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_RApp2(GIVEN_1):
    if GIVEN_1 == 0:
        return 0
    elif GIVEN_1 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1

def get_SNode_8(RApp1, RApp2):
    if RApp1 == 0 and RApp2 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif RApp1 == 1 and RApp2 == 0:
        return 1
    elif RApp1 == 0 and RApp2 == 1:
        return 1
    elif RApp1 == 1 and RApp2 == 1:
        return 1

def get_SNode_9():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_10():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_11():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_12():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_13():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_14():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_15():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_16():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_17():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_18():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_SNode_19():
    if np.random.binomial(n=1, p=0.02):
        return 0
    else:
        return 1

def get_NEED1():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_20(SNode_16, NEED1):
    if SNode_16 == 0 and NEED1 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_16 == 1 and NEED1 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_16 == 0 and NEED1 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_16 == 1 and NEED1 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_GRAV2():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_21(SNode_20, GRAV2):
    if SNode_20 == 0 and GRAV2 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_20 == 1 and GRAV2 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_20 == 0 and GRAV2 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_20 == 1 and GRAV2 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_VALUE3():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_24(SNode_21, VALUE3):
    if SNode_21 == 0 and VALUE3 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_21 == 1 and VALUE3 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_21 == 0 and VALUE3 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_21 == 1 and VALUE3 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1

def get_SLIDING4():
    if np.random.binomial(n=1, p=0.1):
        return 0
    else:
        return 1

def get_SNode_25(SNode_15, SLIDING4):
    if SNode_15 == 0 and SLIDING4 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_15 == 1 and SLIDING4 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_15 == 0 and SLIDING4 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_15 == 1 and SLIDING4 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1

def get_CONSTANT5():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_26(SNode_11, CONSTANT5):
    if SNode_11 == 0 and CONSTANT5 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_11 == 1 and CONSTANT5 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_11 == 0 and CONSTANT5 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_11 == 1 and CONSTANT5 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_KNOWN6():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_VELOCITY7():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_47(SNode_3, VELOCITY7):
    if SNode_3 == 0 and VELOCITY7 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_3 == 1 and VELOCITY7 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_3 == 0 and VELOCITY7 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_3 == 1 and VELOCITY7 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_RApp3(KNOWN6, SNode_26, SNode_47):
    if KNOWN6 == 0 and SNode_26 == 0 and SNode_47 == 0:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 1 and SNode_26 == 0 and SNode_47 == 0:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 0 and SNode_26 == 1 and SNode_47 == 0:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 1 and SNode_26 == 1 and SNode_47 == 0:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 0 and SNode_26 == 0 and SNode_47 == 1:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 1 and SNode_26 == 0 and SNode_47 == 0:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 0 and SNode_26 == 1 and SNode_47 == 1:
        if np.random.binomial(n=1, p=1):
            return 0
        else:
            return 1
    elif KNOWN6 == 1 and SNode_26 == 1 and SNode_47 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1

def get_KNOWN8():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_RApp4(KNOWN8, SNode_11):
    if KNOWN8 == 0 and SNode_11 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif KNOWN8 == 1 and SNode_11 == 0:
        if np.random.binomial(n=1, p=0):
            return 0
        else:
            return 1
    elif KNOWN8 == 0 and SNode_11 == 1:
        if np.random.binomial(n=1, p=0):
            return 0
        else:
            return 1
    elif KNOWN8 == 1 and SNode_11 == 1:
        if np.random.binomial(n=1, p=0):
            return 0
        else:
            return 1

def get_SNode_27(RApp3, RApp4):
    if RApp3 == 0 and RApp4 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif RApp3 == 1 and RApp4 == 0:
        if np.random.binomial(n=1, p=0):
            return 0
        else:
            return 1
    elif RApp3 == 0 and RApp4 == 1:
        if np.random.binomial(n=1, p=0):
            return 0
        else:
            return 1
    elif RApp3 == 1 and RApp4 == 1:
        if np.random.binomial(n=1, p=0):
            return 0
        else:
            return 1

def get_COMPO16():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_48(GOAL_2, COMPO16):
    if GOAL_2 == 0 and COMPO16 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif GOAL_2 == 1 and COMPO16 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif GOAL_2 == 0 and COMPO16 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif GOAL_2 == 1 and COMPO16 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_TRY12():
    if np.random.binomial(n=1, p=0.7):
        return 0
    else:
        return 1

def get_TRY11(TRY12):
    if TRY12 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif TRY12 == 1:
        return 1

def get_GOAL_49(SNode_5, SNode_6, GOAL_48, TRY11):
    if SNode_5 == 1 and SNode_6 == 1 and GOAL_48 == 1 and TRY11 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return

def get_CHOOSE19():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_50(GOAL_49, CHOOSE19):
    if GOAL_49 == 1 and CHOOSE19 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SYSTEM18():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_51(SNode_17, GOAL_50, SYSTEM18):
    if SNode_17 == 0 and GOAL_50 == 0 and SYSTEM18 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 1 and GOAL_50 == 0 and SYSTEM18 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 0 and GOAL_50 == 1 and SYSTEM18 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 1 and GOAL_50 == 1 and SYSTEM18 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 0 and GOAL_50 == 0 and SYSTEM18 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 1 and GOAL_50 == 0 and SYSTEM18 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 0 and GOAL_50 == 1 and SYSTEM18 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_17 == 1 and GOAL_50 == 1 and SYSTEM18 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1

def get_KINEMATI17():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_52(SNode_51, KINEMATI17):
    if SNode_51 == 0 and KINEMATI17 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_51 == 1 and KINEMATI17 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_51 == 0 and KINEMATI17 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_51 == 1 and KINEMATI17 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_IDENTIFY10():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_53(GOAL_49, SNode_52, IDENTIFY10):
    if GOAL_49 == 1 and SNode_52 == 1 and IDENTIFY10 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY9():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_28(SNode_27, GOAL_53, IDENTIFY9):
    if SNode_27 == 1 and GOAL_53 == 1 and IDENTIFY9 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_TRY13(TRY12):
    if TRY12 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif TRY12 == 1:
        return 1

def get_TRY14(TRY12):
    if TRY12 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif TRY12 == 1:
        return 1

def get_TRY15(TRY12):
    if TRY12 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif TRY12 == 1:
        return 1

def get_VAR20():
    if np.random.binomial(n=1, p=0.3):
        return 0
    else:
        return 1

def get_SNode_29(SNode_28, VAR20):
    if SNode_28 == 0 and VAR20 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_28 == 1 and VAR20 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_28 == 0 and VAR20 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_28 == 1 and VAR20 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_SNode_31(SNode_29, VALUE3):
    if SNode_29 == 0 and VALUE3 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_29 == 1 and VALUE3 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_29 == 0 and VALUE3 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_29 == 1 and VALUE3 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1

def get_GIVEN21():
    if np.random.binomial(n=1, p=0.1):
        return 0
    else:
        return 1

def get_SNode_33(SNode_10, GIVEN21):
    if SNode_10 == 0 and GIVEN21 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_10 == 1 and GIVEN21 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_10 == 0 and GIVEN21 == 1:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif SNode_10 == 1 and GIVEN21 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1

def get_SNode_34(SNode_10, CONSTANT5):
    if SNode_10 == 0 and CONSTANT5 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_10 == 1 and CONSTANT5 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_10 == 0 and CONSTANT5 == 1:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif SNode_10 == 1 and CONSTANT5 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1

def get_VECTOR27():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_APPLY32():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_56(GOAL_49, SNode_52, APPLY32):
    if GOAL_49 == 1 and SNode_52 == 1 and APPLY32 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_CHOOSE35():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_57(GOAL_56, CHOOSE35):
    if GOAL_56 == 1 and CHOOSE35 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_MAXIMIZE34():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_59(SNode_7, GOAL_57, MAXIMIZE34):
    if SNode_7 == 1 and GOAL_57 == 1 and MAXIMIZE34 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_AXIS33():
    if np.random.binomial(n=1, p=0.2):
        return 0
    else:
        return 1

def get_SNode_60(SNode_59, AXIS33):
    if SNode_59 == 1 and AXIS33 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_WRITE31():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_61(GOAL_56, SNode_60, WRITE31):
    if GOAL_56 == 1 and SNode_60 == 1 and WRITE31 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_WRITE30():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_62(GOAL_61, WRITE30):
    if GOAL_61 == 1 and WRITE30 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RESOLVE37():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_63(SNode_28, GOAL_62, RESOLVE37):
    if SNode_28 == 1 and GOAL_62 == 1 and RESOLVE37 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_NEED36():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_64(GOAL_63, NEED36):
    if GOAL_63 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_41(SNode_9, CONSTANT5):
    if SNode_9 == 1 and CONSTANT5 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_42(SNode_8, SNode_41, KNOWN6):
    if SNode_8 == 1 and SNode_41 == 1 and KNOWN6 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY39():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_43(SNode_42, GOAL_53, IDENTIFY39):
    if SNode_42 == 1 and GOAL_53 == 1 and IDENTIFY39 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RESOLVE38():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_66(SNode_43, GOAL_62, RESOLVE38):
    if SNode_43 == 1 and GOAL_62 == 1 and RESOLVE38 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_67(GOAL_66, NEED36):
    if GOAL_66 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY41():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_54(GOAL_53, IDENTIFY41):
    if GOAL_53 == 1 and IDENTIFY41 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RESOLVE40():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_69(SNode_54, GOAL_62, RESOLVE40):
    if SNode_54 == 1 and GOAL_62 == 1 and RESOLVE40 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_70(GOAL_69, NEED36):
    if GOAL_69 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY43():
    if np.random.binomial(n=1, p=0.6):
        return 0
    else:
        return 1

def get_SNode_55(SNode_34, GOAL_53, IDENTIFY43):
    if SNode_34 == 1 and GOAL_53 == 1 and IDENTIFY43 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RESOLVE42():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_72(SNode_55, GOAL_62, RESOLVE42):
    if SNode_55 == 1 and GOAL_62 == 1 and RESOLVE42 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_73(GOAL_72, NEED36):
    if GOAL_72 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_KINE29():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_74(GOAL_62, SNode_64, SNode_67, SNode_70, SNode_73, KINE29):
    if GOAL_62 == 1 and SNode_64 == 1 and SNode_67 == 1 and SNode_70 == 1 and SNode_73 == 1 and KINE29 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_VECTOR44():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_75(SNode_4, GOAL_72, SNode_73, VECTOR44):
    if SNode_4 == 1 and GOAL_72 == 1 and SNode_73 == 1 and VECTOR44 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_EQUATION28():
    if np.random.binomial(n=1, p=0.6):
        return 0
    else:
        return 1

def get_GOAL_79(SNode_74, SNode_75, EQUATION28):
    if SNode_74 == 1 and SNode_75 == 1 and EQUATION28 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RApp5(VECTOR27, GOAL_79):
    if VECTOR27 == 1 and GOAL_79 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_GOAL_80(SNode_75, EQUATION28):
    if SNode_75 == 1 and EQUATION28 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RApp6(COMPO16, GOAL_80):
    if COMPO16 == 1 and GOAL_80 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_GOAL_81(RApp5, RApp6):
    if RApp5 == 0 and RApp6 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    else:
        return 1

def get_TRY25():
    if np.random.binomial(n=1, p=0.1):
        return 0
    else:
        return 1

def get_TRY24(TRY25):
    if TRY25 == 0:
        if np.random.binomial(n=1, p=0.95):
            return 0
        else:
            return 1
    elif TRY25 == 1:
        return 1

def get_GOAL_83(GOAL_81, TRY24):
    if GOAL_81 == 1 and TRY24 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_CHOOSE47():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_84(GOAL_83, CHOOSE47):
    if GOAL_83 == 1 and CHOOSE47 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SYSTEM46():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_86(GOAL_84, SYSTEM46):
    if GOAL_84 == 1 and SYSTEM46 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_NEWTONS45():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_156(SNode_86, NEWTONS45):
    if SNode_86 == 1 and NEWTONS45 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_DEFINE23():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_98(GOAL_83, SNode_156, DEFINE23):
    if GOAL_83 == 1 and SNode_156 == 1 and DEFINE23 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY22():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_37(GOAL_98, IDENTIFY22):
    if GOAL_98 == 1 and IDENTIFY22 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_TRY26(TRY25):
    if TRY25 == 0:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1
    elif TRY25 == 1:
        return 1

def get_SNode_38(SNode_37, VAR20):
    if SNode_37 == 1 and VAR20 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_40(SNode_38, VALUE3):
    if SNode_38 == 1 and VALUE3 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_44(SNode_43, VAR20):
    if SNode_43 == 1 and VAR20 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_46(SNode_44, VALUE3):
    if SNode_44 == 1 and VALUE3 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_NULL48():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_65(SNode_29, GOAL_63, SNode_64, NULL48):
    if SNode_29 == 1 and GOAL_63 == 1 and SNode_64 == 1 and NULL48 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_68(GOAL_66, SNode_67, VECTOR44):
    if GOAL_66 == 1 and SNode_67 == 1 and VECTOR44 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_71(GOAL_69, SNode_70, VECTOR44):
    if GOAL_69 == 1 and SNode_70 == 1 and VECTOR44 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_FIND49():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_87(GOAL_83, SNode_156, FIND49):
    if GOAL_83 == 1 and SNode_156 == 1 and FIND49 == 1:
        if np.random.binomial(n=1, p=0.00007):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.7):
            return 0
        else:
            return 1

def get_NORMAL50():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_88(SNode_25, GOAL_87, NORMAL50):
    if SNode_25 == 1 and GOAL_87 == 1 and NORMAL50 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_STRAT_90():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_NORMAL52():
    if np.random.binomial(n=1, p=0.646):
        return 0
    else:
        return 1

def get_INCLINE51(NORMAL52):
    if NORMAL52 == 0:
        return 0
    else:
        return 1

def get_SNode_91(SNode_88, SNode_12, SNode_13, STRAT_90, INCLINE51):
    if SNode_88 == 1 and SNode_12 == 1 and SNode_13 == 1 and STRAT_90 == 1 and INCLINE51 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_HORIZ53(NORMAL52):
    if NORMAL52 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    elif NORMAL52 == 1:
        return 1


def get_BUGGY54(NORMAL52):
    if NORMAL52 == 0:
        if np.random.binomial(n=1, p=0.2):
            return 0
        else:
            return 1
    elif NORMAL52 == 1:
        return 0

def get_SNode_92(SNode_12, STRAT_90, BUGGY54):
    if SNode_12 == 1 and STRAT_90 == 0 and BUGGY54 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY55():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_93(GOAL_87, SNode_88, IDENTIFY55):
    if GOAL_87 == 1 and SNode_88 == 1 and IDENTIFY55 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_WEIGHT56():
    if np.random.binomial(n=1, p=0.3):
        return 0
    else:
        return 1

def get_SNode_94(SNode_16, SNode_33, GOAL_87, WEIGHT56):
    if SNode_16 == 1 and SNode_33 == 1 and GOAL_87 == 1 and WEIGHT56 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_WEIGHT57():
    if np.random.binomial(n=1, p=0.3):
        return 0
    else:
        return 1

def get_SNode_95(SNode_94, WEIGHT57):
    if SNode_94 == 1 and WEIGHT57 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_97(GOAL_87, SNode_94, IDENTIFY55):
    if GOAL_87 == 1 and SNode_94 == 1 and IDENTIFY55 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_FIND58():
    if np.random.binomial(n=1, p=0.7):
        return 0
    else:
        return 1

def get_GOAL_99(GOAL_98, FIND58):
    if GOAL_98 == 1 and FIND58 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_IDENTIFY59():
    if np.random.binomial(n=1, p=0.7):
        return 0
    else:
        return 1

def get_SNode_100(GOAL_98, IDENTIFY59):
    if GOAL_98 == 1 and IDENTIFY59 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_FORCE60():
    if np.random.binomial(n=1, p=0.2):
        return 0
    else:
        return 1

def get_SNode_102(GOAL_87, SNode_88, SNode_94, FORCE60):
    if GOAL_87 == 1 and SNode_88 == 1 and SNode_94 == 1 and FORCE60 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_APPLY61():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_103(GOAL_83, SNode_102, APPLY61):
    if GOAL_83 == 1 and SNode_102 == 1 and APPLY61 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_CHOOSE62():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_104(GOAL_103, CHOOSE62):
    if GOAL_103 == 1 and CHOOSE62 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_106(GOAL_104, MAXIMIZE34):
    if GOAL_104 == 1 and MAXIMIZE34 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_152(SNode_106, AXIS33):
    if SNode_106 == 1 and AXIS33 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_WRITE63():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_107(GOAL_103, SNode_152, WRITE63):
    if GOAL_103 == 1 and SNode_152 == 1 and WRITE63 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_WRITE64():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_108(GOAL_107, WRITE64):
    if GOAL_107 == 1 and WRITE64 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL_109(GOAL_107, WRITE64):
    if GOAL_107 == 1 and WRITE64 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL65():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_110(GOAL_109, GOAL65):
    if GOAL_109 == 1 and GOAL65 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL66():
    if np.random.binomial(n=1, p=0.6):
        return 0
    else:
        return 1

def get_GOAL_111(GOAL_109, GOAL66):
    if GOAL_109 == 1 and GOAL66 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_NEED67():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_RApp7(NEED67, GOAL_109):
    if NEED67 == 1 and GOAL_109 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_RApp8(NEED36, GOAL_111):
    if NEED36 == 1 and GOAL_111 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_SNode_112(RApp7, RApp8):
    if RApp7 == 0 and RApp8 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    else:
        return 1

def get_GOAL68():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_113(GOAL_110, GOAL68):
    if GOAL_110 == 1 and GOAL68 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL_114(GOAL_110, GOAL68):
    if GOAL_110 == 1 and GOAL68 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_115(GOAL_114, NEED36):
    if GOAL_114 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_VECTOR69():
    if np.random.binomial(n=1, p=0.7):
        return 0
    else:
        return 1

def get_SNode_116(SNode_95, SNode_97, GOAL_114, SNode_115, VECTOR69):
    if SNode_95 == 1 and SNode_97 == 1 and GOAL_114 == 1 and SNode_115 == 1 and VECTOR69 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_117(GOAL_113, NEED36):
    if GOAL_113 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_VECTOR70():
    if np.random.binomial(n=1, p=0.1):
        return 0
    else:
        return 1

def get_SNode_118(SNode_91, GOAL_113, VECTOR70):
    if SNode_91 == 1 and GOAL_113 == 1 and VECTOR70 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_EQUAL71():
    if np.random.binomial(n=1, p=0.4):
        return 0
    else:
        return 1

def get_SNode_119(SNode_93, SNode_117, SNode_118, EQUAL71):
    if SNode_93 == 1 and SNode_117 == 1 and SNode_118 == 1 and EQUAL71 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_120(SNode_92, SNode_93, GOAL_113, SNode_117, VECTOR69):
    if SNode_92 == 1 and SNode_93 == 1 and GOAL_113 == 1 and SNode_117 == 1 and VECTOR69 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_GOAL72():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_121(GOAL_109, GOAL72):
    if GOAL_109 == 1 and GOAL72 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_122(GOAL_121, NEED36):
    if GOAL_121 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_VECTOR73():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_123(SNode_4, SNode_100, GOAL_121, SNode_122, VECTOR73):
    if SNode_4 == 1 and SNode_100 == 1 and GOAL_121 == 1 and SNode_122 == 1 and VECTOR73 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_NEWTONS74():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_124(SNode_37, GOAL_109, SNode_112, SNode_122, NEWTONS74):
    if SNode_37 == 1 and GOAL_109 == 1 and SNode_112 == 1 and SNode_122 == 1 and NEWTONS74 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SUM75():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_125(GOAL_109, SNode_112, SUM75):
    if GOAL_109 == 1 and SNode_112 == 1 and SUM75 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_GOAL_126(GOAL_108, GOAL65):
    if GOAL_108 == 1 and GOAL65 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL_127(GOAL_108, GOAL66):
    if GOAL_108 == 1 and GOAL66 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RApp9(NEED67, GOAL_108):
    if NEED67 == 1 and GOAL_108 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_RApp10(NEED36, GOAL_127):
    if NEED36 == 1 and GOAL_127 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_SNode_128(RApp9, RApp10):
    if RApp9 == 0 and RApp10 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    else:
        return 1

def get_GOAL_129(GOAL_126, GOAL68):
    if GOAL_126 == 1 and GOAL68 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL_130(GOAL_126, GOAL68):
    if GOAL_126 == 1 and GOAL68 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_131(GOAL_130, NEED36):
    if GOAL_130 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_132(SNode_95, SNode_97, GOAL_130, SNode_131, VECTOR69):
    if SNode_95 == 1 and SNode_97 == 1 and GOAL_130 == 1 and SNode_131 == 1 and VECTOR69 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_133(GOAL_129, NEED36):
    if GOAL_129 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_134(SNode_91, SNode_93, GOAL_129, SNode_133, VECTOR73):
    if SNode_91 == 1 and SNode_93 == 1 and GOAL_129 == 1 and SNode_133 == 1 and VECTOR73 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_135(SNode_92, SNode_93, GOAL_129, SNode_133, VECTOR69):
    if SNode_92 == 1 and SNode_93 == 1 and GOAL_129 == 1 and SNode_133 == 1 and VECTOR69 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_154(GOAL_121, NEED36):
    if GOAL_121 == 1 and NEED36 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_136(SNode_37, GOAL_108, SNode_128, SNode_154, NEWTONS74):
    if SNode_37 == 1 and GOAL_108 == 1 and SNode_128 == 1 and SNode_154 == 1 and NEWTONS74 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_SNode_137(GOAL_108, SNode_128, SUM75):
    if GOAL_108 == 1 and SNode_128 == 1 and SUM75 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_GOAL_142(SNode_116, SNode_125, EQUATION28):
    if SNode_116 == 1 and SNode_125 == 1 and EQUATION28 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL_143(SNode_116, SNode_132, EQUATION28):
    if SNode_116 == 1 and SNode_132 == 1 and EQUATION28 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GOAL_146(SNode_132, SNode_137, EQUATION28):
    if SNode_132 == 1 and SNode_137 == 1 and EQUATION28 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_RApp11(VECTOR27, GOAL_142):
    if VECTOR27 == 1 and GOAL_142 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_RApp12(COMPO16, GOAL_143):
    if COMPO16 == 1 and GOAL_143 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_RApp13(VECTOR27, GOAL_146):
    if VECTOR27 == 1 and GOAL_146 == 1:
        if np.random.binomial(n=1, p=0.0001):
            return 0
        else:
            return 1
    else:
        return 0

def get_GOAL_147(RApp11, RApp12, RApp13):
    if RApp11 == 0 and RApp12 == 0 and RApp13 == 0:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1
    else:
        return 1

def get_TRY76():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_149(GOAL_147, TRY76):
    if GOAL_147 == 1 and TRY76 == 1:
        if np.random.binomial(n=1, p=0.00007):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.7):
            return 0
        else:
            return 1

def get_APPLY77():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_GOAL_150(SNode_20, SNode_37, GOAL_149, APPLY77):
    if SNode_20 == 1 and SNode_37 == 1 and GOAL_149 == 1 and APPLY77 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_GRAV78():
    if np.random.binomial(n=1, p=0.5):
        return 0
    else:
        return 1

def get_SNode_151(GOAL_150, GRAV78):
    if GOAL_150 == 1 and GRAV78 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_GOAL_153(GOAL_108, GOAL72):
    if GOAL_108 == 1 and GOAL72 == 1:
        if np.random.binomial(n=1, p=0.00008):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.8):
            return 0
        else:
            return 1

def get_SNode_155(Node_4, SNode_100, GOAL_153, SNode_154, VECTOR44):
    if Node_4 == 1 and SNode_100 == 1 and GOAL_153 == 1 and SNode_154 == 1 and VECTOR44 == 1:
        if np.random.binomial(n=1, p=0.00009):
            return 0
        else:
            return 1
    else:
        if np.random.binomial(n=1, p=0.9):
            return 0
        else:
            return 1

def get_andes():
    # DAG Example 3 - Andes, Y=SNode_151 (https://www.bnlearn.com/bnrepository/discrete-verylarge.html#andes)
    Prior1 = Node(name="GOAL_2", function=get_GOAL_2)
    Prior2 = Node(name="SNode_3", function=get_SNode_3)
    Prior3 = Node(name="SNode_4", function=get_SNode_4)
    Prior4 = Node(name="SNode_5", function=get_SNode_5)
    Prior5 = Node(name="SNode_6", function=get_SNode_6)
    Prior6 = Node(name="SNode_7", function=get_SNode_7)
    Prior7 = Node(name="DISPLACEM0", function=get_DISPLACEM0)
    Prior8 = Node(name="RApp1", function=get_RApp1, args=[Prior7, Prior2])
    Prior9 = Node(name="GIVEN_1", function=get_GIVEN_1)
    Prior10 = Node(name="RApp2", function=get_RApp2, args=[Prior9])
    Prior11 = Node(name="SNode_8", function=get_SNode_8, args=[Prior8, Prior10])
    Prior12 = Node(name="SNode_9", function=get_SNode_9)
    Prior13 = Node(name="SNode_10", function=get_SNode_10)
    Prior14 = Node(name="SNode_11", function=get_SNode_11)
    Prior15 = Node(name="SNode_12", function=get_SNode_12)
    Prior16 = Node(name="SNode_13", function=get_SNode_13)
    Prior17 = Node(name="SNode_14", function=get_SNode_14)
    Prior18 = Node(name="SNode_15", function=get_SNode_15)
    Prior19 = Node(name="SNode_16", function=get_SNode_16)
    Prior20 = Node(name="SNode_17", function=get_SNode_17)
    Prior21 = Node(name="SNode_18", function=get_SNode_18)
    Prior22 = Node(name="SNode_19", function=get_SNode_19)
    Prior23 = Node(name="NEED1", function=get_NEED1)
    Prior24 = Node(name="SNode_20", function=get_SNode_20, args=[Prior19, Prior23])
    Prior25 = Node(name="GRAV2", function=get_GRAV2)
    Prior26 = Node(name="SNode_21", function=get_SNode_21, args=[Prior24, Prior25])
    Prior27 = Node(name="VALUE3", function=get_VALUE3)
    Prior28 = Node(name="SNode_24", function=get_SNode_24, args=[Prior26, Prior27])
    Prior29 = Node(name="SLIDING4", function=get_SLIDING4)
    Prior30 = Node(name="SNode_25", function=get_SNode_25, args=[Prior18, Prior29])
    Prior31 = Node(name="CONSTANT5", function=get_CONSTANT5)
    Prior32 = Node(name="SNode_26", function=get_SNode_26, args=[Prior14, Prior31])
    Prior33 = Node(name="KNOWN6", function=get_KNOWN6)
    Prior34 = Node(name="VELOCITY7", function=get_VELOCITY7)
    Prior35 = Node(name="SNode_47", function=get_SNode_47, args=[Prior2, Prior34])
    Prior36 = Node(name="RApp3", function=get_RApp3, args=[Prior33, Prior32, Prior35])
    Prior37 = Node(name="KNOWN8", function=get_KNOWN8)
    Prior38 = Node(name="RApp4", function=get_RApp4, args=[Prior37, Prior14])
    Prior39 = Node(name="SNode_27", function=get_SNode_27, args=[Prior36, Prior38])
    Prior40 = Node(name="COMPO16", function=get_COMPO16)
    Prior41 = Node(name="GOAL_48", function=get_GOAL_48, args=[Prior1, Prior40])
    Prior42 = Node(name="TRY12", function=get_TRY12)
    Prior43 = Node(name="TRY11", function=get_TRY11, args=[Prior42])
    Prior44 = Node(name="GOAL_49", function=get_GOAL_49, args=[Prior4, Prior5, Prior41, Prior43])
    Prior45 = Node(name="CHOOSE19", function=get_CHOOSE19)
    Prior46 = Node(name="GOAL_50", function=get_GOAL_50, args=[Prior44, Prior45])
    Prior47 = Node(name="SYSTEM18", function=get_SYSTEM18)
    Prior48 = Node(name="SNode_51", function=get_SNode_51, args=[Prior20, Prior46, Prior47])
    Prior49 = Node(name="KINEMATI17", function=get_KINEMATI17)
    Prior50 = Node(name="SNode_52", function=get_SNode_52, args=[Prior48, Prior49])
    Prior51 = Node(name="IDENTIFY10", function=get_IDENTIFY10)
    Prior52 = Node(name="GOAL_53", function=get_GOAL_53, args=[Prior44, Prior50, Prior51])
    Prior53 = Node(name="IDENTIFY9", function=get_IDENTIFY9)
    Prior54 = Node(name="SNode_28", function=get_SNode_28, args=[Prior39, Prior52, Prior53])
    Prior55 = Node(name="TRY13", function=get_TRY13, args=[Prior42])
    Prior56 = Node(name="TRY14", function=get_TRY14, args=[Prior42])
    Prior57 = Node(name="TRY15", function=get_TRY15, args=[Prior42])
    Prior58 = Node(name="VAR20", function=get_VAR20)
    Prior59 = Node(name="SNode_29", function=get_SNode_29, args=[Prior54, Prior56])
    Prior60 = Node(name="SNode_31", function=get_SNode_31, args=[Prior57, Prior27])
    Prior61 = Node(name="GIVEN21", function=get_GIVEN21)
    Prior62 = Node(name="SNode_33", function=get_SNode_33, args=[Prior13, Prior59])
    Prior63 = Node(name="SNode_34", function=get_SNode_34, args=[Prior13, Prior31])
    Prior64 = Node(name="VECTOR27", function=get_VECTOR27)
    Prior65 = Node(name="APPLY32", function=get_APPLY32)
    Prior66 = Node(name="GOAL_56", function=get_GOAL_56, args=[Prior44, Prior50, Prior65])
    Prior67 = Node(name="CHOOSE35", function=get_CHOOSE35)
    Prior68 = Node(name="GOAL_57", function=get_GOAL_57, args=[Prior66, Prior67])
    Prior69 = Node(name="MAXIMIZE34", function=get_MAXIMIZE34)
    Prior70 = Node(name="SNode_59", function=get_SNode_59, args=[Prior6, Prior68, Prior69])
    Prior71 = Node(name="AXIS33", function=get_AXIS33)
    Prior72 = Node(name="SNode_60", function=get_SNode_60, args=[Prior70, Prior71])
    Prior73 = Node(name="WRITE31", function=get_WRITE31)
    Prior74 = Node(name="GOAL_61", function=get_GOAL_61, args=[Prior66, Prior72, Prior73])
    Prior75 = Node(name="WRITE30", function=get_WRITE30)
    Prior76 = Node(name="GOAL_62", function=get_GOAL_62, args=[Prior74, Prior75])
    Prior77 = Node(name="RESOLVE37", function=get_RESOLVE37)
    Prior78 = Node(name="GOAL_63", function=get_GOAL_63, args=[Prior54, Prior76, Prior77])
    Prior79 = Node(name="NEED36", function=get_NEED36)
    Prior80 = Node(name="SNode_64", function=get_SNode_64, args=[Prior78, Prior79])
    Prior81 = Node(name="SNode_41", function=get_SNode_41, args=[Prior12, Prior31])
    Prior82 = Node(name="SNode_42", function=get_SNode_42, args=[Prior11, Prior81, Prior33])
    Prior83 = Node(name="IDENTIFY39", function=get_IDENTIFY39)
    Prior84 = Node(name="SNode_43", function=get_SNode_43, args=[Prior82, Prior52, Prior83])
    Prior85 = Node(name="RESOLVE38", function=get_RESOLVE38)
    Prior86 = Node(name="GOAL_66", function=get_GOAL_66, args=[Prior84, Prior76, Prior85])
    Prior87 = Node(name="SNode_67", function=get_SNode_67, args=[Prior86, Prior79])
    Prior88 = Node(name="IDENTIFY41", function=get_IDENTIFY41)
    Prior89 = Node(name="SNode_54", function=get_SNode_54, args=[Prior52, Prior88])
    Prior90 = Node(name="RESOLVE40", function=get_RESOLVE40)
    Prior91 = Node(name="GOAL_69", function=get_GOAL_69, args=[Prior89, Prior76, Prior90])
    Prior92 = Node(name="SNode_70", function=get_SNode_70, args=[Prior91, Prior79])
    Prior93 = Node(name="IDENTIFY43", function=get_IDENTIFY43)
    Prior94 = Node(name="SNode_55", function=get_SNode_55, args=[Prior63, Prior52, Prior93])
    Prior95 = Node(name="RESOLVE42", function=get_RESOLVE42)
    Prior96 = Node(name="GOAL_72", function=get_GOAL_72, args=[Prior94, Prior76, Prior95])
    Prior97 = Node(name="SNode_73", function=get_SNode_73, args=[Prior96, Prior79])
    Prior98 = Node(name="KINE29", function=get_KINE29)
    Prior99 = Node(name="SNode_74", function=get_SNode_74, args=[Prior76, Prior80, Prior87, Prior92, Prior97, Prior98])
    Prior100 = Node(name="VECTOR44", function=get_VECTOR44)
    Prior101 = Node(name="SNode_75", function=get_SNode_75, args=[Prior3, Prior96, Prior97, Prior100])
    Prior102 = Node(name="EQUATION28", function=get_EQUATION28)
    Prior103 = Node(name="GOAL_79", function=get_GOAL_79, args=[Prior99, Prior101, Prior102])
    Prior104 = Node(name="RApp5", function=get_RApp5, args=[Prior64, Prior103])
    Prior105 = Node(name="GOAL_80", function=get_GOAL_80, args=[Prior101, Prior102])
    Prior106 = Node(name="RApp6", function=get_RApp6, args=[Prior40, Prior105])
    Prior107 = Node(name="GOAL_81", function=get_GOAL_81, args=[Prior104, Prior106])
    Prior108 = Node(name="TRY25", function=get_TRY25)
    Prior109 = Node(name="TRY24", function=get_TRY24, args=[Prior108])
    Prior110 = Node(name="GOAL_83", function=get_GOAL_83, args=[Prior107, Prior109])
    Prior111 = Node(name="CHOOSE47", function=get_CHOOSE47)
    Prior112 = Node(name="GOAL_84", function=get_GOAL_84, args=[Prior110, Prior111])
    Prior113 = Node(name="SYSTEM46", function=get_SYSTEM46)
    Prior114 = Node(name="SNode_86", function=get_SNode_86, args=[Prior112, Prior113])
    Prior115 = Node(name="NEWTONS45", function=get_NEWTONS45)
    Prior116 = Node(name="SNode_156", function=get_SNode_156, args=[Prior114, Prior115])
    Prior117 = Node(name="DEFINE23", function=get_DEFINE23)
    Prior118 = Node(name="GOAL_98", function=get_GOAL_98, args=[Prior110, Prior116, Prior117])
    Prior119 = Node(name="IDENTIFY22", function=get_IDENTIFY22)
    Prior120 = Node(name="SNode_37", function=get_SNode_37, args=[Prior118, Prior119])
    Prior121 = Node(name="TRY26", function=get_TRY26, args=[Prior108])
    Prior122 = Node(name="SNode_38", function=get_SNode_38, args=[Prior120, Prior58])
    Prior123 = Node(name="SNode_40", function=get_SNode_40, args=[Prior122, Prior27])
    Prior124 = Node(name="SNode_44", function=get_SNode_44, args=[Prior82, Prior56])
    Prior125 = Node(name="Y", function=get_SNode_46, args=[Prior124, Prior27])  # Continue Test here
    Prior126 = Node(name="NULL48", function=get_NULL48)
    Prior127 = Node(name="SNode_65", function=get_SNode_65, args=[Prior59, Prior78, Prior80, Prior126])
    Prior128 = Node(name="SNode_68", function=get_SNode_68, args=[Prior86, Prior87, Prior100])
    Prior129 = Node(name="SNode_71", function=get_SNode_71, args=[Prior91, Prior92, Prior100])
    Prior130 = Node(name="FIND49", function=get_FIND49)
    Prior131 = Node(name="GOAL_87", function=get_GOAL_87, args=[Prior110, Prior116, Prior130])
    Prior132 = Node(name="NORMAL50", function=get_NORMAL50)
    Prior133 = Node(name="SNode_88", function=get_SNode_88, args=[Prior30, Prior131, Prior132])
    Prior134 = Node(name="STRAT_90", function=get_STRAT_90)
    Prior135 = Node(name="NORMAL52", function=get_NORMAL52)
    Prior136 = Node(name="INCLINE51", function=get_INCLINE51, args=[Prior135])
    Prior137 = Node(name="SNode_91", function=get_SNode_91, args=[Prior133, Prior15, Prior16, Prior134, Prior136])
    Prior138 = Node(name="HORIZ53", function=get_HORIZ53, args=[Prior135])
    Prior139 = Node(name="BUGGY54", function=get_BUGGY54, args=[Prior135])
    Prior140 = Node(name="SNode_92", function=get_SNode_92, args=[Prior15, Prior134, Prior139])
    Prior141 = Node(name="IDENTIFY55", function=get_IDENTIFY55)
    Prior142 = Node(name="SNode_93", function=get_SNode_93, args=[Prior131, Prior133, Prior141])
    Prior143 = Node(name="WEIGHT56", function=get_WEIGHT56)
    Prior144 = Node(name="SNode_94", function=get_SNode_94, args=[Prior19, Prior62, Prior131, Prior143])
    Prior145 = Node(name="WEIGHT57", function=get_WEIGHT57)
    Prior146 = Node(name="get_SNode_95", function=get_SNode_95, args=[Prior144, Prior145])
    Prior147 = Node(name="SNode_97", function=get_SNode_97, args=[Prior131, Prior144, Prior141])
    Prior148 = Node(name="get_FIND58", function=get_FIND58)
    Prior149 = Node(name="GOAL_99", function=get_GOAL_99, args=[Prior118, Prior148])
    Prior150 = Node(name="IDENTIFY59", function=get_IDENTIFY59)
    Prior151 = Node(name="SNode_100", function=get_SNode_100, args=[Prior118, Prior150])
    Prior152 = Node(name="FORCE60", function=get_FORCE60)
    Prior153 = Node(name="SNode_102", function=get_SNode_102, args=[Prior131, Prior133, Prior144, Prior152])
    Prior154 = Node(name="APPLY61", function=get_APPLY61)
    Prior155 = Node(name="GOAL_103", function=get_GOAL_103, args=[Prior110, Prior153, Prior154])
    Prior156 = Node(name="CHOOSE62", function=get_CHOOSE62)
    Prior157 = Node(name="GOAL_104", function=get_GOAL_104, args=[Prior155, Prior156])
    Prior158 = Node(name="SNode_106", function=get_SNode_106, args=[Prior157, Prior69])
    Prior159 = Node(name="SNode_152", function=get_SNode_152, args=[Prior158, Prior71])
    Prior160 = Node(name="WRITE63", function=get_WRITE63)
    Prior161 = Node(name="GOAL_107", function=get_GOAL_107, args=[Prior155, Prior159, Prior160])
    Prior162 = Node(name="WRITE64", function=get_WRITE64)
    Prior163 = Node(name="GOAL_108", function=get_GOAL_108, args=[Prior161, Prior162])
    Prior164 = Node(name="GOAL_109", function=get_GOAL_109, args=[Prior161, Prior162])
    Prior165 = Node(name="GOAL65", function=get_GOAL65)
    Prior166 = Node(name="GOAL_110", function=get_GOAL_110, args=[Prior164, Prior165])
    Prior167 = Node(name="GOAL66", function=get_GOAL66)
    Prior168 = Node(name="GOAL_111", function=get_GOAL_111, args=[Prior164, Prior167])
    Prior169 = Node(name="NEED67", function=get_NEED67)
    Prior170 = Node(name="RApp7", function=get_RApp7, args=[Prior169, Prior164])
    Prior171 = Node(name="RApp8", function=get_RApp8, args=[Prior79, Prior168])
    Prior172 = Node(name="SNode_112", function=get_SNode_112, args=[Prior170, Prior171])
    Prior173 = Node(name="GOAL68", function=get_GOAL68)
    Prior174 = Node(name="GOAL_113", function=get_GOAL_113, args=[Prior166, Prior173])
    Prior175 = Node(name="GOAL_114", function=get_GOAL_114, args=[Prior166, Prior173])
    Prior176 = Node(name="SNode_115", function=get_SNode_115, args=[Prior175, Prior79])
    Prior177 = Node(name="VECTOR69", function=get_VECTOR69)
    Prior178 = Node(name="SNode_116", function=get_SNode_116, args=[Prior146, Prior147, Prior175, Prior176, Prior177])
    Prior179 = Node(name="SNode_117", function=get_SNode_117, args=[Prior174, Prior79])
    Prior180 = Node(name="VECTOR70", function=get_VECTOR70)
    Prior181 = Node(name="SNode_118", function=get_SNode_118, args=[Prior137, Prior174, Prior180])
    Prior182 = Node(name="EQUAL71", function=get_EQUAL71)
    Prior183 = Node(name="SNode_119", function=get_SNode_119, args=[Prior142, Prior179, Prior181, Prior182])
    Prior184 = Node(name="SNode_120", function=get_SNode_120, args=[Prior140, Prior142, Prior174, Prior179, Prior180])
    Prior185 = Node(name="GOAL72", function=get_GOAL72)
    Prior186 = Node(name="GOAL_121", function=get_GOAL_121, args=[Prior164, Prior185])
    Prior187 = Node(name="SNode_122", function=get_SNode_122, args=[Prior186, Prior79])
    Prior188 = Node(name="VECTOR73", function=get_VECTOR73)
    Prior189 = Node(name="SNode_123", function=get_SNode_123, args=[Prior3, Prior151, Prior186, Prior187, Prior188])
    Prior190 = Node(name="NEWTONS74", function=get_NEWTONS74)
    Prior191 = Node(name="SNode_124", function=get_SNode_124, args=[Prior120, Prior164, Prior172, Prior187, Prior190])
    Prior192 = Node(name="SUM75", function=get_SUM75)
    Prior193 = Node(name="SNode_125", function=get_SNode_125, args=[Prior164, Prior172, Prior192])
    Prior194 = Node(name="GOAL_126", function=get_GOAL_126, args=[Prior163, Prior165])
    Prior195 = Node(name="GOAL_127", function=get_GOAL_127, args=[Prior163, Prior167])
    Prior196 = Node(name="RApp9", function=get_RApp9, args=[Prior169, Prior163])
    Prior197 = Node(name="RApp10", function=get_RApp10, args=[Prior79, Prior195])
    Prior198 = Node(name="SNode_128", function=get_SNode_128, args=[Prior194, Prior195])
    Prior199 = Node(name="GOAL_129", function=get_GOAL_129, args=[Prior194, Prior173])
    Prior200 = Node(name="GOAL_130", function=get_GOAL_130, args=[Prior194, Prior173])
    Prior201 = Node(name="SNode_131", function=get_SNode_131, args=[Prior200, Prior79])
    Prior202 = Node(name="SNode_132", function=get_SNode_132, args=[Prior146, Prior147, Prior200, Prior201, Prior177])
    Prior203 = Node(name="SNode_133", function=get_SNode_133, args=[Prior199, Prior79])
    Prior204 = Node(name="SNode_134", function=get_SNode_134, args=[Prior137, Prior142, Prior199, Prior203, Prior188])
    Prior205 = Node(name="SNode_135", function=get_SNode_135, args=[Prior140, Prior142, Prior199, Prior203, Prior177])
    Prior206 = Node(name="SNode_154", function=get_SNode_154, args=[Prior186, Prior79])
    Prior207 = Node(name="SNode_136", function=get_SNode_136, args=[Prior120, Prior163, Prior198, Prior206, Prior190])
    Prior208 = Node(name="SNode_137", function=get_SNode_137, args=[Prior163, Prior198, Prior192])
    Prior209 = Node(name="GOAL_142", function=get_GOAL_142, args=[Prior178, Prior193, Prior102])
    Prior210 = Node(name="GOAL_143", function=get_GOAL_143, args=[Prior178, Prior202, Prior102])
    Prior211 = Node(name="GOAL_146", function=get_GOAL_146, args=[Prior202, Prior208, Prior102])
    Prior212 = Node(name="RApp11", function=get_RApp11, args=[Prior64, Prior209])
    Prior213 = Node(name="RApp12", function=get_RApp12, args=[Prior40, Prior210])
    Prior214 = Node(name="RApp13", function=get_RApp13, args=[Prior64, Prior211])
    Prior215 = Node(name="GOAL_147", function=get_GOAL_147, args=[Prior212, Prior213, Prior214])
    Prior216 = Node(name="TRY76", function=get_TRY76)
    Prior217 = Node(name="GOAL_149", function=get_GOAL_149, args=[Prior215, Prior216])
    Prior218 = Node(name="APPLY77", function=get_APPLY77)
    Prior219 = Node(name="GOAL_150", function=get_GOAL_150, args=[Prior24, Prior120, Prior217, Prior218])
    Prior220 = Node(name="GRAV78", function=get_GRAV78)
    Prior221 = Node(name="SNode_151", function=get_SNode_151, args=[Prior219, Prior220])
    Prior222 = Node(name="GOAL_153", function=get_GOAL_153, args=[Prior163, Prior185])
    Prior223 = Node(name="SNode_155", function=get_SNode_155, args=[Prior3, Prior151, Prior222, Prior206, Prior100])
    # Y is IDENTIFY9, Top=SNode_29, SNode_28, SNode_34, SNode_59, SNode_64, SNode_92, SNode_67, SNode_73, SNode_54, SNode_151, SNode_152, SNode_154, SNode_137, SNode_128, SNode_125,SNode_40, GOAL_57, GOAL_62, GOAL_83, GOAL_80, GOAL_127, GOAL_121, GOAL_113, GOAL_110, GOAL_109,GOAL_107,GOAL_103 RApp10/RApp9, GOAL_126
    listNodes = [Prior1, Prior2, Prior3, Prior4, Prior5, Prior6, Prior7, Prior8, Prior9, Prior10, Prior11, Prior12,
                 Prior13, Prior14, Prior15, Prior16, Prior17, Prior18, Prior19, Prior20, Prior21, Prior22, Prior23,
                 Prior24, Prior25, Prior26, Prior27, Prior28, Prior29, Prior30, Prior31, Prior32, Prior33, Prior34,
                 Prior35, Prior36, Prior37, Prior38, Prior39, Prior40, Prior41, Prior42, Prior43, Prior44, Prior45,
                 Prior46, Prior47, Prior48, Prior49, Prior50, Prior51, Prior52, Prior53, Prior54, Prior55, Prior56,
                 Prior57, Prior58, Prior59, Prior60, Prior61, Prior62, Prior63, Prior64, Prior65, Prior66, Prior67,
                 Prior68, Prior69, Prior70, Prior71, Prior72, Prior73, Prior74, Prior75, Prior76, Prior77, Prior78,
                 Prior79, Prior80, Prior81, Prior82, Prior83, Prior84, Prior85, Prior86, Prior87, Prior88, Prior89,
                 Prior90, Prior91, Prior92, Prior93, Prior94, Prior95, Prior96, Prior97, Prior98, Prior99, Prior100,
                 Prior101, Prior102, Prior103, Prior104, Prior105, Prior106, Prior107, Prior108, Prior109, Prior110,
                 Prior111, Prior112, Prior113, Prior114, Prior115, Prior116, Prior117, Prior118, Prior119, Prior120,
                 Prior121, Prior122, Prior123, Prior124, Prior125, Prior126, Prior127, Prior128, Prior129, Prior130,
                 Prior131, Prior132, Prior133, Prior134, Prior135, Prior136, Prior137, Prior138, Prior139, Prior140,
                 Prior141, Prior142, Prior143, Prior144, Prior145, Prior146, Prior147, Prior148, Prior149, Prior150,
                 Prior151, Prior152, Prior153, Prior154, Prior155, Prior156, Prior157, Prior158, Prior159, Prior160,
                 Prior161, Prior162, Prior163, Prior164, Prior165, Prior166, Prior167, Prior168, Prior169, Prior170,
                 Prior171, Prior172, Prior173, Prior174, Prior175, Prior176, Prior177, Prior178, Prior179, Prior180,
                 Prior181, Prior182, Prior183, Prior184, Prior185, Prior186, Prior187, Prior188, Prior189, Prior190,
                 Prior191, Prior192, Prior193, Prior194, Prior195, Prior196, Prior197, Prior198, Prior199, Prior200,
                 Prior201, Prior202, Prior203, Prior204, Prior205, Prior206, Prior207, Prior208, Prior209, Prior210,
                 Prior211, Prior212, Prior213, Prior214, Prior215, Prior216, Prior217, Prior218, Prior219, Prior220,
                 Prior221, Prior222, Prior223]
    andes = Graph(name="Andes Example - Real-world", list_nodes=listNodes)
    # andes.draw()
    ds_model = DagsimModel("Real-world", andes)
    return ds_model
