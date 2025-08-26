from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
from .save import save


class BtfTransition(BaseModel):
    text: str

    def to_et(self) -> ET.Element:
        e = ET.Element("BTF_Transition")
        e.text = self.text
        return e


class Enum(BaseModel):
    name: str
    value: str
    task_state_property: Optional[str] = None
    spinlock_state_property: Optional[str] = None
    context_state_formula: Optional[str] = None
    additional_values_property: Optional[List[str]] = None

    # Attributes for when Enum functions as a TaskState single variable Enum
    name_property: Optional[str] = None
    value_property: Optional[str] = None

    def __init__(self, name: str, value: str, **data):
        super().__init__(name=name, value=value, **data)

    def to_et(self) -> ET.Element:
        e = ET.Element("Enum")
        append(e, "Name", self.name)
        append(e, "Value", self.value)

        properties = None
        if self.task_state_property:
            properties = properties or ET.Element("Properties")
            append(properties, "TaskState", self.task_state_property)

        if self.spinlock_state_property:
            properties = properties or ET.Element("Properties")
            append(properties, "SpinlockState", self.spinlock_state_property)

        if self.name_property and self.value_property:
            property = ET.SubElement(e, "Property")
            append(property, "Name", self.name_property)
            append(property, "Value", self.value_property)

        # Required when multiple names map to the same value
        if self.additional_values_property:
            properties = properties or ET.Element("Properties")
            for value in self.additional_values_property:
                append(properties, "Value", value)

        # Required for complex state analysis in winIDEA
        if self.context_state_formula:
            properties = properties or ET.Element("Properties")
            append(properties, "ContextStateFormula", self.context_state_formula)

        if properties is not None:
            e.append(properties)

        return e


