from typing import List
from itchi.profilerxml.model import TypeEnum, Enum, BtfTransition


SPINLOCKS = "TypeEnum_SpinLocks"
SPINLOCK_STATE = "TypeEnum_SpinLockState"
TASK_MAPPING_MULTI_CORE = "TypeEnum_TaskMapping[{}]"
TASK_STATE_MAPPING = "TypeEnum_TaskStateMapping"
BTF_MAPPING = "TypeEnum_BTFMapping"
THREAD_MAPPING = "TypeEnum_ThreadMapping"
ARTI_MDF4 = "TypeEnum_ARTIMDF4"
TASK_MAPPING = "TypeEnum_TaskMapping"
BTF_TASK_MAPPING = "TypeEnum_BTF_Task_Mapping"
BTF_ISR_MAPPING = "TypeEnum_BTF_ISR_Mapping"
RUNNABLE_MAPPING = "TypeEnum_RunnableMapping"


def get_btf_mapping_type_enum(states: List[str]) -> TypeEnum:
    """Get BTF state mapping only for the states that are in the ORTI
    file.

    Args:
        states List[str]: List of state name string

    Returns:
        TypeEnum: Mapping from states to BTF events
    """
    enums: List[Enum] = [
        Enum("NEW", "Active"),
        Enum("NEW_ISR", "Active"),
        Enum("MK_THS_NEW", "Active"),
        Enum("READY", "Ready"),
        Enum("READY_ASYNC", "Ready"),
        Enum("READY_ISR", "Ready"),
        Enum("READY_SYNC", "Ready"),
        Enum("READY_TASK", "Ready"),
        Enum("READ_ASYNC", "Ready"),
        Enum("MK_THS_READY", "Ready"),
        Enum("DELAYED", "Ready"),
        Enum("RUNNING", "Running"),
        Enum("RUNNING_ISR", "Running"),
        Enum("MK_THS_RUNNING", "Running"),
        Enum("WAITING_EVENT", "Waiting"),
        Enum("WAITING_SEM", "Waiting"),
        Enum("WAITING_DELAYED", "Waiting"),
        Enum("WAITING", "Waiting"),
        Enum("TERMINATED_TASK", "Terminated"),
        Enum("TERMINATED_ISR", "Terminated"),
        Enum("INVALID", "Terminated"),
        Enum("QUARANTINED", "Terminated"),
        Enum("SUSPENDED", "Terminated"),
        Enum("SUSPENDED_DELAYABLE", "Terminated"),
        Enum("INVALID", "Terminated"),
        Enum("MK_THS_IDLE", "Terminated"),
    ]

    # Only write those Enums into the Profiler XML whose corresponding state is part
    # of the ORTI file.
    enums = [enum for enum in enums if enum.name in states]

    # Special BTF transitions to follow BTF spec more closely.
    properties = [
        BtfTransition(text="Terminated-Ready:Active"),
        BtfTransition(text="Unknown-Ready:Active"),
    ]

    return TypeEnum(name=BTF_MAPPING, properties=properties, enums=enums)
