from .objects import InspectorState


class StateResolver():
    def __init__(self, taskStateDecl, taskStateVar):
        self.taskStateDecl = taskStateDecl
        self.taskStateVar = taskStateVar
        self.inspectorStates = self._createInspectorStates()

    def getStates(self):
        return self.inspectorStates

    def _createInspectorStates(self):
        stateValueTuples = self._getStateValueTuples()
        stateNames = []
        states = []
        # We want each state only once.
        for stateValueTuple in stateValueTuples:
            state = self._createState(stateValueTuple, stateValueTuples)
            stateName = state["StateName"]
            if stateName not in stateNames:
                stateNames.append(stateName)
                states.append(state)

        # Additional state for when task is preempted by ISR. When the task
        # resume we go back to RUNNING. When the parent task exits this means
        # the ISR has caused a scheduling event and the task goes to READY.
        isrReadyState = {
            "StateName": "READY_ISR",
            "IsVisible": True,
            "States": [{"NextStateName": "RUNNING",
                        "StateFormula": "StateParentResume",
                        "Suspend": False},
                       {"NextStateName": "READY",
                        "StateFormula": "StateParentInactive",
                        "Suspend": False}]}
        states.append(isrReadyState)

        return states

    def _createState(self, stateValueTuple, stateValueTuples):
        stateName = stateValueTuple[0]
        state = {
            "StateName": stateName,
            "IsVisible": True,
            "States": []}
        for svt in stateValueTuples:
            if svt[0] == stateName:
                # No transition to itself or other states with the same name.
                pass
            else:
                stateFormula = "$({}:=VALUE) == {}".format(self.taskStateVar, svt[1])
                nextStateDict = {
                    "NextStateName": svt[0],
                    "StateFormula": stateFormula,
                    "Suspend": False}
                state["States"].append(nextStateDict)

        # Additional transition to preempt task when ISR is running.
        if stateName == "RUNNING":
            nextStateDict = {
                "NextStateName": "READY_ISR",
                "StateFormula": "StateParentPreempt",
                "Suspend": False}
            state["States"].append(nextStateDict)

        state = InspectorState(state)
        return state

    def _getStateValueTuples(self):
        enumElems = self.taskStateDecl['attribute_type']['enum_elements']
        return [(e.desc, e.const) for e in enumElems]
