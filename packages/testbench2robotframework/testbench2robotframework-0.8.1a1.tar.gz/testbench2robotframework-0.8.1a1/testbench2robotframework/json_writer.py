import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path
from typing import Union

from .config import Configuration
from .log import logger
from .model import (
    ReferenceAssignment,
    TestCaseDetails,
    TestCaseSetDetails,
    TestCaseSetExecutionForImport,
    TestStructureTree,
)

TEST_STRUCTURE_TREE_FILE = "cycle_structure"


def write_test_structure_element(
    json_dir: str,
    test_structure_element: Union[TestStructureTree, TestCaseSetDetails, TestCaseDetails],
) -> None:
    if isinstance(test_structure_element, TestStructureTree):
        filepath = Path(json_dir) / Path(TEST_STRUCTURE_TREE_FILE + ".json")
    else:
        filepath = Path(json_dir) / Path(f"{test_structure_element.uniqueID}.json")
    with Path(filepath).open("w+", encoding="utf8") as output_file:
        json.dump(
            asdict(test_structure_element),
            output_file,
            indent=2,
            default=lambda o: o.value if isinstance(o, Enum) else str(o),
        )


def write_main_protocol(json_dir: str, main_protocol: list[TestCaseSetExecutionForImport]) -> None:
    protocol = [asdict(tcs) for tcs in main_protocol]
    filepath = Path(json_dir) / Path("protocol.json")
    with Path(filepath).open("w+", encoding="utf8") as output_file:
        json.dump(
            protocol,
            output_file,
            indent=2,
            default=lambda o: o.value if isinstance(o, Enum) else str(o),
        )


def write_references(json_dir: str, references: list[ReferenceAssignment]) -> None:
    filepath = Path(json_dir) / Path("references.json")
    with Path(filepath).open("w+", encoding="utf8") as output_file:
        json.dump(
            [asdict(ref) for ref in references],
            output_file,
            indent=2,
            default=lambda o: o.value if isinstance(o, Enum) else str(o),
        )


def write_default_config(config_file):
    with Path(config_file).open("w+", encoding="utf-8") as file:
        json.dump(
            Configuration.from_dict({}).__dict__,
            file,
            default=lambda o: o.__dict__,
            indent=2,
        )
        logger.warning(f"Default Configuration generated to {config_file}")
