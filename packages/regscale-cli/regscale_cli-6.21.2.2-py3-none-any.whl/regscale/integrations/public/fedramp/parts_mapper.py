import json
from typing import List, Optional, Tuple

from regscale.core.decorators import singleton


@singleton
class PartMapper:
    """
    PartMapper class Standardized approach to mapping identifiers between control id in FedRAMP and other frameworks

    # Example usage
    mapper = PartMapper()
    mapper.load_fedramp_version_5_mapping() or mapper.load_json_from_file("path/to/fedramp_r5_parts.json")
    control_label_and_part_results = mapper.find_by_control_label_and_part("AC-1", "a1")
    oscal_control_id_and_part_results = mapper.find_by_oscal_control_id_and_part("ac-1", "a1")
    print("Results for control label 'AC-1' and part 'a1':", control_label_and_part_results)
    print("Results for OSCAL control ID 'ac-1' and part 'a1':", oscal_control_id_and_part_results)
    """

    def __init__(self):
        self.data = []

    def find_by_source(self, source: str) -> Optional[str]:
        """
        Find a mapping by source.
        :param str source: The source.
        :return: A str of the oscal part identifier or null.
        :rtype: Optional[str]
        """
        result = None
        for item in self.data:
            if str(item.get("SOURCE")).strip() == source:
                result = item.get("OSCAL_PART_IDENTIFIER")
                return result
        return result

    def find_sub_parts(self, source: str) -> List[str]:
        """
        Find a mapping by source.
        :param str source: The source.
        :return: A list of sub-parts.
        :rtype: List[str]
        """
        result = []
        for item in self.data:
            if str(item.get("SOURCE")).strip() == source:
                parts = item.get("SUB_PARTS", [])
                return parts
        return result

    def load_json_from_file(self, json_file: str):
        """
        Load json from a file
        :param str json_file: string name of a file
        """
        with open(json_file) as jf:
            parsed_json = json.load(jf)
        self.data = parsed_json

    def load_fedramp_version_5_mapping(self):
        """
        Load FedRAMP version 5 mapping
        """
        from importlib.resources import path as resource_path

        with resource_path("regscale.integrations.public.fedramp.mappings", "fedramp_r5_parts.json") as json_file_path:
            self.load_json_from_file(json_file_path.__str__())

    def load_fedramp_version_4_mapping(self):
        """
        Load FedRAMP version 4 mapping
        """
        from importlib.resources import path as resource_path

        with resource_path("regscale.integrations.public.fedramp.mappings", "fedramp_r4_parts.json") as json_file_path:
            self.load_json_from_file(json_file_path.__str__())

    def find_by_control_id_and_part_letter(self, control_label: str, part: str) -> list:
        """
        Find a mapping by control label and part letter.
        :param str control_label: The control label.
        :param str part: The part letter.
        :return: A list of mappings.
        :rtype: list
        """
        result = [
            item.get("OSCAL_PART_IDENTIFIER")
            for item in self.data
            if item.get("CONTROLLABEL") == control_label and item.get("Part") == part
        ]
        return result

    def find_by_oscal_control_id_and_part_letter(self, oscal_control_id: str, part: str) -> list:
        """
        Find a mapping by OSCAL control ID and part letter.
        :param str oscal_control_id:
        :param str part:
        :return: A list of mappings.
        :rtype: list
        """
        result = [
            item.get("OSCAL_PART_IDENTIFIER")
            for item in self.data
            if item.get("OSCALCONTROL_ID") == oscal_control_id and item.get("Part") == part
        ]
        return result
