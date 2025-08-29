# from dataclasses import dataclass
# from typing import Set, List, Dict
# import pyslang

# @dataclass
# class ParserContext:
#     module_name: str
#     file_path: str
#     parsed_instances: Set[str]
#     module_names: Set[str]
#     all_modules: List[Dict]
#     port_names: Set[str]
#     macros: Dict[str, str]

# @dataclass
# class ComponentParserContext:
#     file_path: str
#     source_text: str
#     port_names: Set[str]
#     module_name: str
#     all_modules: List[Dict]
#     syntax_tree: pyslang.SyntaxTree
#     parsed_instances: Set[str]
#     module_names: Set[str]
#     macros: Dict[str, str]







# tested3

# identifies counters, registers, muxes, and gates in both .v files (Verilog/SystemVerilog files) and .lib files (library files)


from dataclasses import dataclass
from typing import Dict, Set, List

@dataclass
class ParserContext:
    macros: Dict[str, str]
    parsed_instances: Set[str]
    module_names: Set[str]
    detailed_output: List[str]
    # Updated to use dictionary for lib_cells
    lib_cells: Dict[str, Dict[str, str]]

@dataclass
class ComponentParserContext:
    components: Dict[str, List[str]]
    connections: Dict[str, Dict]
    port_names: Set[str]