class TypeEnum(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    name: str
    properties: List[BtfTransition] = []
    enums: List[Enum] = []

    # If we load a TypeEnum from an existing file we store it here.
    # In case we don't update it we can write it back unchanged.
    existing: Optional[ET.Element] = None

    def to_et(self) -> ET.Element:
        if self.existing is not None:
            return self.existing
        e = ET.Element("TypeEnum")
        append(e, "Name", self.name)
        if self.properties:
            properties = ET.SubElement(e, "Properties")
            for property in self.properties:
                properties.append(property.to_et())
        for enum in self.enums:
            e.append(enum.to_et())
        return e

    @staticmethod
    def from_et(e: ET.Element) -> "TypeEnum":
        return TypeEnum(
            name=find(e, "Name"),
            existing=e,
        )


class StateInfo(BaseModel):
    name: str
    property: str

    def __init__(self, name: str, property: str):
        super().__init__(name=name, property=property)

    def to_et(self) -> ET.Element:
        e = ET.Element("StateInfo")
        append(e, "Name", self.name)
        append(e, "Property", self.property)
        return e


class RunnableState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mask_id: str
    mask_core: Optional[str] = None
    exit_value: int

    def to_et(self) -> ET.Element:
        e = ET.Element("Runnable")
        append(e, "MaskID", self.mask_id)
        if self.mask_core:
            append(e, "MaskCore", self.mask_core)
        append(e, "ExitValue", str(self.exit_value))
        return e


class TaskState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mask_id: Optional[str] = None
    mask_state: Optional[str] = None
    mask_core: Optional[str] = None
    type: Optional[str] = None
    btf_mapping_type: Optional[str] = None
    state_infos: List[StateInfo] = []

    def to_et(self) -> ET.Element:
        e = ET.Element("TaskState")
        append_if(e, "MaskID", self.mask_id)
        append_if(e, "MaskState", self.mask_state)
        append_if(e, "MaskCore", self.mask_core)
        append_if(e, "Type", self.type)
        append_if(e, "BTFMappingType", self.btf_mapping_type)

        for state_info in self.state_infos:
            e.append(state_info.to_et())
        return e


class Sampling(BaseModel):
    model_config = ConfigDict(extra="forbid")

    acquisition: str
    sample_pool: int

    def to_et(self) -> ET.Element:
        e = ET.Element("Properties")
        append(e, "Acquisition", self.acquisition)
        append(e, "SamplePool", str(self.sample_pool))
        return e


class Spinlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mask_id: str = "0x0000FFFF"
    mask_core: str = "0xFF000000"
    mask_type: str = "0x00FF0000"
    type: str = "TypeEnum_SpinlockState"
    state_analysis: bool = True

    def to_et(self) -> ET.Element:
        e = ET.Element("Properties")
        append(e, "Spinlock_MaskID", self.mask_id)
        append(e, "Spinlock_MaskCore", self.mask_core)
        append(e, "Spinlock_MaskType", self.mask_type)
        append(e, "Spinlock_Type", self.type)
        append(e, "Spinlock_TaskStateAnalysis", str(self.state_analysis).lower())
        return e


class SwatConfigProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type_mask: str
    time_offset: int
    time_size: int
    time_right_shift: int
    structure: str
    target_version: str
    target_interface: str
    time_address: str = ""  # can be overriden via config
    polling_interval: int = 1  # `0` means as fast as possible

    def to_et(self, p: Optional[ET.Element]) -> ET.Element:
        e = p if p is not None else ET.Element("Properties")
        append(e, "TypeMask", self.type_mask)
        append(e, "TimeOffset", str(self.time_offset))
        append(e, "TimeSize", str(self.time_size))
        append(e, "TimeRightShift", str(self.time_right_shift))
        append(e, "Structure", self.structure)
        append(e, "TargetVersion", self.target_version)
        append(e, "TargetInterface", self.target_interface)
        if self.time_address != "":
            append(e, "TimeAddress", self.time_address)
        append(e, "PollingInterval", str(self.polling_interval))
        return e


class SwatObjectProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type_value: int = 0
    data_offset: int = 0
    data_size: int = 0

    task_state_mask_core: Optional[str] = None
    task_state_mask_state: Optional[str] = None
    task_state_mask_thread_id: Optional[str] = None
    task_state_type_enum_name: Optional[str] = None

    runnable_mask_core: Optional[str] = None
    runnable_mask_id: Optional[str] = None
    runnable_exit_value: Optional[str] = None

    def to_et(self, p: Optional[ET.Element]) -> ET.Element:
        e = p if p is not None else ET.Element("Properties")
        append(e, "SWAT_TypeValue", hex(self.type_value))
        append(e, "SWAT_DataOffset", str(self.data_offset))
        append(e, "SWAT_DataSize", str(self.data_size))

        append_if(e, "TaskState_MaskCore", self.task_state_mask_core)
        append_if(e, "TaskState_MaskState", self.task_state_mask_state)
        append_if(e, "TaskState_MaskID", self.task_state_mask_thread_id)
        append_if(e, "TaskState_Type", self.task_state_type_enum_name)

        append_if(e, "Runnable_MaskCore", self.runnable_mask_core)
        append_if(e, "Runnable_MaskID", self.runnable_mask_id)
        append_if(e, "Runnable_ExitValue", self.runnable_exit_value)
        return e


class ProfilerObject(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    name: str
    definition: str
    description: str
    type: Optional[str] = None
    default_value: Optional[str] = None
    expression: Optional[str] = None
    signaling: Optional[str] = None
    level: Optional[str] = None
    core: Optional[str] = None
    source_core: Optional[str] = None
    task_state: Optional[TaskState] = None
    arti_mdf4_mapping_type: Optional[str] = None
    btf_mapping_type: Optional[str] = None
    runnable_state: Optional[RunnableState] = None
    sampling: Optional[Sampling] = None
    spinlock: Optional[Spinlock] = None
    task_state_type: Optional[str] = None
    swat_config_properties: Optional[SwatConfigProperties] = None
    swat_object_properties: Optional[SwatObjectProperties] = None

    # If we load a ProfilerObject from an existing file we store it here.
    # In case we don't update it we can write it back unchanged.
    existing: Optional[ET.Element] = None

    def to_et(self) -> ET.Element:
        if self.existing is not None:
            return self.existing
        e = ET.Element("Object")
        append(e, "Name", self.name)
        append(e, "Definition", self.definition)
        append(e, "Description", self.description)
        append_if(e, "Type", self.type)
        append_if(e, "DefaultValue", self.default_value)
        append_if(e, "Expression", self.expression)
        append_if(e, "Signaling", self.signaling)
        append_if(e, "Level", self.level)
        append_if(e, "Core", self.core)
        append_if(e, "SourceCore", self.source_core)

        if self.task_state:
            e.append(self.task_state.to_et())

        if self.runnable_state:
            e.append(self.runnable_state.to_et())

        if self.sampling:
            e.append(self.sampling.to_et())

        if self.spinlock:
            e.append(self.spinlock.to_et())

        p = None
        if self.arti_mdf4_mapping_type:
            p = p if p is not None else ET.Element("Properties")
            append(p, "TaskState_ARTIMappingType", self.arti_mdf4_mapping_type)

        if self.btf_mapping_type:
            p = p if p is not None else ET.Element("Properties")
            append(p, "TaskState_BTFMappingType", self.btf_mapping_type)

        if self.task_state_type:
            p = p if p is not None else ET.Element("Properties")
            append(p, "TaskState_Type", self.task_state_type)

        if self.swat_config_properties:
            p = self.swat_config_properties.to_et(p)

        if self.swat_object_properties:
            p = self.swat_object_properties.to_et(p)

        if p is not None:
            e.append(p)

        return e

    @staticmethod
    def from_et(e: ET.Element) -> "ProfilerObject":
        return ProfilerObject(
            name=find(e, "Name"),
            definition=find(e, "Definition"),
            description=find(e, "Description"),
            expression=find_if(e, "Expression"),
            existing=e,
        )


class ProfilerXml(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = "OS"
    num_cores: int = 1
    orti: Optional[str] = ""
    inspector_path: Optional[str] = None
    types: List[TypeEnum] = []
    objects: List[ProfilerObject] = []

    def to_et(self) -> ET.Element:
        e = ET.Element("OperatingSystem")
        append(e, "Name", self.name)
        append(e, "NumCores", str(self.num_cores))
        if self.orti is not None:
            append(e, "ORTI", self.orti)

        if self.types:
            types = ET.SubElement(e, "Types")
            for type_enum in self.types:
                types.append(type_enum.to_et())

        objects = ET.SubElement(e, "Profiler")
        if self.inspector_path:
            inspector = ET.SubElement(objects, "Inspector")
            append(inspector, "Path", str(self.inspector_path))

        for object in self.objects:
            objects.append(object.to_et())

        return e

    @staticmethod
    def from_et(e: ET.Element) -> "ProfilerXml":
        return ProfilerXml(
            name=find(e, "Name"),
            num_cores=int(find(e, "NumCores")),
            orti=find_if(e, "ORTI"),
            inspector_path=find_if(e, "Profiler.Inspector.Path"),
            types=[TypeEnum.from_et(c) for c in e.iter("TypeEnum")],
            objects=[ProfilerObject.from_et(c) for c in e.iter("Object")],
        )

    def set_type_enum(self, new: TypeEnum) -> None:
        """Override TypeEnum with the same name or append."""
        for i, existing in enumerate(self.types):
            if new.name == existing.name:
                self.types[i] = new
                break
        else:
            self.types.append(new)

    def set_object(self, new: ProfilerObject) -> None:
        """Override ProfilerObject with the same name or append."""
        for i, existing in enumerate(self.objects):
            if new.name == existing.name:
                self.objects[i] = new
                break
        else:
            self.objects.append(new)

    def save(self, filename: Path):
        save(self.to_et(), filename)


def append(e: ET.Element, key: str, value: str) -> ET.Element:
    """Append element with tag key and text value to element tree object."""
    child = ET.Element(key)
    child.text = value
    e.append(child)
    return e


def append_if(e: ET.Element, key: str, value: Optional[str]) -> ET.Element:
    """Append element with tag key and text value if value is not None."""
    if value is None:
        return e
    return append(e, key, value)


def find(e: ET.Element, key: str) -> str:
    """Finds element with the key and returns text. Raises Exception
    if there is not exactly one child element with the key."""
    elems = e.findall(key)
    if len(elems) == 0:
        m = f"Missing expected tag {key}."
        raise ValueError(m)
    elif len(elems) > 1:
        m = f"Multiple tags {key}. Only one is expected."
        raise ValueError(m)
    elem = elems[0]
    if elem.text is None:
        return ""
    return elem.text


def find_if(e: ET.Element, key: str) -> Optional[str]:
    """Finds first element with the key and returns text. Returns None
    if it does not exist. Can find multiple keys recursively by delimiting
    keys with '.'. For example, 'Profiler.Inspector.Path'."""
    if key == "":
        if e.text is None:
            return ""
        return e.text
    keys = key.split(".")
    elem = e.find(keys[0])
    if elem is None:
        return None
    return find_if(elem, ".".join(keys[1:]))
