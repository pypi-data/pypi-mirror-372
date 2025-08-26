import pathlib
import typing
import urllib.request
import itchi.config as config


class ItchiConfig:
    def __init__(self, configFilePath: pathlib.Path):
        ##
        # @brief Class constructor
        # @param configFilePath path to the configuration (.json) file
        #
        self._oldConfig = config.ItchiConfig.default_factory()
        self._newConfig = config.ItchiConfig.default_factory()
        self._defaultConfig = config.ItchiConfig.default_factory()
        self._configDataValid = True
        self._configFilePath = pathlib.Path(configFilePath)

    def getConfigFilePath(self) -> pathlib.Path:
        return self._configFilePath

    @classmethod
    def createDefaultConfigFile(cls, configFilePath: pathlib.Path):
        config.write_default_config(configFilePath)

    def loadConfigFileData(self) -> bool:
        ##
        # @brief  Load configuration data from file specified at object instantiation
        # @return True if configuration data was successfully loaded and is valid else False
        #
        try:
            self._oldConfig = config.load_config(self._configFilePath)
            self._configDataValid = True
        except BaseException:
            self._configDataValid = False

        return self._configDataValid

    def saveConfigFileData(self) -> typing.Tuple[bool, str]:
        ##
        # @brief  Save configuration data in file whose path was specified at object instantiation
        # @return A tuple of (True, "") if data was successfully saved else (False, exceptionString)
        #
        bFileSavedSuccess = False
        errMsg = ""

        if self._configDataValid:
            try:
                configData = config.ItchiConfig(**self._newConfig.model_dump())
                with open(self._configFilePath, mode="w", encoding="utf-8") as f:
                    f.write(configData.model_dump_json(indent=4))

                bFileSavedSuccess = True
            except Exception as ex:
                errMsg = str(ex)

        return (bFileSavedSuccess, errMsg)

    def isConfigDataValid(self) -> bool:
        ##
        # @brief  Check if the configured data is valid
        # @return True if configured data is valid else False
        #
        return self._configDataValid

    def getOrtiFilePath(self) -> pathlib.Path:
        return self._oldConfig.orti_file

    def setOrtiFilePath(self, filePath: pathlib.Path):
        self._newConfig.orti_file = filePath

    def getPxmlFilePath(self) -> pathlib.Path:
        return self._oldConfig.profiler_xml_file

    def setPxmlFilePath(self, filePath: pathlib.Path):
        self._newConfig.profiler_xml_file = filePath

    def isConfigSectionAlsoAttribute(self, configSectionKey: str):
        if hasattr(self._defaultConfig, configSectionKey) and type(
            getattr(self._defaultConfig, configSectionKey)
        ) in (
            str,
            list,
        ):
            return True

        return False

    def getCmdConfigSections(self, cmdKey: str) -> typing.List[str]:
        ##
        # @brief  Get configuration sections that need to be configured by the user for specified command
        # @param  cmdKey Name of the command
        # @return A list of configuration sections associated with the command
        #
        return config.CommandConfig.get_required_sections(cmdKey)

    def getConfigSectionAttributes(self, configSectionKey: str) -> typing.List[str]:
        ##
        # @brief  Get attributes of the specified configuration section
        # @param  configSectionKey Name of the configuration section
        # @return A list of attributes in configuration section
        #
        attributesList = []
        if self.isConfigSectionAlsoAttribute(configSectionKey):
            attributesList = [configSectionKey]
        else:
            configSectionObj = getattr(self._defaultConfig, configSectionKey)
            if configSectionObj:
                attributesList = configSectionObj.model_dump().keys()

        return attributesList

    def getConfigSectionAttributeValue(
        self, configSectionKey: str, attributeKey: str
    ) -> typing.Any:
        ##
        # @brief  Get value of the attribute in configuration section
        # @param  configSectionKey Name of the configuration section
        # @param  attributeKey     Name of the attribute
        # @return Value of the attribute
        #

        # Get attribute value from the old configuration file (if available) or
        # from the default configuration
        if self.isConfigSectionAlsoAttribute(configSectionKey):
            config = (
                self._oldConfig
                if hasattr(self._oldConfig, configSectionKey)
                else self._defaultConfig
            )
            attributeValue = getattr(config, attributeKey)
        else:
            config = self._defaultConfig
            if hasattr(self._oldConfig, configSectionKey):
                if hasattr(getattr(self._oldConfig, configSectionKey), attributeKey):
                    config = self._oldConfig
            configSectionObj = getattr(config, configSectionKey)
            attributeValue = getattr(configSectionObj, attributeKey)
        return attributeValue

    def setConfigSectionAttributeValue(
        self, configSectionKey: str, attributeKey: str, value: typing.Any
    ):
        ##
        # @brief Set value of the attribute in configuration section
        # @param configSectionKey Name of the configuration section
        # @param attributeKey     Name of the attribute
        # @param value            Value to be set
        #
        if self.isConfigSectionAlsoAttribute(configSectionKey):
            setattr(self._newConfig, configSectionKey, value)
        else:
            configSectionObj = getattr(self._newConfig, configSectionKey)
            setattr(configSectionObj, attributeKey, value)

    def getAttributeType(self, configSectionKey: str, attributeKey: str) -> typing.Any:
        ##
        # @brief  Get type hint of an attribute
        # @param  configSectionKey Name of the configuration section
        # @param  attributeKey     Name of the attribute
        # @return Attribute type by using get_type_hints()
        #
        if self.isConfigSectionAlsoAttribute(configSectionKey):
            attributeType = typing.get_type_hints(self._defaultConfig)[attributeKey]
        else:
            configSectionObj = getattr(self._defaultConfig, configSectionKey)
            attributeType = typing.get_type_hints(configSectionObj)[attributeKey]

        return attributeType


class ItchiHelp:
    _html_url: str = "https://www.isystem.com/downloads/winIDEA/help/itchi-commands.html"
    _html_data: typing.Optional[str] = None

    try:
        with urllib.request.urlopen(_html_url) as response:
            _html_data = response.read().decode("utf-8")
    except Exception:
        print(f"Could not open iTCHi help at {_html_url}")

    @classmethod
    def get_html_url(cls) -> str:
        return cls._html_url

    @classmethod
    def get_html_data(cls) -> typing.Optional[str]:
        return cls._html_data
