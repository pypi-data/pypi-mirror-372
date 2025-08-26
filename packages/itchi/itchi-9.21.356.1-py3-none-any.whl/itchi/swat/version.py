from dataclasses import dataclass


@dataclass
class SwatVersion:
    major: int = 1
    minor: int = 0
    revision: int = 1
    patch: int = 0
    interface_id: int = 1

    def target_version_profiler_xml_str(self) -> str:
        return f"v{self.major}_{self.minor}r{self.revision}p{self.patch}"

    def target_interface_profiler_xml_str(self) -> str:
        return f"{self.interface_id}"
