import xml.etree.ElementTree as ET
from pathlib import Path


def save(profiler_xml_et: ET.Element, filename: Path) -> None:
    """ Save Profiler XML object to file. """
    indent(profiler_xml_et)
    tree = ET.ElementTree(profiler_xml_et)
    add_namespace_attributes(tree)
    tree.write(filename)


def add_namespace_attributes(tree: ET.ElementTree) -> None:
    root = tree.getroot()
    attributes = [
        ("xmlns", "http://resources.isystem.com/rtos_description"),
        ("xmlns:it", "http://www.w3.org/2001/XMLSchema-instance"),
        ("it:schemaLocation",
            "http://resources.isystem.com/rtos_description https://www.isystem.com/downloads/schemas/RTOS_description_0.xsd"), ]
    for key, value in attributes:
        root.set(key, value)


def indent(elem: ET.Element, level: int = 0):
    """Takes a ET object an reindents it took look nice when
    written to a file.

    http://effbot.org/zone/element-lib.htm#prettyprint

    :param elem: The ET element to pretty print.
    :param level: Current indent level. (Default value = 0)

    """
    i = "\n" + level * "  "
    if len(elem):
        if elem.tag == "Enum":
            elem.tail = i
            return
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
