import logging
import re
from typing import List, Set
from itchi.config import ItchiConfig
from itchi.profilerxml.model import ProfilerXml, ProfilerObject


def get_signal_objects(signals: List[str]) -> List[ProfilerObject]:
    return [ProfilerObject(
        name=signal_name,
        definition=signal_name,
        description=signal_name,
        expression=signal_name,
        level="None",
    ) for signal_name in signals]


def signals(profiler_xml: ProfilerXml, config: ItchiConfig):
    if not config.signals:
        logging.warning("Executed with signals flag but no signals in config JSON.")
        return

    for signal in get_signal_objects(config.signals.signals):
        profiler_xml.set_object(signal)


def extract_variables(formula: str) -> Set[str]:
    """
    Extracts C variable identifiers from a given formula string. Variables that
    start with the address operator '&' are excluded. This function uses a regex
    approach, which is suitable for most common ORTI use cases, but should not be
    considered as a substitute for a proper C parser.

    Args:
        formula (str): A string containing C identifiers.

    Returns:
        Set[str]: A set of unique variable identifiers found in the input string.

    Example:
        >>> extract_variables("foo.bar &quz")
        {'foo.bar'}

        >>> extract_variables("(Os_ControlledCoreInfo0.ReadyTasks.p0")
        {'Os_ControlledCoreInfo0.ReadyTasks.p0'}
    """
    formula = formula.replace("(", "").replace(")", "")
    pattern = r'\b(?<!&)[A-Za-z_][A-Za-z0-9_\.\[\]]*'
    matches = re.findall(pattern, formula)
    return set(matches)


def get_all_variables(profiler_xml: ProfilerXml) -> List[str]:
    """
    Retrieves a list of all symbols for which hardware tracing has to be
    configured from the provided ProfilerXml object. It iterates through all
    objects and types in the ProfilerXml, adding relevant expressions and
    signaling to a set of variables. Expressions are extracted from enums and
    added to the set as well.

    Args:
        profiler_xml (ProfilerXml): A ProfilerXml object containing objects and types for profiling.

    Returns:
        List[str]: A sorted list of unique variable identifiers found in the ProfilerXml object.

    Example:
        >>> get_all_variables(profiler_xml)
        ['Program_Flow_Trace', 'variable1', 'variable2', ...]
    """
    vars: Set[str] = set()
    for object in profiler_xml.objects:
        if object.expression and object.expression == "$(EnumType)":
            pass  # variables are part of enum.value_property
        elif object.expression:
            vars.add(object.expression)
        elif object.signaling and object.signaling == "Exec":
            vars.add("Program_Flow_Trace")
        elif object.signaling:
            vars.add(object.signaling)
    for enum_type in profiler_xml.types:
        for enum in enum_type.enums:
            if enum.context_state_formula:
                vars.update(extract_variables(enum.context_state_formula))
            elif enum.value_property:
                vars.update(extract_variables(enum.value_property))
    return sorted(list(vars))


def log_trace_symbols(profiler_xml: ProfilerXml):
    vars = get_all_variables(profiler_xml)
    logging.info("Symbols to trace:")
    for signal in vars:
        logging.info(f"  {signal}")
