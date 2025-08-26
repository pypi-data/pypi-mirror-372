import copy
from typing import List
from itchi.ortilib.orti import Orti
from itchi.ortilib.formula import Formula
from itchi.config import TaskStateInspectorsConfig
from .formula_resolver import FormulaResolver
from .state_resolver import StateResolver
from .isr import get_isr_inspector
from .objects import InspectorJsonFile, Inspector


class TaskStateInspectors(object):
    """
    Create winIDEA Inspectors to analyze task STATES
    for the provided ORTI file. Files are saved into
    inspectors_file when save method is called.
    """

    def __init__(self, orti: Orti, config: TaskStateInspectorsConfig):
        self.orti = orti
        self.inspectorsFile = config.inspectors_file
        self.constantVariables = config.constant_variables
        self.defaultState = config.default_state
        self.defaultStateValue = self._defaultStateValue(self.defaultState)
        self.parentAreaTemplate = config.parent_area_template
        self.inspectorJson = InspectorJsonFile.get_empty()
        self.taskCoreToCoreName = config.task_core_to_core_name

        # List of area names referenced by the events. This can be used
        # to add the respective areas to the Profiler data section.
        self.dataAreaVarNames: List[str] = []

        for task in self.orti.get_object_defs_task():
            formula = [
                attr["formula"] for attr in task["attributes"] if attr["attribute_name"] == "STATE"
            ][0]
            formula = Formula(formula)
            i = self.ortiTaskToInspector(task, formula)
            self.inspectorJson.append_inspector(i)
            if config.create_preemption_aware_running_state:
                i_copy = self._copyPatchInspectorToRespectPreemptions(i)
                self.inspectorJson.append_inspector(i_copy)

    def _copyPatchInspectorToRespectPreemptions(self, inspector):
        """This is a hack that copies and Inspector and makes it so that it has a single
        visiable state RUNNING_WITH_PREEMPTIONS that respects preemptions by setting the suspend
        flag to true for transitions to states that to not cause a preemption. We have to make
        a copy, because otherwise we screw up the BTF and MDF4 exports."""
        PREEMPTING_STATES = [
            "READY",
            "READY_ASYNC",
            "READY_ISR",
            "READY_SYNC",
            "READY_TASK",
            "READ_ASYNC",
            "DELAYED",
        ]
        inspector = copy.deepcopy(inspector)
        inspector["Name"] += "_PreemptPatchInspector"
        for state in inspector["State"]:
            if state["StateName"] == "RUNNING":
                state["StateName"] = "RUNNING_"
                for transition in state["States"]:
                    if transition["NextStateName"] in PREEMPTING_STATES:
                        transition["Suspend"] = True
            else:
                state["IsVisible"] = False
            for transition in state["States"]:
                if transition["NextStateName"] == "RUNNING":
                    transition["NextStateName"] = "RUNNING_"
        return inspector

    def _defaultStateValue(self, defaultState: str) -> int:
        enumElems = self.orti.get_enum_elements_task_state()
        for e in enumElems:
            if e.desc == defaultState and isinstance(e.const, int):
                return e.const
        return 0

    def save(self):
        self.inspectorJson.save_to_file(self.inspectorsFile)
        return self

    def getParentAreaName(self, task):
        taskName = task["object_name"]
        task_core = task["task_core_index"]
        default_core_name = f"Core {task_core}"
        core_name = self.taskCoreToCoreName.get(task_core, default_core_name)
        return self.parentAreaTemplate.format(
            core_id=task_core, core_name=core_name, task_name=taskName
        )

    def extractDataAreaVarNames(self, events):
        varNames = [
            event["AreaName"].replace("Data/", "")
            for event in events
            if event["AreaName"].startswith("Data/")
        ]
        for name in varNames:
            self.dataAreaVarNames.append(name)

    def ortiTaskToInspector(self, task, formula):
        runningTaskVars = [a["formula"] for a in self.orti.get_attribute_defs_runningtask()]
        taskStateVar = "VarState"
        taskStateDecl = self.orti.get_attribute_decl("TASK", "STATE")

        inspectorName = f"Inspector_{task['object_name']}"
        formula_resolver = FormulaResolver(
            inspectorName,
            formula,
            runningTaskVars,
            taskStateVar,
            self.defaultStateValue,
            self.constantVariables,
        )
        inspectorVars = formula_resolver.getVariables()
        inspectorEvents = formula_resolver.getEvents()
        inspectorStates = StateResolver(taskStateDecl, taskStateVar).getStates()
        parentAreaName = self.getParentAreaName(task)

        i = Inspector.get_empty()
        i["Name"] = inspectorName
        i["IsVisible"] = False
        i["Parents"] = [{"Parent": parentAreaName}]
        i["DefaultState"] = self.defaultState
        i["Variable"] = inspectorVars
        i["Macro"] = []
        i["Event"] = inspectorEvents
        i["State"] = inspectorStates
        i.validate()

        self.extractDataAreaVarNames(inspectorEvents)
        return i

    def addIsrInspectors(self):
        isr_defs = self.orti.get_attribute_defs_runningisr2()
        for isr_def in isr_defs:
            soc_core = isr_def["soc_core"]
            soc_name = isr_def["soc_name"]
            parent_area = f"Data/{soc_name}: ISRs2[]"
            i = get_isr_inspector(parent_area, soc_core)
            self.inspectorJson.append_inspector(i)
