import re
import logging
import sys
from pathlib import Path
from typing import Dict, List

from .orti_parser import OrtiEnum, Parser
from .orti_scanner import Scanner


class Orti(dict):
    def __init__(self, orti_file_path: Path):
        logging.info(f"Load '{orti_file_path}'.")
        with open(orti_file_path, "r") as f:
            source = f.read()

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        assert not scanner.has_error, "Failed to scan ORTI file."
        parser = Parser(tokens)

        # Our parser parses the ORTI string into a dictionary object. What we would
        # like to do is to create a proper data model for the ORTI file and then
        # translate the dictionary into that data model. However, we currently don't have
        # such a data model and we have to live with the type error in the following line.
        orti_dict: dict = parser.parse()
        if orti_dict is None:
            logging.critical("Could not parse ORTI file.")
            sys.exit(1)

        self.orti_file = orti_file_path
        self.update(orti_dict)
        self.merge_os_objects()

        # The following two variables are used to override the heuristic
        # that gets the default ISR2 and Task strings from the ORTI file.
        self._default_task = ""
        self._default_isr2 = ""

        # On some microcontrollers the ORTI core index does not match the
        # physical core on the target. For example, on Cortex-M based devices
        # there might be a M0+ core which does not run AUTOSAR, but has the
        # index 0. In this case, the AUTOSAR core 0 must be remapped to core 1
        # (say the M4 core). The following variable is used to do the remapping.
        self.orti_core_to_soc_core: Dict[int, int] = {}
        # Similarly, on SoCs the ORTI core index is not helpful to identify the
        # core. With this attribute we allow remapping an ORTI core to a SoC name.
        # If no mapping is provided, a default string is used.
        self.orti_core_to_soc_name: Dict[int, str] = {}

    def get_declaration_spec(self, object_type):
        ds = [
            d
            for d in self["declaration_section"]["declaration_specs"]
            if d["object_type"] == object_type
        ]
        assert len(ds) == 1
        return ds[0]

    def get_attribute_decl(self, object_type: str, attribute_name: str):
        object_decl = self.get_declaration_spec(object_type)

        # See get_attribute_defs for explanation.
        smpSupport = r"(\[\])?"
        regexString = r"^{}{}$".format(attribute_name, smpSupport)
        r = re.compile(regexString)
        attribute_decls = [
            attribute_decl
            for attribute_decl in object_decl["attribute_decls"]
            if r.match(attribute_decl["attribute_name"])
        ]
        assert (
            len(attribute_decls) == 1
        ), f"Expected one attribute {attribute_name} of type {object_type}."
        return attribute_decls[0]

    def get_object_defs(self):
        return self["information_section"]

    def get_object_defs_by_type(self, object_type: str):
        return [o for o in self.get_object_defs() if o["object_type"] == object_type]

    def get_object_defs_task(self):
        return self.get_object_defs_by_type("TASK")

    def get_object_def_by_name(self, object_name: str):
        os = [o for o in self.get_object_defs() if o["object_name"] == object_name]
        assert len(os) == 1
        return os[0]

    def merge_os_objects(self):
        """
        ORTI 2.2 Part B specifies that there can only be one OS object.
        However, ETAS writes an OS object for each core anyway.
        This breaks the Orti API. To restore expected functionality
        this procedure merges multiple OS objects into a single
        object that adheres to the ORTI 2.3 Multi-Core extensions.
        """
        os_objects = self.get_object_defs_by_type("OS")
        if len(os_objects) == 1:
            #  Only one OS object there. We are good.
            return
        m = f"'{self.orti_file}' contains multiple OS objects. Merging into single object."
        logging.debug(m)
        merged_os = {"object_type": "OS", "object_name": "OsMerged", "attributes": []}
        for core_index, os_object in enumerate(os_objects):
            os_object["object_type"] = "INVALID_OS"
            for a in os_object["attributes"]:
                a["attribute_name"] += "[{}]".format(core_index)
                merged_os["attributes"].append(a)
        self["information_section"].append(merged_os)

    def get_object_def_os(self):
        os_objects = self.get_object_defs_by_type("OS")
        # There can be only one OS object according to ORTI 2.2 Part B spec.
        assert len(os_objects) == 1
        return os_objects[0]

    def get_attribute_defs(self, object_type: str, attribute_name: str):
        objects = self.get_object_defs_by_type(object_type)

        # We have to find both "attribute_name" as well as "attribute_name[2]".
        # I.e., we are supporting the ORTI SMP extension.
        smp_support = r"(\[\d+\])?"
        r_string = r"^{}{}$".format(attribute_name, smp_support)
        r = re.compile(r_string)

        def get_soc_core(match) -> int:
            # The idea of this little function is to detect whether SMP
            # extension is used or not.  If the optional smp_support is hit
            # then the tuple contains that string.  Otherwise, it contains none
            # in which case the index is simply zero.
            index = 0
            if match.groups()[0] is not None:
                index = int(match.groups()[0].lstrip("[").rstrip("]"))
            if index in self.orti_core_to_soc_core:
                index = self.orti_core_to_soc_core[index]
            return index

        def get_soc_name(match) -> str:
            index = 0
            if match.groups()[0] is not None:
                index = int(match.groups()[0].lstrip("[").rstrip("]"))
            if index in self.orti_core_to_soc_name:
                soc_name = self.orti_core_to_soc_name[index]
            else:
                soc_name = f"Core {index}"
            return soc_name

        attribute_defs = []
        for object in objects:
            for attribute in object["attributes"]:
                if match := r.match(attribute["attribute_name"]):
                    attribute_name = attribute["attribute_name"]
                    attribute["soc_core"] = get_soc_core(match)
                    attribute["soc_name"] = get_soc_name(match)
                    attribute_defs.append(attribute)
        return attribute_defs

    def get_attribute_defs_runningtask(self):
        attribute_defs = self.get_attribute_defs("OS", "RUNNINGTASK")
        return attribute_defs

    def get_attribute_defs_runningisr2(self):
        attribute_defs = self.get_attribute_defs("OS", "RUNNINGISR2")
        if len(attribute_defs) == 0:
            m = "Could not find RUNNINGISR2 attribute definitions. Falling back to RUNNINGISR."
            logging.warning(m)
            attribute_defs = self.get_attribute_defs("OS", "RUNNINGISR")
        return attribute_defs

    def get_enum_elements(self, object_type: str, attribute_name: str) -> List[OrtiEnum]:
        attr_decl = self.get_attribute_decl(object_type, attribute_name)
        enum_elements = attr_decl["attribute_type"]["enum_elements"]
        return enum_elements

    def get_enum_elements_runningtask(self) -> List[OrtiEnum]:
        return self.get_enum_elements("OS", "RUNNINGTASK")

    def get_enum_elements_runningisr2(self) -> List[OrtiEnum]:
        return self.get_enum_elements("OS", "RUNNINGISR2")

    def get_enum_elements_task_state(self) -> List[OrtiEnum]:
        return self.get_enum_elements("TASK", "STATE")

    def set_default_task(self, name: str):
        self._default_task = name

    def set_default_isr2(self, name: str):
        self._default_isr2 = name

    def get_default_task(self):
        """
        Returns the default Task based on the following steps.

        1. If self._default_task then it is returned.
        2. If NO_TASK or INVALID_TASK is found in the ORTI it is returned.
        3. Otherwise, the name of the last element in the RUNNINGTASK
           declaration is returned.
        """
        if self._default_task:
            return self._default_task

        attr_decl = self.get_attribute_decl("OS", "RUNNINGTASK")
        enum_elements = attr_decl["attribute_type"]["enum_elements"]
        assert len(enum_elements) > 0, "At least one RUNNINGTASK ENUM elem is expected"
        for elem in enum_elements:
            if elem.desc in ["NO_TASK", "INVALID_TASK"]:
                return elem.desc
        return enum_elements[-1].desc

    def get_default_isr2(self):
        """
        Returns the default ISR2 based on the following steps.

        1. If self._default_isr2 then it is returned.
        2. If NO_ISR or INVALID_ISR is found in the ORTI it is returned.
        3. Otherwise, the name of the last element in the RUNNINGISR2
           declaration is returned.
        """
        if self._default_isr2:
            return self._default_isr2

        try:
            attr_decl = self.get_attribute_decl("OS", "RUNNINGISR2")
        except AssertionError:
            logging.warning(
                "Could not find RUNNINGISR2 attribute decl. Falling back to RUNNINGISR."
            )
            attr_decl = self.get_attribute_decl("OS", "RUNNINGISR")
        enum_elements = attr_decl["attribute_type"]["enum_elements"]
        assert len(enum_elements) > 0, "At least one RUNNINGISR2 ENUM elem is expected"
        for elem in enum_elements:
            if elem.desc in ["NO_ISR", "INVALID_ISR"]:
                return elem.desc
        return enum_elements[-1].desc

    def get_os_name(self):
        """Returns the name of the OS object definition."""
        return self.get_object_def_os()["object_name"]

    def get_number_of_cores(self):
        """Returns the number of runningtask definitions."""
        return len(self.get_attribute_defs_runningtask())

    def search_and_replace_running_taskisr(self, search_replace_list):
        if not search_replace_list:
            return
        tasks = self.get_attribute_defs_runningtask()
        isr2s = self.get_attribute_defs_runningisr2()
        elems = tasks + isr2s
        for e in elems:
            old_formula = e["formula"]
            for search, replace in search_replace_list:
                e["formula"] = e["formula"].replace(search, replace)
            new_formula = e["formula"]
            if old_formula != new_formula:
                m = "Replaced '{}' with '{}'.".format(old_formula, new_formula)
                logging.debug(m)

    def replace_spaces_in_states(self):
        """Replace spaces in Task STATE attributes with underscores."""
        try:
            taskStateEnum = self.get_enum_elements_task_state()
        except AssertionError:
            # EB AutoCore OS for TriCore does not contain TASK STATE attributes
            logging.info("ORTI file does not contain TASK STATE attributes.")
            return
        for enum in taskStateEnum:
            enum.desc = enum.desc.replace(" ", "_")
