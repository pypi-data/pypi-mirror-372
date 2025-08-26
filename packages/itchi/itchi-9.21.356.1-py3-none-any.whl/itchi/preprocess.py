import argparse
import json
import logging
import pydantic
import re
import itchi.config
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
from itchi.config import ItchiConfig, CommandConfig
from itchi.ortilib.orti import Orti
from itchi.profilerxml.model import ProfilerXml


def update_orti(config: ItchiConfig, orti_object: Orti):
    """Manipulate Orti object based on config."""
    if config.running_taskisr is not None:
        default_task = config.running_taskisr.default_task
        if default_task:
            orti_object.set_default_task(default_task)
            msg = f"Set {default_task=}."
            logging.info(msg)

        default_isr2 = config.running_taskisr.default_isr2
        if default_isr2:
            orti_object.set_default_isr2(default_isr2)
            msg = f"Set {default_isr2=}."
            logging.info(msg)

        search_and_replace = config.running_taskisr.search_replace_list
        if search_and_replace:
            orti_object.search_and_replace_running_taskisr(search_and_replace.items())
            msg = f"Apply {search_and_replace=}."
            logging.info(msg)

        orti_core_to_soc_core = config.running_taskisr.orti_core_to_soc_core
        if orti_core_to_soc_core:
            orti_object.orti_core_to_soc_core = orti_core_to_soc_core
            logging.info("Remapping ORTI cores to SoC cores.")
            logging.info("  orti_core -> soc_core")
            for orti_core, soc_core in orti_core_to_soc_core.items():
                logging.info(f"  {orti_core:>9} -> {soc_core}")

        orti_core_to_core_name = config.running_taskisr.orti_core_to_core_name
        if orti_core_to_core_name:
            orti_object.orti_core_to_soc_name = orti_core_to_core_name
            logging.info("Remapping ORTI cores to SoC core names.")
            logging.info("  orti_core -> soc_name")
            for orti_core, soc_name in orti_core_to_core_name.items():
                logging.info(f"  {orti_core:>9} -> {soc_name}")

    if config.task_state is not None:
        os_config_h = config.task_state.autocore_os_config_h
        task_to_core_mapping = config.task_state.task_to_core_mapping
        if os_config_h.is_file():
            update_orti_task_defs_from_os_config_h(os_config_h, orti_object)
            logging.info(f"Updated Task cores from '{os_config_h}'.")
        elif task_to_core_mapping:
            logging.info("Updated Task cores based on task_to_core_mapping.")
            update_orti_task_defs_from_task_mapping(task_to_core_mapping, orti_object)
        elif config.task_state.task_to_core_heuristic:
            logging.info("Updated Task cores based on heuristics.")
            update_orti_task_defs_with_heuristic(orti_object)

    # Replace spaces in STATES with underscores because Inspector states do not allow spaces.
    orti_object.replace_spaces_in_states()

    return orti_object


def update_namespace(args: argparse.Namespace, commands: Optional[CommandConfig]):
    """
    Updates the command line arguments with commands provided in the
    configuration. Only overrides inactive commands. That means you can enable
    a command via the config file, but not disable one.

    Args:
        args (argparse.Namespace): Argparse Namespace object
        commands (core.config.CommandConfig): iTCHi command config object
    """
    if commands is None:
        return
    for command, value in commands:
        if value is True:
            setattr(args, command, value)


def load_config(config_file: Path) -> Optional[ItchiConfig]:
    """Load iTCHi config from file. Return None on error.

    Args:
        config_file (Path): Config file path

    Returns:
        Optional[core.config.ItchiConfig]: ItchiConfig or None
    """
    try:
        config = itchi.config.load_config(config_file)
    except FileNotFoundError:
        msg = f"Config file {config_file} not found."
        logging.error(msg)
        return None
    except pydantic.ValidationError as err:
        logging.error(f"Failed to load {config_file}.")
        for line in str(err).split("\n"):
            logging.error(line)
        return None
    except json.decoder.JSONDecodeError as err:
        logging.error(f"JSON error while loading {config_file}.")
        for line in str(err).split("\n"):
            logging.error(line)
        return None
    logging.info(f"Load '{config_file}'.")
    return config


def set_meta_tags(orti_object: Orti, profiler_xml: ProfilerXml):
    """Set the Name, NumCores, and ORTI attributes of the Profiler
    XML file based on the contents of the ORTI file.

    Args:
        orti (Orti): ORTI file object
        profiler_xml (ProfilerXml): Profiler XML object for which to set the attributes
    """
    profiler_xml.name = orti_object.get_os_name()
    profiler_xml.num_cores = orti_object.get_number_of_cores()
    profiler_xml.orti = str(orti_object.orti_file)


