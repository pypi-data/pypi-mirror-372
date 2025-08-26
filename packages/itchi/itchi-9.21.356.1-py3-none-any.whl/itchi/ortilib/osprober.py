from .orti import Orti
from enum import Enum


class Os(Enum):
    MICROSAR = "Vector MICROSAR OS"
    AUTOCORE = "Elektrobit AutoCore OS"
    AUTOCORE_MK = "Elektrobit AutoCore OS MK (similar to Safety OS)"
    SAFETYOS = "Elektrobit Safety OS"
    RTAOS = "ETAS RTA-OS"
    KSAR = "KPIT KSAR OS"
    ERIKA = "Erika Enterprise OS"
    FREERTOS = "FreeRTOS"
    UNKNOWN = "Unknown OS"


def probe(orti: Orti) -> Os:
    try:
        for enum in orti.get_enum_elements_runningtask():
            formula = enum.formula
            if formula is None:
                continue

            if formula.startswith("&OsCfg_Trace"):
                return Os.MICROSAR

            if formula.startswith("Os_const_tasks"):
                return Os.RTAOS

            if formula.startswith("&Os_const_tasks"):
                return Os.RTAOS

            if formula.startswith("&OS_taskTable"):
                return Os.AUTOCORE

            if formula.startswith("&Os_GaaStaticTask"):
                return Os.KSAR
    except AssertionError:
        # Some OSs don't have the RUNNINGTASK ENUM (violating the ORTI spec)
        pass

    try:
        for enum in orti.get_enum_elements("OS", "vs_RUNNINGTHREAD"):
            formula = enum.formula
            if formula is None:
                continue

            if formula.startswith("MK_taskCfgTable"):
                return Os.AUTOCORE_MK

    except AssertionError:
        # AutoCore OS (and maybe Safety OS) are the only OSs that have a RUNNINGTHREAD ENUM
        pass

    try:
        for enum in orti.get_enum_elements("OS", "RUNNINGTASK"):
            formula = enum.formula
            if formula is None:
                continue

            if formula.startswith("EE_stkfirst"):
                return Os.ERIKA
    except AssertionError:
        # There are OS that do not have a RUNNINGTASK object (even though ORTI requires it)
        pass

    return Os.UNKNOWN
