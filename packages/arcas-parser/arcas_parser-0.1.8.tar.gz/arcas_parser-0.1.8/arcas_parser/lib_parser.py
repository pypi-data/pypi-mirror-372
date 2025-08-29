# import re
# import logging
# from typing import Dict, Set, List

# def parse_lib_file(lib_file: str) -> Dict[str, Dict[str, str]]:
#     """
#     Parse a Verilog .lib file to extract standard cell names and their types.
#     Returns a dictionary mapping cell names to their type and ports, e.g.,
#     {'SDK_AND2_D0': {'type': 'gate', 'inputs': ['A', 'B'], 'outputs': ['Y']}, ...}
#     """
#     lib_cells = {}
#     try:
#         if not lib_file or not lib_file.endswith('.lib'):
#             logging.info("No valid .lib file provided, skipping parsing")
#             return lib_cells
#         with open(lib_file, 'r', encoding='utf-8') as f:
#             content = f.read()
        
#         # Match Verilog module declarations, e.g., module SDK_AND2_D0 (input A, input B, output Y);
#         module_pattern = re.compile(r'module\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
#         for match in module_pattern.finditer(content):
#             cell_name = match.group(1)
#             ports_str = match.group(2).replace('\n', ' ').strip()
            
#             # Extract ports (e.g., input A, input B, output Y)
#             inputs = []
#             outputs = []
#             inouts = []
#             port_decls = re.findall(r'(input|output|inout)\s+((?:reg\s+)?[\w\s,]+)(?=\s*,|\s*$)', ports_str)
#             for direction, port_list in port_decls:
#                 ports = [p.strip() for p in port_list.replace('reg', '').split(',') if p.strip()]
#                 if direction == 'input':
#                     inputs.extend(ports)
#                 elif direction == 'output':
#                     outputs.extend(ports)
#                 elif direction == 'inout':
#                     inouts.extend(ports)
            
#             # Classify cell type based on naming convention
#             cell_type = 'other'
#             if 'DFF' in cell_name or 'SFF' in cell_name:
#                 cell_type = 'flip_flop'
#             elif any(g in cell_name for g in ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR', 'INV', 'BUF']):
#                 cell_type = 'gate'
#             elif 'MUX' in cell_name or 'AOI' in cell_name or 'OAI' in cell_name or 'OIA' in cell_name:
#                 cell_type = 'mux'
#             elif 'TRAN' in cell_name or 'PULLUP' in cell_name or 'PULLDOWN' in cell_name:
#                 cell_type = 'switch'
            
#             lib_cells[cell_name] = {
#                 'type': cell_type,
#                 'inputs': inputs,
#                 'outputs': outputs,
#                 'inouts': inouts
#             }
#             logging.debug(f"Parsed standard cell: {cell_name} (type={cell_type}, inputs={inputs}, outputs={outputs}, inouts={inouts})")
        
#         logging.info(f"Parsed {len(lib_cells)} standard cells from {lib_file}")
#         return lib_cells
#     except Exception as e:
#         logging.error(f"Error parsing .lib file {lib_file}: {e}")
#         return lib_cells






# import logging
# import re

# def parse_lib_file(lib_file):
#     try:
#         logging.debug(f"Parsing library file: {lib_file}")
#         cells = {}
#         with open(lib_file, 'r', encoding='utf-8') as f:
#             content = f.read()
#         cell_pattern = re.compile(r'module\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
#         for match in cell_pattern.finditer(content):
#             cell_name = match.group(1)
#             port_list = match.group(2)
#             cell_type = 'unknown'
#             inputs = []
#             outputs = []
#             inouts = []
#             # Parse ports
#             ports = [p.strip() for p in port_list.split(',')]
#             for port in ports:
#                 port = port.strip()
#                 if port.startswith('input'):
#                     inputs.append(port.replace('input', '').strip())
#                 elif port.startswith('output'):
#                     outputs.append(port.replace('output', '').strip())
#                 elif port.startswith('inout'):
#                     inouts.append(port.replace('inout', '').strip())
#             # Determine cell type
#             if 'DFF' in cell_name or 'SFF' in cell_name:
#                 cell_type = 'flip_flop'
#             elif 'MUX' in cell_name:
#                 cell_type = 'mux'
#             elif 'TRAN' in cell_name or 'PULLUP' in cell_name or 'PULLDOWN' in cell_name:
#                 cell_type = 'switch'
#             else:
#                 cell_type = 'gate'
#             cells[cell_name] = {
#                 'type': cell_type,
#                 'inputs': inputs,
#                 'outputs': outputs,
#                 'inouts': inouts
#             }
#             logging.debug(f"Parsed standard cell: {cell_name} (type={cell_type}, inputs={inputs}, outputs={outputs}, inouts={inouts})")
#         logging.info(f"Parsed {len(cells)} cells from {lib_file}")
#         # Flush logs
#         for handler in logging.getLogger('').handlers:
#             handler.flush()
#         return cells
#     except Exception as e:
#         logging.error(f"Failed to parse library file {lib_file}: {e}")
#         return {}









import re
import logging
from typing import Dict, Set, List

