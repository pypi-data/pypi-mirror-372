from itchi.config import ItchiConfig, RunnableProgramFlowConfig
from itchi.profilerxml.model import ProfilerXml, ProfilerObject, TypeEnum, Enum
from typing import List
from csv import reader
import logging


def get_runnable_type_enum(runnables: List[str]) -> TypeEnum:
    return TypeEnum(
        name="TypeEnum_RunnableMapping_ProgramFlow",
        enums=[Enum(name, "&" + name) for name in runnables],
    )


def get_runnable_object() -> ProfilerObject:
    return ProfilerObject(
        definition="RunnablesProgramFlowDefinition",
        description="All Cores: Runnables (Program Flow)",
        name="RunnablesProgramFlowName",
        type="TypeEnum_RunnableMapping_ProgramFlow",
        level="Runnable",
        expression="",
        signaling="Exec",
        default_value="0",
    )


def get_runnables_from_csv(runnable_config: RunnableProgramFlowConfig) -> List[str]:
    runnables = []
    set_index = True
    index = 0
    with open(runnable_config.csv_file, newline="", mode="r") as csvfile:
        csv_reader = reader(csvfile)
        for idx, row in enumerate(csv_reader):
            # export via Column Name
            if runnable_config.csv_column_name:
                if set_index == False:
                    if row[index]:
                        runnables.append(row[index])
                else:
                    index = row.index(runnable_config.csv_column_name)
                    set_index = False
            # export via Column Index
            else:
                temp = row[int(runnable_config.csv_column_id)]
                if temp:
                    runnables.append(temp)
    return runnables


def runnable_program_flow(profiler_xml: ProfilerXml, config: ItchiConfig):
    runnables = []

    if config.runnable_program_flow is None:
        return
    if config.runnable_program_flow.csv_file.name:
        logging.info(f"Load '{config.runnable_program_flow.csv_file.name}'.")
        runnables = get_runnables_from_csv(config.runnable_program_flow)
    runnables.extend(config.runnable_program_flow.runnables)
    logging.info(f"Added {len(runnables)} runnables to program flow configuration.")
    runnableTypeEnum = get_runnable_type_enum(runnables)
    profiler_xml.set_type_enum(runnableTypeEnum)
    profiler_xml.set_object(get_runnable_object())
