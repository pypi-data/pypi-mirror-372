import logging
from typing import List
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml, ProfilerObject


def running_taskisr(orti: Orti, profiler_xml: ProfilerXml) -> ProfilerXml:
    """Update the Profiler XML object with the objects for Running Task/ISR
    tracing. In general, winIDEA can handle this use case by itself. However,
    we might want to override the default object, get rid of pointers, or
    we might need this objects for advanced use cases.

    Args:
        orti (Orti): ORTI object
        profiler_xml (ProfilerXml): Profiler XML object

    Returns:
        ProfilerXml: The same updated Profiler XML object
    """
    logging.info("Running 'running_taskisr'.")
    tasks = get_task_objects(orti)
    isr2s = get_isr2_objects(orti)
    for task, isr in zip(tasks, isr2s):
        profiler_xml.set_object(task)
        profiler_xml.set_object(isr)

    pointer_warning(orti)
    return profiler_xml


def get_task_objects(orti: Orti, postfix: str = "") -> List[ProfilerObject]:
    """Transform ORTI Task objects into Profiler XML Task objects.

    Args:
        orti (Orti): ORTI object.

    Returns:
        List[ProfilerObject]: Task objects to be added to Profiler XML.
    """
    default_task = orti.get_default_task()
    tasks = orti.get_attribute_defs_runningtask()
    return [
        ProfilerObject(
            name=t["attribute_name"] + postfix,
            definition=t["attribute_name"] + postfix,
            description=f"{t['soc_name']}: Tasks" + postfix,
            type="OS:RUNNINGTASK",
            default_value=default_task,
            expression=t["formula"],
            level="Task",
            core=str(t["soc_core"]),
        )
        for t in tasks
    ]


def get_isr2_objects(orti: Orti, postfix: str = "") -> List[ProfilerObject]:
    """Transform ORTI ISR2 objects into Profiler XML ISR2 objects.

    Args:
        orti (Orti): ORTI object

    Returns:
        List[ProfilerObject]: ISR2 objects to be added to Profiler XML
    """

    def get_type_str(isr_attr_def):
        """This is a workaround for NeuSAR which does not have a RUNNINGISR2 attribute."""
        if "RUNNINGISR2" in isr_attr_def["attribute_name"]:
            return "OS:RUNNINGISR2"
        else:
            return "OS:RUNNINGISR"

    default_isr = orti.get_default_isr2()
    isrs2 = orti.get_attribute_defs_runningisr2()
    return [
        ProfilerObject(
            name=i["attribute_name"] + postfix,
            definition=i["attribute_name"] + postfix,
            description=f"{i['soc_name']}: ISRs2" + postfix,
            type=get_type_str(i),
            default_value=default_isr,
            expression=i["formula"],
            level="IRQ0",  # lowest IRQ level in Profiler XML
            core=str(i["soc_core"]),
        )
        for i in isrs2
    ]


def pointer_warning(orti: Orti) -> bool:
    """This function searches the running task/ISR variables for pointers
    and prints a warning if pointers a found.

    The heuristic for doing this is simply search all strings for either
    '*' or '->'.

    Returns:
        bool: True if pointer has been found and False otherwise.
    """

    def check_formula(formula, variables_with_pointer):
        if "*" in formula or "->" in formula:
            variables_with_pointer.append(formula)

    variables_with_pointer: List[str] = []

    for task in orti.get_attribute_defs_runningtask():
        check_formula(task["formula"], variables_with_pointer)

    for isr in orti.get_attribute_defs_runningisr2():
        check_formula(isr["formula"], variables_with_pointer)

    if variables_with_pointer:
        logging.warning("Pointers found in variables:")
        for var in variables_with_pointer:
            logging.warning(f"  {var}")
        m = "Pointers can cause problems because they can only be resolved with connected target."
        logging.warning(m)
        m = "Use the running_taskisr.search_replace_list attribute to replace pointers with static symbols."
        logging.warning(m)
        return True
    return False