def parse_lib_file(lib_file: str) -> Dict[str, Dict[str, any]]:
    """
    Parse a Verilog .lib file to extract standard cell names, types, and ports.
    Returns a dictionary mapping cell names to their type and ports, e.g.,
    {'SDK_AND2_D0': {'type': 'gate', 'inputs': ['A', 'B'], 'outputs': ['Y']}, ...}
    """
    lib_cells = {}
    try:
        if not lib_file or not lib_file.endswith('.lib'):
            logging.info("No valid .lib file provided, skipping parsing")
            return lib_cells
        with open(lib_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match Verilog module declarations
        module_pattern = re.compile(r'module\s+(\w+)\s*\((.*?)\)\s*;(.*?)(?:endmodule|primitive)', re.DOTALL | re.MULTILINE)
        for match in module_pattern.finditer(content):
            cell_name = match.group(1)
            ports_str = match.group(2).replace('\n', ' ').strip()
            cell_body = match.group(3).strip()
            
            # Extract ports
            inputs = []
            outputs = []
            inouts = []
            port_decls = re.findall(r'(input|output|inout)\s+((?:reg\s+)?[\w\s,]+)(?=\s*,|\s*$)', ports_str)
            for direction, port_list in port_decls:
                ports = [p.strip() for p in port_list.replace('reg', '').split(',') if p.strip()]
                if direction == 'input':
                    inputs.extend(ports)
                elif direction == 'output':
                    outputs.extend(ports)
                elif direction == 'inout':
                    inouts.extend(ports)
            
            # Classify cell type
            cell_type = 'other'
            if 'DFF' in cell_name or 'SFF' in cell_name:
                cell_type = 'flip_flop'
            elif any(g in cell_name for g in ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR', 'INV', 'BUF']):
                cell_type = 'gate'
            elif 'MUX' in cell_name or 'AOI' in cell_name or 'OAI' in cell_name or 'OIA' in cell_name:
                cell_type = 'mux'
            elif 'TRAN' in cell_name or 'PULLUP' in cell_name or 'PULLDOWN' in cell_name:
                cell_type = 'switch'
            elif re.search(r'\breg\b', cell_body):  # Detect registers in cell body
                cell_type = 'register'
            elif re.search(r'\+\s*1\b', cell_body):  # Detect counter-like behavior
                cell_type = 'counter'
            
            lib_cells[cell_name] = {
                'type': cell_type,
                'inputs': inputs,
                'outputs': outputs,
                'inouts': inouts,
                'body': cell_body  # Store body for further analysis if needed
            }
            logging.debug(f"Parsed standard cell: {cell_name} (type={cell_type}, inputs={inputs}, outputs={outputs}, inouts={inouts})")
        
        logging.info(f"Parsed {len(lib_cells)} standard cells from {lib_file}")
        return lib_cells
    except Exception as e:
        logging.error(f"Error parsing .lib file {lib_file}: {e}")
        return lib_cells


# import re
# import logging
# from typing import Dict, Set, List

# def parse_lib_file(lib_file: str) -> Dict[str, Dict[str, any]]:
#     """
#     Parse a Verilog .lib file to extract standard cell names, types, and ports.
#     Returns a dictionary mapping cell names to their type and ports, e.g.,
#     {'SDK_AND2_D0': {'type': 'gate', 'inputs': ['A', 'B'], 'outputs': ['Y']}, ...}
#     """
#     lib_cells = {}
#     try:
#         if not lib_file or not lib_file.endswith('.lib'):
#             logging.info("No valid .lib file provided, skipping parsing")
#             return lib_cells
#         with open(lib_file, 'r', encoding='utf-8') as f:
#             content = f.read()
        
#         # Match Verilog module declarations
#         module_pattern = re.compile(r'module\s+(\w+)\s*\((.*?)\)\s*;(.*?)(?:endmodule|primitive)', re.DOTALL | re.MULTILINE)
#         for match in module_pattern.finditer(content):
#             cell_name = match.group(1)
#             ports_str = match.group(2).replace('\n', ' ').strip()
#             cell_body = match.group(3).strip()
            
#             # Extract ports
#             inputs = []
#             outputs = []
#             inouts = []
#             port_decls = re.findall(r'(input|output|inout)\s+((?:reg\s+)?[\w\s,]+)(?=\s*,|\s*$)', ports_str)
#             for direction, port_list in port_decls:
#                 ports = [p.strip() for p in port_list.replace('reg', '').split(',') if p.strip()]
#                 if direction == 'input':
#                     inputs.extend(ports)
#                 elif direction == 'output':
#                     outputs.extend(ports)
#                 elif direction == 'inout':
#                     inouts.extend(ports)
            
#             # Classify cell type
#             cell_type = 'other'
#             if 'DFF' in cell_name or 'SFF' in cell_name:
#                 cell_type = 'flip_flop'
#             elif any(g in cell_name for g in ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR', 'INV', 'BUF']):
#                 cell_type = 'gate'
#             elif 'MUX' in cell_name or 'AOI' in cell_name or 'OAI' in cell_name or 'OIA' in cell_name:
#                 cell_type = 'mux'
#             elif 'TRAN' in cell_name or 'PULLUP' in cell_name or 'PULLDOWN' in cell_name:
#                 cell_type = 'switch'
#             elif re.search(r'\breg\b', cell_body):  # Detect registers in cell body
#                 cell_type = 'register'
#             elif re.search(r'\+\s*1\b', cell_body):  # Detect counter-like behavior
#                 cell_type = 'counter'
            
#             lib_cells[cell_name] = {
#                 'type': cell_type,
#                 'inputs': inputs,
#                 'outputs': outputs,
#                 'inouts': inouts,
#                 'body': cell_body  # Store body for further analysis if needed
#             }
#             logging.debug(f"Parsed standard cell: {cell_name} (type={cell_type}, inputs={inputs}, outputs={outputs}, inouts={inouts})")
        
#         logging.info(f"Parsed {len(lib_cells)} standard cells from {lib_file}")
#         return lib_cells
#     except Exception as e:
#         logging.error(f"Error parsing .lib file {lib_file}: {e}")
#         return lib_cells