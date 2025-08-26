##
# @brief A middle layer between iTCHi models (configuration) and GUI
#
import ast
import datetime
import enum
import io
import os
import pathlib
import sys
import typing
from .models import ItchiConfig, ItchiHelp
from dataclasses import dataclass
from collections import defaultdict
from typing import Tuple, Dict, List, Optional
from itchi import itchi_cli
from itchi.config_attrs_doc import CONFIG_ATTRS_DOC


@enum.unique
class EConfigSectionAttributeType(enum.IntEnum):
    ##
    # @brief Enumerator for attribute types that GUI uses when showing their values
    #
    # Enumerator         | Description                                                             |
    # -------------------|-------------------------------------------------------------------------|
    # Basic              | Basic type (str, int, ...); In GUI it will be shown as a simple string  |
    # Boolean            | Boolean type (True, False); In GUI it will be shown as a checkbox       |
    # Enum               | Enum type; In GUI it will be shown as a drop-down
    # Path               | String with an additional file picker button that opens file explorer   |
    # IterableOneColumn  | Attribute will have a drop-down item with one column editable           |
    # IterableTwoColumns | Attribute will have a drop-down item with two columns editable          |
    #
    Basic = enum.auto()
    Boolean = enum.auto()
    Enum = enum.auto()
    Path = enum.auto()
    IterableOneColumn = enum.auto()
    IterableTwoColumns = enum.auto()


@dataclass
class ConfigSectionAttribute:
    ##
    # @brief Class that acts as middlelayer between iTCHi config attribute and property editor.
    #
    name: str
    type: EConfigSectionAttributeType
    value: typing.Any


class CmdInfo:
    ##
    # @brief Holds information about specific command for GUI
    #
    def __init__(self, group: str, htmlElementId: str = ""):
        ##
        # @brief Class constructor
        # @param group         Name of the group under which the command will be sorted
        # @param cmdBlockList  A list of other commands that this command blocks when selected
        # @param htmlElementID Element id associated with the command
        #                        - used for searching help .hmtl
        #                        - used in conjuction with htmlElementID
        self.group = group
        self.htmlElementId = htmlElementId
        self._blockedCountingSemaphore = 0


