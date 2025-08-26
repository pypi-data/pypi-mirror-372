import json
from copy import deepcopy


class InspectorJsonFile(dict):
    schema = {
        "type": "object",
        "properties": {
            "Repository": {
                "type": "object",
                "properties": {
                    "Version": {
                        "type": "string"
                    },
                    "Inspectors": {
                        "type": "array"
                    },
                },
                "required": [
                    "Version",
                    "Inspectors",
                ]
            }
        },
        "required": [
            "Repository"
        ]
    }

    empty = {
        "Repository":
        {
            "Version": "2.2",
            "Groups": [],
            "Inspectors": [],
            "Macros": [],
            "Templates": {
                "Parameters": [],
                "URLs": []
            },
        }}

    @classmethod
    def from_json_file(cls, file_name):
        with open(file_name, 'r') as f:
            d = json.load(f)
        return cls(d)

    @classmethod
    def get_empty(cls):
        return cls(deepcopy(cls.empty))

    def __init__(self, object_dict):
        self.update(object_dict)
        self.validate()

    def save_to_file(self, file_name):
        version = self["Repository"]["Version"]
        if version != "2.2":
            m = "Inspector version {} not supported!".format(version)
            raise Exception(m)
        with open(file_name, 'w') as f:
            json.dump(self, f, indent=2)

    def validate(self):
        pass

    def get_inspectors(self):
        inspectors = list(map(Inspector, self["Repository"]["Inspectors"]))
        return inspectors

    def append_inspector(self, inspector):
        i = Inspector(inspector)
        self["Repository"]["Inspectors"].append(i)
        return self


class Inspector(dict):
    schema = {
        "type": "object",
        "properties": {
            "Enabled": {"type": "boolean"},
            "IsVisible": {"type": "boolean"},
            "DefaultState": {"type": "string"},
            "Name": {"type": "string"},
            "Parents": {"type": "array"},
            "State": {"type": "array"},
            "TimeConstraint": {"type": "array"},
            "Event": {"type": "array"},
            "Variable": {"type": "array"},
        },
        "required": [
            "Enabled",
            "IsVisible",
            "DefaultState",
            "Name",
            "Parents",
            "State",
            "TimeConstraint",
            "Event",
            "Variable"
        ],
        "additionalProperties": False,
    }

    empty = {
        "Enabled": True,
        "IsVisible": True,
        "DefaultState": "",
        "Name": "",
        "Parents": [],
        "State": [],
        "TimeConstraint": [],
        "Event": [],
        "Variable": []
    }

    @classmethod
    def get_empty(cls):
        return cls(cls.empty)

    def __init__(self, object_dict):
        self.update(object_dict)
        self.validate()

    def validate(self):
        pass

    def __str__(self):
        s = "<Inspector '{}'>".format(self.get_name())
        return s

    def get_name(self):
        return self["Name"]

    def get_states(self):
        return self["State"]

    def get_event_by_name(self, name):
        for event in self["Event"]:
            if name == event["EventName"]:
                return event
        raise ValueError("No event with name {}.".format(name))


class InspectorState(dict):

    empty = {
        "StateName": "",
        "IsVisible": True,
        "States": []
    }

    schema = {
        "type": "object",
        "properties": {
            "StateName": {"type": "string"},
            "IsVisible": {"type": "boolean"},
            "States": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "NextStateName": {"type": "string"},
                        "StateFormula": {"type": "string"},
                        "Suspend": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                    "required": [
                        "NextStateName",
                        "StateFormula",
                        "Suspend",
                    ],
                },
            },
        },
        "required": [
            "StateName",
            "IsVisible",
            "States",
        ],
        "additionalProperties": False,
    }

    @classmethod
    def get_empty(cls):
        return cls(cls.empty)

    def __init__(self, object_dict):
        self.update(object_dict)
        self.validate()

    def validate(self):
        pass


class InspectorEvent(dict):
    empty = {
        "AreaName": "",
        "EventName": "",
        "Formula": "",
        "ValidateEventName": "",
        "Validate": False,
        "UseRequirement": False,
        "EventType": "",
        "SEventType":
        {
            "EEvent": "Entry",
            "EState": "Active"
        }}
    schema = {
        "type": "object",
        "properties": {
            "AreaName": {"type": "string"},
            "EventName": {"type": "string"},
            "Formula": {"type": "string"},
            "ValidateEventName": {"type": "string"},
            "Validate": {"type": "boolean"},
            "UseRequirement": {"type": "boolean"},
            "EventType": {"type": "string"},
            "SEventType": {
                "type": "object",
                "properties": {
                    "EEvent": {"type": "string"},
                    "EState": {"type": "string"},
                },
                "additionalProperties": False,
                "required": [
                    "EEvent",
                    "EState",
                ],
            }
        },
        "required": [
            "AreaName",
            "EventName",
            "Formula",
            "ValidateEventName",
            "Validate",
            "UseRequirement",
            "EventType",
            "SEventType",
        ],
        "additionalProperties": False,
    }

    @classmethod
    def get_empty(cls):
        return cls(cls.empty)

    def __init__(self, object_dict):
        self.update(object_dict)
        self.validate()

    def validate(self):
        pass


class InspectorVariable(dict):
    empty = {
        "AreaDisplay": "",
        "VariableType": "",
        "VariableName": "",
        "DefaultValue": 0,
        "DefaultVal": "0",
        "VariableFormula": [],
        "IsVisible": True
    }
    schema = {
        "type": "object",
        "properties": {
            "AreaDisplay": {"type": "string"},
            "VariableType": {"type": "string"},
            "VariableName": {"type": "string"},
            "DefaultValue": {"type": "number"},
            "DefaultVal": {"type": "string"},
            "IsVisible": {"type": "boolean"},
            "VariableFormula": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "EventName": {"type": "string"},
                        "Formula": {"type": "string"},
                    },
                },
            },
        },
        "additionalProperties": False,
    }

    @classmethod
    def get_empty(cls):
        return cls(cls.empty)

    def __init__(self, object_dict):
        self.update(object_dict)
        self.validate()

    def validate(self):
        pass
