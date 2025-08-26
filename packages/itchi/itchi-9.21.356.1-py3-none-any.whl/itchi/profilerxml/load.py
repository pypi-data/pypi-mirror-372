import re
import os
import logging
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional
from .model import ProfilerXml


def load_or_create(filename: Path) -> ProfilerXml:
    if os.path.isfile(filename):
        profiler_xml = load(filename)
        if profiler_xml is None:
            m = f"Could not load '{filename}'. Delete the file to create a new one."
            logging.critical(m)
            sys.exit(1)
        m = f"Load '{filename}'."
        logging.info(m)
    else:
        profiler_xml = ProfilerXml()
    return profiler_xml


def load(path: Path) -> Optional[ProfilerXml]:
    purge_namespace_attributes(path)
    try:
        root_element = ET.parse(path).getroot()
        profilerxml = ProfilerXml.from_et(root_element)
        return profilerxml
    except ET.ParseError:
        logging.critical("XML Parser error.")
        return None
    except ValueError as e:
        logging.critical(e)
        return None


def purge_namespace_attributes(path: Path) -> None:
    """
    If an existing Profiler XML file has namespace attributes ElementTree will prefix all
    elements accordingly. That makes it a nightmare to work with. To avoid the issue our crude
    solution is to strip out the namespace attributes. We do that by removing all characters
    between '<OperatingSystem' and '>'. It's not ideal, but it solves the problem well. The save
    routine later adds the attributes back before writing out the file.
    """
    r = re.compile("<OperatingSystem[^>]*>")
    with open(path, "r") as f:
        xml: str = f.read()
        xml = r.sub("<OperatingSystem>", xml)
    with open(path, "w") as f:
        f.write(xml)