class Controller:
    log_file: str = "itchi.log"
    cmds = {
        "running_taskisr": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "runningtaskisr",
        ),
        "running_taskisr_btf": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "runningtaskisrtracingwithbtfexport",
        ),
        "running_taskisr_sampling": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "runningtaskisrsampling",
        ),
        "task_state_single_variable": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "taskstatetracingwithsinglestatevariables",
        ),
        "task_state_complex_native": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "taskstatetracingwithcomplexstatenative",
        ),
        "task_state_instrumentation_microsar": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "taskstatetracingwithinstrumentation",
        ),
        "task_state_instrumentation_autocore": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "taskstatetracingwithinstrumentation",
        ),
        "task_state_swat_microsar": CmdInfo(
            "Task/ISR (Thread) Tracing",
            "softwaretracing",
        ),
        "runnable_instrumentation": CmdInfo(
            "Runnable Tracing",
            "runnabletracingwithinstrumentation",
        ),
        "runnable_program_flow": CmdInfo("Runnable Tracing", "runnableprogramflow"),
        "runnable_swat": CmdInfo("Runnable Tracing", "softwaretracing"),
        "signals": CmdInfo("Signals", "signals"),
        "signals_swat": CmdInfo("Signals", "softwaretracing"),
        "spinlock_instrumentation_microsar": CmdInfo("Spinlocks", "spinlockwithinstrumentation"),
    }

    @classmethod
    def createDefaultConfigFile(cls, configFilePathStr: str):
        configFilePath = pathlib.Path(configFilePathStr)
        ItchiConfig.createDefaultConfigFile(configFilePath)

    @classmethod
    def getHtmlData(cls) -> Optional[str]:
        return ItchiHelp.get_html_data()

    @classmethod
    def getHtmlUrl(cls) -> str:
        return ItchiHelp.get_html_url()

    @classmethod
    def getGroupCmds(cls) -> Dict[str, List[str]]:
        ##
        # @brief  Get groups (checkbox menu item) and cmds for each group (combo box)
        # @return A dict of {'groupName': ListOfCmds[]}
        #
        groupsCmds: Dict[str, List[str]] = defaultdict(list)
        for cmd, cmdInfo in Controller.cmds.items():
            groupsCmds[cmdInfo.group].append(cmd)
        return groupsCmds

    def __init__(self, configFilePathStr: str):
        ##
        # @brief Class constructor
        # @param configFilePath Absolute path to the configuration file used for iTCHi configuration
        #
        self._itchiConfig = ItchiConfig(pathlib.Path("itchi.json"))

        if configFilePathStr:
            try:
                configFilePath = pathlib.Path(configFilePathStr).resolve()
                if configFilePath.is_file():
                    self._itchiConfig = ItchiConfig(configFilePath)
                    self._itchiConfig.loadConfigFileData()
                    self._itchiHelp = ItchiHelp()

                    # Change dir to config file dir -> orti, pxml can then use relative path
                    configFileDir = configFilePath.parent
                    os.chdir(configFileDir)
            except BaseException:
                return

    def isConfigDataValid(self) -> bool:
        ##
        # @brief  Check if the configuration data is valid
        # @return True if configuration data is valid, False otherwise
        #
        if self._itchiConfig is not None:
            return self._itchiConfig.isConfigDataValid()

        return False

    def setOrtiFilePath(self, filePathStr: str) -> bool:
        ##
        # @brief  Set ORTI file path
        # @return True if file path is valid and file exists, False otherwise
        #
        if filePathStr:
            try:
                filePath = pathlib.Path(filePathStr)
                if filePath.is_file():
                    self._itchiConfig.setOrtiFilePath(filePath)
                    return True
            except BaseException:
                return False

        return False

    def getOrtiFilePath(self) -> str:
        ortiFilePath = self._itchiConfig.getOrtiFilePath()
        return str(ortiFilePath)

    def setPxmlFilePath(self, filePathStr: str) -> bool:
        ##
        # @brief  Set Profiler XMl file path
        # @return True if file path is valid and directory exists (file will be
        #         created), False otherwise
        bFilePathValid = False

        if filePathStr:
            filePath = pathlib.Path(filePathStr)
            dirPath = filePath.resolve().parent
            if dirPath.exists():
                bFilePathValid = True
                self._itchiConfig.setPxmlFilePath(filePath)

        return bFilePathValid

    def getPxmlFilePath(self) -> str:
        pxmlFilePath = self._itchiConfig.getPxmlFilePath()
        pxmlFilePathStr = str(pxmlFilePath)
        if not pxmlFilePathStr:
            pxmlFilePathStr = "profiler.xml"
        return pxmlFilePathStr

    def getCmdConfigSections(self, cmdKey: str) -> typing.List[str]:
        ##
        # @brief  Get configuration sections that need to be configured by the
        #         user for specified command
        # @param  cmdKey Name of the command
        # @return A list of configuration sections associated with the command
        #
        return self._itchiConfig.getCmdConfigSections(cmdKey)

    def _getConfigSectionAttributeType(
        self, configSectionKey: str, attributeKey: str
    ) -> EConfigSectionAttributeType:
        ##
        # @brief  Get type of an attribute
        # @param  configSectionKey Name of the configuration section
        # @param  attributeKey     Name of the attribute
        # @return Attribute type in form of EConfigSectionAttributeType
        attrType = self._itchiConfig.getAttributeType(configSectionKey, attributeKey)
        originType = typing.get_origin(attrType)
        guiAttrType = EConfigSectionAttributeType.Basic
        if attrType is bool:
            guiAttrType = EConfigSectionAttributeType.Boolean
        elif isinstance(attrType, enum.EnumMeta):
            guiAttrType = EConfigSectionAttributeType.Enum
        elif attrType == pathlib.Path:
            guiAttrType = EConfigSectionAttributeType.Path
        elif originType is list:
            guiAttrType = EConfigSectionAttributeType.IterableOneColumn
        elif originType is dict:
            guiAttrType = EConfigSectionAttributeType.IterableTwoColumns
        elif attrType in [str, int]:
            pass
        else:
            print(f"Unknown ConfigSectionAttributeType {attrType}. Default to basic.")

        return guiAttrType

    def getConfigSectionAttributes(self, configSectionKey: str) -> List[ConfigSectionAttribute]:
        ##
        # @brief  For a configuration section get a list of its attributes, their types and values
        # @param  configSectionKey Name of the configuration section
        # @return A list of dictionaries that contains and attribute, its type and value
        #         [{'name': attributeName, 'type': attributeType, 'value': attributeValue}, ...]
        #

        configSectionAttrTypeList = []
        attributes = self._itchiConfig.getConfigSectionAttributes(configSectionKey)
        for attributeName in attributes:
            attributeType = self._getConfigSectionAttributeType(configSectionKey, attributeName)
            attributeValue = self._itchiConfig.getConfigSectionAttributeValue(
                configSectionKey, attributeName
            )
            attribute = ConfigSectionAttribute(attributeName, attributeType, attributeValue)

            if isinstance(attributeValue, dict):
                items = []
                for k, v in attributeValue.items():
                    if isinstance(v, enum.Enum):
                        # Convert enum values to lowercase strings for GUI serialization
                        items.append((k, v.name.lower()))
                    else:
                        items.append((k, v))
                attribute.value = items
            elif isinstance(attributeValue, enum.Enum):
                attribute.value = attributeValue
            elif isinstance(attributeValue, pathlib.Path):
                if attributeValue == pathlib.Path(""):
                    attribute.value = ""
                else:
                    attribute.value = str(attributeValue)
            configSectionAttrTypeList.append(attribute)

        return configSectionAttrTypeList

    def setConfigSectionAttribute(
        self, configSectionKey: str, attributeKey: str, value: typing.Any
    ):
        ##
        # @brief Set value to the attribute
        # @param configSectionKey Name of the configuration section
        # @param attributeKey     Name of the attribute
        # @param value            Value to be set to attribute
        #

        # Cast value back to the expected type and save it in model
        attrTypeUI = self._getConfigSectionAttributeType(configSectionKey, attributeKey)
        if attrTypeUI in (
            EConfigSectionAttributeType.IterableOneColumn,
            EConfigSectionAttributeType.IterableTwoColumns,
        ):
            attrType = self._itchiConfig.getAttributeType(configSectionKey, attributeKey)
            if value:
                valueStr = (
                    "[" + value + "]" if typing.get_origin(attrType) is list else "{" + value + "}"
                )
                valueList = ast.literal_eval(valueStr)
            else:
                valueList = [] if typing.get_origin(attrType) is list else {}
            self._itchiConfig.setConfigSectionAttributeValue(
                configSectionKey, attributeKey, valueList
            )
        else:
            self._itchiConfig.setConfigSectionAttributeValue(configSectionKey, attributeKey, value)

    def isConfigSectionAlsoAttribute(self, configSectionKey: str) -> bool:
        if not configSectionKey:
            return False

        return self._itchiConfig.isConfigSectionAlsoAttribute(configSectionKey)

    def wasCmdPreviouslySelected(self, cmdKey: str) -> bool:
        commandDictList = self.getConfigSectionAttributes("commands")
        cmdIdx = next(
            (index for (index, d) in enumerate(commandDictList) if d.name == cmdKey), None
        )
        if (cmdIdx is not None) and (commandDictList[cmdIdx].value is True):
            return True

        return False

    def saveSelectedCommands(self, selectedCmdKeyList: typing.List[str]):
        # Set all commands to false -> if they were previously selected
        for cmd in self.getConfigSectionAttributes("commands"):
            cmdSelected = True if cmd.name in selectedCmdKeyList else False
            self.setConfigSectionAttribute("commands", cmd.name, cmdSelected)

    def set_log_file(self, log_file: str):
        self.log_file = log_file

    def runItchi(self):
        # Consolas font has charaters with the same width so that new lines are properly aligned
        out_msg = "<html><body>"
        out_msg += "<style>.pre {font-family: Consolas;}</style>"
        out_msg += "-------------------- RUNNING ITCHI --------------------"
        msg_style = ""

        b_save_success, err_msg = self._itchiConfig.saveConfigFileData()
        if b_save_success:
            config_file_path = str(self._itchiConfig.getConfigFilePath())

            parser = itchi_cli.create_parser()
            captured_output = io.StringIO()
            sys.stdout = captured_output
            itchi_cli.main(
                parser.parse_args(["--config", config_file_path, "--log_file", self.log_file])
            )

            msg = f"<pre>{captured_output.getvalue()}</pre>"
            sys.stdout = sys.__stdout__
        else:
            msg_style = "style='color:red;'"
            msg = "There was a problem with saving configuration data\n"
            msg += err_msg

        out_msg += f"<pre {msg_style}>{msg}</pre>"
        now = datetime.datetime.now().strftime("%H:%M:%S")
        out_msg += f"-------------------- FINISHED {now} --------------------"
        out_msg += "</body></html>"
        return out_msg

    def getLogFileData(self):
        # Log file is located in the same folder as .json config file (current directory)
        try:
            with open(self.log_file, mode="r", encoding="utf-8") as f:
                logData = f.read()
        except Exception as ex:
            logData = f"FAILED: {ex}"

        return logData

    def getHtmlElementId(self, cmdKey: str) -> str:
        if cmdKey in self.cmds:
            return self.cmds[cmdKey].htmlElementId
        return ""

    def getAttributesHelp(self, cfgSectionsList: List[str]) -> Tuple[List[str], List[List[str]]]:
        # Get documentation for all attributes
        cells_data = []
        for top_level_key, value in CONFIG_ATTRS_DOC.items():
            if type(value) is str:
                cells_data.append([top_level_key, value])
            elif type(value) is dict:
                for sub_level_key, sub_value in value.items():
                    cells_data.append([f"{top_level_key} {sub_level_key}", sub_value])

        # Filter data to only show the relevant sections
        cells_data_shown = []
        for cellData in cells_data:
            attr_cfg_section_name = cellData[0].split(" ")[0]
            if attr_cfg_section_name in cfgSectionsList:
                cells_data_shown.append(cellData)

        column_names = ["attribute", "description"]
        return (column_names, cells_data_shown)
