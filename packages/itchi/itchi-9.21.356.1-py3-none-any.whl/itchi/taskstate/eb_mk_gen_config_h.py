import logging
import re
import sys
import itchi.taskstate.single_variable as task_state_single_variable
import itchi.type_enum
from itchi.ortilib.orti import Orti, OrtiEnum
from dataclasses import dataclass
from pathlib import Path
from typing import List
from itchi.profilerxml.model import ProfilerXml, ProfilerObject, TypeEnum, Enum
from itchi.config import ItchiConfig


@dataclass
class EbThread:
    expr: str
    name: str
    core: int


def get_task_threads(mk_gen_config_h: Path) -> List[EbThread]:
    r = re.compile(
        r"&(MK_c\d_taskThreads\[\d+\])"  # expression
        r".*?"  # non-greedy match all
        r'"(\S+)",'  # task name
        r".*?"  # non-greedy match all
        r"Task name"  # to be sure we got the name
        r".*?"  # non-greedy match all
        r"(\d+),"  # core ID
        r".*?"  # non-greedy match all
        r"core",  # to be sure we got everything
        re.DOTALL,
    )
    with open(mk_gen_config_h, "r") as f:
        return [
            EbThread(expr=m[0] + ".state", name=m[1], core=int(m[2])) for m in r.findall(f.read())
        ]


def get_isr_threads(mk_gen_config_h: Path) -> List[EbThread]:
    r = re.compile(
        r"&(MK_c\d_isrThreads\[\d+\])"  # expression
        r".*?"  # non-greedy match all
        r'"(\S+)",'  # isr name
        r".*?"  # non-greedy match all
        r"ISR name"  # to be sure we got the name
        r".*?"  # non-greedy match all
        r"(\d+),"  # core ID
        r".*?"  # non-greedy match all
        r"core",  # to be sure we got everything
        re.DOTALL,
    )
    with open(mk_gen_config_h, "r") as f:
        return [
            EbThread(expr=m[0] + ".state", name=m[1], core=int(m[2])) for m in r.findall(f.read())
        ]


def get_core_count(threads: List[EbThread]) -> int:
    return max((t.core for t in threads)) + 1


def get_special_threads(core_count: int) -> List[EbThread]:
    threads = []
    for core in range(core_count):
        threads.append(EbThread(f"MK_c{core}_aux1Thread.state", f"Aux1_Core{core}", core))
        threads.append(EbThread(f"MK_c{core}_aux2Thread.state", f"Aux2_Core{core}", core))
        threads.append(EbThread(f"MK_c{core}_idleThread.state", f"Idle_Core{core}", core))
    return threads


def get_thread_objects(core_count: int) -> List[ProfilerObject]:
    thread_objects = []
    for core in range(core_count):
        area = f"Core {core}: Threads"
        p = ProfilerObject(
            name=area,
            definition=area,
            description=area,
            type=itchi.type_enum.TASK_MAPPING_MULTI_CORE.format(core),
            default_value=f"Idle_Core{core}",
            expression="$(EnumType)",
            level="Task",
            core=str(core),
        )
        thread_objects.append(p)
    return thread_objects


def get_mk_gen_config_h_fake_enum():
    return [
        OrtiEnum(desc="MK_THS_IDLE", const=0),
        OrtiEnum(desc="MK_THS_READY", const=1),
        OrtiEnum(desc="MK_THS_RUNNING", const=2),
        OrtiEnum(desc="MK_THS_NEW", const=3),
    ]


def get_thread_mapping_type_enums(threads: List[EbThread]) -> List[TypeEnum]:
    core_count = get_core_count(threads)
    type_enums: List[TypeEnum] = [
        TypeEnum(name=itchi.type_enum.TASK_MAPPING_MULTI_CORE.format(core_id), enums=[])
        for core_id in range(core_count)
    ]

    for index, thread in enumerate(threads):
        thread_enum = Enum(
            thread.name, str(index), name_property="Expression", value_property=thread.expr
        )
        type_enums[thread.core].enums.append(thread_enum)
    return type_enums


def task_state_eb_mk_gen_config_h(orti: Orti, profiler_xml: ProfilerXml, config: ItchiConfig):
    """Implement task state profiling based on a single state variable.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object
        config (ItchiConfig): iTCHi config object
    """
    if not config.task_state:
        return

    logging.info("Running task_state_single_variable for EB with Mk_gen_config.h.")
    if not config.task_state.autocore_mk_gen_config_h.is_file():
        logging.critical("Mk_gen_config.h is configured but does not exist.")
        sys.exit(1)

    threads = get_task_threads(config.task_state.autocore_mk_gen_config_h)
    threads += get_isr_threads(config.task_state.autocore_mk_gen_config_h)
    core_count = get_core_count(threads)
    threads += get_special_threads(core_count)
    profiler_xml.num_cores = core_count

    # Hack to not duplicate code. EB MK_gen_config_h ORTI does not have this enum.
    setattr(orti, "get_enum_elements_task_state", get_mk_gen_config_h_fake_enum)
    for thread in get_thread_objects(core_count):
        thread.task_state = task_state_single_variable.get_task_state(orti)
        thread.task_state.btf_mapping_type = itchi.type_enum.BTF_MAPPING
        profiler_xml.set_object(thread)

    # Add type enums that contain expression for each thread and core.
    for type_enum in get_thread_mapping_type_enums(threads):
        profiler_xml.set_type_enum(type_enum)

    # Add enum that maps task state IDs to task state names.
    task_state_type_enum = TypeEnum(
        name=itchi.type_enum.TASK_STATE_MAPPING,
        enums=[
            Enum(enum.desc, str(enum.const))
            for enum in get_mk_gen_config_h_fake_enum()
            if isinstance(enum.const, int) or isinstance(enum.const, str)
        ],
    )
    profiler_xml.set_type_enum(task_state_type_enum)

    # Add BTF mapping for task states.
    states = [enum.desc for enum in get_mk_gen_config_h_fake_enum()]
    btf_type_enum = itchi.type_enum.get_btf_mapping_type_enum(states)
    profiler_xml.set_type_enum(btf_type_enum)
