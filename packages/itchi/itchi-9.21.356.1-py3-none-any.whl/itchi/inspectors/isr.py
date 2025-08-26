from .objects import Inspector


def get_isr_inspector(parent_name: str, core_index: str) -> Inspector:
    i = Inspector.get_empty()
    inspector_name = f"ISRs_Core_{core_index}"
    i["Name"] = inspector_name
    i["IsVisible"] = False
    i["Parents"] = [{"Parent": parent_name}]
    i["DefaultState"] = "Default"
    i["Variable"] = []
    i["Macro"] = []
    i["State"] = [
        {
            "StateName": "Default",
            "IsVisible": False,
            "States":
            [
                {
                    "NextStateName": "TERMINATED",
                    "StateFormula": "X",
                    "Suspend": False
                },
                {
                    "NextStateName": "RUNNING",
                    "StateFormula": "E",
                    "Suspend": False
                }
            ]
        },
        {
            "StateName": "TERMINATED",
            "IsVisible": True,
            "States":
            [
                {
                    "NextStateName": "RUNNING",
                    "StateFormula": "E",
                    "Suspend": False
                }
            ]
        },
        {
            "StateName": "RUNNING",
            "IsVisible": True,
            "States":
            [
                {
                    "NextStateName": "TERMINATED",
                    "StateFormula": "X",
                    "Suspend": False
                },
                {
                    "NextStateName": "PREEMPTED",
                    "StateFormula": "S",
                    "Suspend": True
                }
            ]
        },
        {
            "StateName": "PREEMPTED",
            "IsVisible": False,
            "States":
            [
                {
                    "NextStateName": "RUNNING",
                    "StateFormula": "R",
                    "Suspend": False
                }
            ]
        }
    ]
    i["Event"] = [
        {
            "AreaName": "$(PARENT_PATH)",
            "EventName": "E",
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
        },
        {
            "AreaName": "$(PARENT_PATH)",
            "EventName": "X",
            "Formula": "",
            "ValidateEventName": "",
            "CoreName": "All cores",
            "Validate": False,
            "UseRequirement": False,
            "EventType": "Event",
            "SEventType":
            {
                "EEvent": "Exit",
                "EState": "Active"
            }
        },
        {
            "AreaName": "$(PARENT_PATH)",
            "EventName": "R",
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
        },
        {
            "AreaName": "$(PARENT_PATH)",
            "EventName": "S",
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
        }
    ]
    return i