def update_orti_task_defs_with_heuristic(orti: Orti):
    """
    Update ORTI task definitions task_core_index attribute based
    on core index extracted from Task STATE formula.

    Args:
        orti (Orti): [description]
    """
    # Regex to extract core ID.
    re_naive = re.compile(r"[Cc]ore_?(\d+)")
    re_etas_rtaos = re.compile(r"Os_ControlledCoreInfo(\d+)")
    heuristic_regexes = [re_naive, re_etas_rtaos]

    task_defs = orti.get_object_defs_task()
    for task_def in task_defs:
        task_name = task_def["object_name"]
        try:
            (state_formula,) = [attr["formula"] for attr in task_def["attributes"] if attr["attribute_name"] == "STATE"]
        except ValueError:
            msg = f"Task '{task_name}' does not have a STATE attribute. Falling back to name."
            logging.warning(msg)
            state_formula = task_name

        # For each regex see if it matches the state formula. If yes use that
        # index, otherwise, default to '0'.
        for r in heuristic_regexes:
            match = r.findall(state_formula)
            if match:
                core_id = int(match[0])
                msg = f"Heuristic detected '{core_id}' for '{task_name}'."
                logging.debug(msg)
                break
        else:
            core_id = 0
            msg = f"Heuristic failed for '{task_name}'. Falling back to '{core_id}'."
            logging.warning(msg)
        task_def["task_core_index"] = core_id


def update_orti_task_defs_from_os_config_h(os_config_h_file: Path, orti: Orti):
    """
    This procedure extracts task name, expression and core number from the
    AutoCore Os_config.h file and updates the ORTI file with the information.
    This is necessary for multi-core applications where winIDEA has to be
    aware of the core IDs. Also the STATE definitions in the ORTI file contain
    pointers while the information from this file can be used to get the state
    from a symbol without pointer.

    The information we are interested in is structure like this:

    ~~~C
    OS_TASKCONFIG_INIT(    /* T_STARTSTOP_SLAVE_CORE_2 */
      &OS_taskDynamic_core2[0],        /* Dynamic task structure */
      // other stuff
    ),
    ~~~

    We first find the lines that contain OS_TASKCONFIG_INIT and extract the
    task name via a regular expression (r_name). After the task_name we search
    for the expression (OS_taskDynamic) variable that can be used to record
    the state of the task. We have to append ".state" to that expression.
    Finally, we use another regex to extract the core number.  It searches for
    a sequence of one or more numbers (\\d) after the "core" string. The
    task_name together with the expression and core_number are appended to the
    tasks list.

    Args:
        os_config_h_file (str): Elektrobit AutoCore Os_config.h file path
        orti (Orti): ORTI object
    """
    if not os_config_h_file.is_file():
        return

    @dataclass
    class Task:
        task_name: str
        expression: str
        core_id: str

    # Extract information from Os_config.h
    tasks = {}
    r_name = r"/\* (\S+) \*/"
    r_task_structure = re.compile(r"&(OS_taskDynamic_core(\d+)\[\d+\])")
    with open(os_config_h_file) as f:
        task_name = ""
        for line in f:
            if "OS_TASKCONFIG_INIT" in line:
                task_name = re.findall(r_name, line)[0]
            elif m := r_task_structure.findall(line):
                assert len(m) == 1, "There should be only one task struct per line!"
                task_struct, core_id = m[0]
                expr = task_struct + ".state"
                tasks[task_name] = Task(task_name, expr, core_id)

    # Update Orti object
    unmatched_task_names = []
    for task_def in orti.get_object_defs_task():
        task_name = task_def["object_name"]
        if task_name in tasks:
            task_info = tasks[task_name]
            task_def["task_core_index"] = int(task_info.core_id)
            for attr in task_def["attributes"]:
                if attr["attribute_name"] == "STATE":
                    attr["formula"] = task_info.expression
        else:
            unmatched_task_names.append(task_name)

    if unmatched_task_names:
        first = unmatched_task_names[0]
        count = len(unmatched_task_names)
        msg = f"Object '{first}' and {count - 1} others not in '{os_config_h_file}'."
        logging.critical(msg)
        msg = f"Make sure that '{os_config_h_file}' and ORTI file are in sync to avoid this issue."
        logging.critical(msg)
        sys.exit(1)


def update_orti_task_defs_from_task_mapping(task_to_core_mapping: Dict[str, int], orti: Orti):
    """
    Adds a task_core_index attribute to each task in the ORTI file.
    If the tasks is specified in task_to_core_mapping the respective
    core index is used. Otherwise, the function defaults to '0'.

    Args:
        task_to_core_mapping (Dict[str, int]): explicit core mapping from iTCHi config
        orti (Orti): ORTI object
    """
    if not task_to_core_mapping:
        return orti

    mapping = task_to_core_mapping

    for task_def in orti.get_object_defs_task():
        task_name = task_def["object_name"]
        try:
            core_id = mapping[task_name]
        except KeyError:
            core_id = 0
            m = "No task to core mapping for '{}'. Default to '{}'"
            m = m.format(task_name, str(core_id))
            logging.warning(m)
        task_def["task_core_index"] = int(core_id)
