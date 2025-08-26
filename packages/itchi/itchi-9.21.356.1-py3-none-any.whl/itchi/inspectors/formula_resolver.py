import logging
from .objects import InspectorEvent, InspectorVariable


class FormulaResolver(object):

    def __init__(self, inspectorName, formula, runningTaskVars,
                 taskStateVar, defaultStateValue, constantVariables=None):
        # Some variables that we need to resolve the expressions.
        if constantVariables is not None:
            self.constantVariables = constantVariables
        else:
            self.constantVariables = {}
        self.supportOperators = ['&&', '||', '<=', '>=', '!=',
                                 '==', '>', '<', '+', '-', '*', '<<', '>>', '&']
        self.invalidExpressionMessage = "Unsupported expression: '{}'"
        self.taskStateVar = taskStateVar
        self.inspectorName = inspectorName
        self.defaultStateValue = defaultStateValue

        # Some expressions contain references to the running task variables.
        # We do not resolve those, but use the parent element instead (which
        # is essentially the running task variable).
        self.runningTaskVariables = runningTaskVars
        self.runningTaskInFormula = False
        self.runningTaskActiveVar = "VarParentActive"
        self.runningTaskInactiveVar = "VarParentInactive"
        self.runningTaskActiveVal = "$(VarParentActive:=VALUE)"
        self.runningTaskInactiveVal = "$(VarParentInactive:=VALUE)"
        self.parentActiveEvent = "StateParentActive"
        self.parentInactiveEvent = "StateParentInactive"
        self.parentResumeEvent = "StateParentResume"
        self.parentPreemptEvent = "StateParentPreempt"

        # Variables that will be used to create the Profiler Inspector.
        self.inspectorEvents = []
        self.inspectorVariables = []
        self.stateFormula = self.resolve(formula.formula)
        if self.runningTaskInFormula:
            self.createRunningTaskEventsAndVariables()
        self.createStateVariable()
        self.createTaskPreemptResumeForIsrs()

    def createTaskPreemptResumeForIsrs(self):
        parentResumeEvent = InspectorEvent({
            "AreaName": "$(PARENT_PATH)",
            "EventName": self.parentResumeEvent,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Event",
            "SEventType":
            {
                "EEvent": "Resume",
                "EState": "Active"
            }
        })
        self.inspectorEvents.append(parentResumeEvent)

        parentPreemptEvent = InspectorEvent({
            "AreaName": "$(PARENT_PATH)",
            "EventName": self.parentPreemptEvent,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Event",
            "SEventType":
            {
                "EEvent": "Suspend",
                "EState": "Active"
            }
        })
        self.inspectorEvents.append(parentPreemptEvent)

        varStateEvent = InspectorEvent({
            "AreaName": "$(PARENT_PATH)/{}/VarState".format(self.inspectorName),
            "EventName": "VarState",
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Data",
            "SEventType":
            {
                "EEvent": "Entry",
                "EState": "Active"
            }
        })
        self.inspectorEvents.append(varStateEvent)

        areaName = "$(PARENT_PATH)/{}/{}".format(self.inspectorName, self.runningTaskActiveVar)
        varParentActive = InspectorEvent({
            "AreaName": areaName,
            "EventName": self.runningTaskActiveVar,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Data",
            "SEventType":
            {
                "EEvent": "Entry",
                "EState": "Active"
            }
        })
        self.inspectorEvents.append(varParentActive)

        areaName = "$(PARENT_PATH)/{}/{}".format(self.inspectorName, self.runningTaskInactiveVar)
        varParentInactive = InspectorEvent({
            "AreaName": areaName,
            "EventName": self.runningTaskInactiveVar,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Data",
            "SEventType":
            {
                "EEvent": "Entry",
                "EState": "Active"
            }
        })
        self.inspectorEvents.append(varParentInactive)

    def getVariables(self):
        return self.inspectorVariables

    def getEvents(self):
        return self.inspectorEvents

    def createStateVariable(self):
        """
        Must be called after all other events and variables have
        been added.
        """
        var = ({
            "AreaDisplay": "Decimal",
            "VariableType": "Unsigned",
            "RangeLo": "",
            "RangeHi": "",
            "Unit": "",
            "Fill": False,
            "VariableName": self.taskStateVar,
            "DefaultValue": 0xfefe,
            "DefaultVal": str(self.defaultStateValue),
            "VariableFormula":
                [{"EventName": e["EventName"],
                  "Formula": self.stateFormula}
                 for e in self.inspectorEvents],
            "IsVisible": False,
        })
        self.inspectorVariables.append(var)

    def createRunningTaskEventsAndVariables(self):
        varRunningTaskActive = InspectorVariable({
            "AreaDisplay": "Decimal",
            "VariableType": "Unsigned",
            "RangeLo": "",
            "RangeHi": "",
            "Unit": "",
            "Fill": False,
            "VariableName": self.runningTaskActiveVar,
            "DefaultValue": 0,
            "DefaultVal": "0",
            "VariableFormula": [
                {"EventName": self.parentActiveEvent,
                 "Formula": "1"},
                {"EventName": self.parentInactiveEvent,
                 "Formula": "0"},
            ],
            "IsVisible": False,
        })
        varRunningTaskInactive = InspectorVariable({
            "AreaDisplay": "Decimal",
            "VariableType": "Unsigned",
            "RangeLo": "",
            "RangeHi": "",
            "Unit": "",
            "Fill": False,
            "VariableName": self.runningTaskInactiveVar,
            "DefaultValue": 1,
            "DefaultVal": "1",
            "VariableFormula": [
                {"EventName": self.parentActiveEvent,
                 "Formula": "0"},
                {"EventName": self.parentInactiveEvent,
                 "Formula": "1"},
            ],
            "IsVisible": False,
        })

        self.inspectorVariables.append(varRunningTaskActive)
        self.inspectorVariables.append(varRunningTaskInactive)

        parentActiveEvent = InspectorEvent({
            "AreaName": "$(PARENT_PATH)",
            "EventName": self.parentActiveEvent,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Event",
            "SEventType":
            {
                "EEvent": "Entry",
                "EState": "Active"
            }
        })

        parentInactiveEvent = InspectorEvent({
            "AreaName": "$(PARENT_PATH)",
            "EventName": self.parentInactiveEvent,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Event",
            "SEventType":
            {
                "EEvent": "Exit",
                "EState": "Inactive"
            }
        })

        self.inspectorEvents.append(parentActiveEvent)
        self.inspectorEvents.append(parentInactiveEvent)

    def resolveTernary(self, expression):
        exp = expression

        def inverseExpression(exp):
            inverseTable = {
                "==": "!=",
                "!=": "==",
                ">=": "<",
                "<=": ">",
                "<": ">=",
                ">": "<=",
            }
            try:
                exp['type'] = inverseTable[exp['type']]
                return exp
            except KeyError:
                logging.error("Cannot reverse expression.")
                raise Exception(self.invalidExpressionMessage.format(exp))

        cond = exp['condition']
        condInv = inverseExpression(dict(cond))
        expressionTrue = exp['expression_true']
        expressionFalse = exp['expression_false']

        exp = {
            "type": "+",
            "expression_1":
                {
                    "type": "*",
                    "expression_1": cond,
                    "expression_2": expressionTrue,
                },
            "expression_2":
                {
                    "type": "*",
                    "expression_1": condInv,
                    "expression_2": expressionFalse,
                }
        }
        return self.resolveOperation(exp)

    def resolveOperation(self, expression):
        exp = expression
        operator = exp['type']
        exp1 = self.resolve(exp['expression_1'])
        exp2 = self.resolve(exp['expression_2'])

        # Check some conditions that allow result in a more trivial result.
        if exp1 == "1" and operator == "*":
            return exp2
        if exp2 == "1" and operator == "*":
            return exp1
        if exp1 == "0" and operator == "+":
            return exp2
        if exp2 == "0" and operator == "+":
            return exp1
        if (exp1 == "0" or exp2 == "0") and operator == "*":
            return "0"

        try:
            # See if we can evaluate the expression.
            r = "{} {} {}"
            r = r.format(int(exp1), operator, int(exp2))
            # pylint: disable = eval-used
            r = str(int(eval(r)))
        except Exception:
            r = "({} {} {})"
            r = r.format(exp1, operator, exp2)
        return r

    def resolveRunningTask(self, expression):
        self.runningTaskInFormula = True
        if expression['type'] == "==":
            return self.runningTaskActiveVal
        if expression['type'] == "!=":
            return self.runningTaskInactiveVal
        logging.error("Cannot resolve running task for this expression.")
        raise Exception(self.invalidExpressionMessage.format(expression))

    def resolveVariable(self, expression):
        try:
            return str(self.constantVariables[expression])
        except KeyError:
            pass
        name = expression
        for char in ["(", ")", ".", "->", "*", "[", "]"]:
            name = name.replace(char, "_")
        area = "Data/{}".format(expression)
        value = "$({}:=VALUE)".format(name)
        event = InspectorEvent({
            "AreaName": area,
            "EventName": name,
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Data",
            "SEventType":
            {
                "EEvent": "Entry",
                "EState": "Active"
            }
        })
        self.inspectorEvents.append(event)
        return value

    def resolve(self, expression):
        def isRunningTaskCompare(expression):
            if expression['expression_1'] in self.runningTaskVariables:
                return True
            if expression['expression_2'] in self.runningTaskVariables:
                return True
            return False

        if isinstance(expression, str):
            return self.resolveVariable(expression)
        if isinstance(expression, int):
            return str(expression)
        if isinstance(expression, dict):
            if expression['type'] == 'ternary':
                return self.resolveTernary(expression)
            if isRunningTaskCompare(expression):
                return self.resolveRunningTask(expression)
            if expression['type'] in self.supportOperators:
                return self.resolveOperation(expression)
            raise Exception(self.invalidExpressionMessage.format(expression))
        raise Exception(self.invalidExpressionMessage.format(expression))
