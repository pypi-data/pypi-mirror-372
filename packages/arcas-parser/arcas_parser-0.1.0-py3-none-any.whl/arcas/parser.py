# import re
# import logging
# import pyslang
# import os
# from uuid import uuid4
# from utility import detect_counter
# from ContextClasses import ParserContext, ComponentParserContext
# from typing import Dict, Set, Tuple, List

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     if included_files is None:
#         included_files = set()
#     try:
#         if file_path in included_files:
#             logging.warning(f"Skipping recursive include of {file_path}")
#             return source_text
#         included_files.add(file_path)
#         include_pattern = re.compile(r'`include\s+"([^"]+)"')
#         while include_pattern.search(source_text):
#             for match in include_pattern.finditer(source_text):
#                 include_file = match.group(1)
#                 include_path = os.path.join(os.path.dirname(file_path), include_file)
#                 logging.debug(f"Processing include: {include_file} -> {include_path}")
#                 try:
#                     with open(include_path, 'r', encoding='utf-8') as inc_file:
#                         include_content = inc_file.read()
#                     include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                     source_text = source_text.replace(match.group(0), include_content)
#                 except FileNotFoundError:
#                     logging.error(f"Include file not found: {include_path}")
#                     return source_text
#                 except Exception as e:
#                     logging.error(f"Error processing include {include_file}: {e}")
#                     return source_text
#         for macro_name, macro_value in macros.items():
#             macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#             def replace_macro(match):
#                 suffix = match.group(1)
#                 if suffix.startswith('-'):
#                     try:
#                         return str(int(macro_value) + int(suffix))
#                     except ValueError:
#                         return match.group(0)
#                 return str(macro_value)
#             source_text = macro_pattern.sub(replace_macro, source_text)
#             logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#         return source_text
#     except Exception as e:
#         logging.error(f"Error preprocessing {file_path}: {e}")
#         return source_text

# def get_port_width(port, macros: Dict[str, str]) -> str:
#     try:
#         if port is None:
#             return "1"
#         # Handle explicit dimensions
#         if hasattr(port, 'dimensions') and len(port.dimensions) > 0:
#             dim = port.dimensions[0]
#             msb = str(dim.msb.valueText) if hasattr(dim.msb, 'valueText') else str(dim.msb)
#             lsb = str(dim.lsb.valueText) if hasattr(dim.lsb, 'valueText') else str(dim.lsb)
#             if msb in macros:
#                 msb = str(macros[msb])
#             if lsb in macros:
#                 lsb = str(macros[lsb])
#             try:
#                 msb, lsb = int(msb), int(lsb)
#                 return f"[{msb}:{lsb}]"
#             except ValueError:
#                 logging.warning(f"Non-integer dimension in port: msb={msb}, lsb={lsb}")
#         # Handle type-based width
#         if hasattr(port, 'type') and port.type:
#             type_str = str(port.type)
#             match = re.search(r'\[(\d+|`?\w+):(\d+|`?\w+)\]', type_str)
#             if match:
#                 msb, lsb = match.groups()
#                 if msb.startswith('`'):
#                     msb = macros.get(msb[1:], msb)
#                 if lsb.startswith('`'):
#                     lsb = macros.get(lsb[1:], lsb)
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer type dimension: msb={msb}, lsb={lsb}")
#         # Fallback to text-based analysis
#         if hasattr(port, 'getText'):
#             text = port.getText()
#             match = re.search(r'\[(\w+|\d+):(\w+|\d+)\]', text)
#             if match:
#                 msb, lsb = match.groups()
#                 if msb in macros:
#                     msb = str(macros[msb])
#                 if lsb in macros:
#                     lsb = str(macros[lsb])
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer text dimension: msb={msb}, lsb={lsb}")
#         # Check port name for specific widths
#         port_name = getattr(port, 'name', None)
#         port_name = port_name.valueText if port_name and hasattr(port_name, 'valueText') else ''
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[6:0]"
#         if any(macro in port_name for macro in macros):
#             for macro_name, macro_value in macros.items():
#                 if macro_name in port_name:
#                     try:
#                         width = int(macro_value) - 1
#                         return f"[{width}:0]"
#                     except ValueError:
#                         pass
#         # Default to 1 for control signals
#         if port_name in ('clk_i', 'rst_i', 'we1', 'we2', 're1', 're2', 'wb_ack_o', 'wb_err_o', 'rf_we', 'o3_we', 'o4_we', 'o6_we', 'o7_we', 'o8_we', 'o9_we', 'i3_re', 'i4_re', 'i6_re'):
#             return "1"
#         return "1"
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_name}: {e}")
#         return "1"

# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     ports = []
#     port_names = set()
#     try:
#         # Handle ANSI-style ports
#         if hasattr(member, 'header') and hasattr(member.header, 'ports') and member.header.ports:
#             for port in member.header.ports:
#                 name = getattr(port, 'name', None) or getattr(getattr(port, 'declarator', None), 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     direction = "unknown"
#                     if hasattr(port, 'direction'):
#                         direction = str(port.direction).lower().split()[0]
#                     elif hasattr(getattr(port, 'header', None), 'direction'):
#                         direction = str(port.header.direction).lower().split()[0]
#                     data_type = str(getattr(port, 'type', '') or getattr(port.header, 'dataType', '') or 'wire').strip()
#                     width = get_port_width(port, macros)
#                     ports.append(f"{name}: {direction} {data_type} {width}")
#                     port_names.add(name)
#                     logging.debug(f"Parsed ANSI port: {name} ({direction} {data_type} {width})")
#         # Handle non-ANSI-style ports
#         for sub_member in member.members:
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 name = getattr(sub_member, 'name', None) or getattr(getattr(sub_member, 'declarator', None), 'name', None)
#                 if name and hasattr(name, 'valueText') and name.valueText not in port_names:
#                     name = name.valueText
#                     direction = str(getattr(sub_member, 'direction', 'input')).lower().split()[0]
#                     data_type = str(getattr(sub_member, 'type', 'wire')).strip()
#                     width = get_port_width(sub_member, macros)
#                     ports.append(f"{name}: {direction} {data_type} {width}")
#                     port_names.add(name)
#                     logging.debug(f"Parsed non-ANSI port: {name} ({direction} {data_type} {width})")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText') and name.valueText not in port_names:
#                         name = name.valueText
#                         direction = 'input' if name in ('clk_i', 'rst_i', 'wb_cyc_i', 'wb_stb_i', 'wb_we_i', 'wb_data_i', 'wb_addr_i', 'sdata_pad_i') else 'output'
#                         data_type = 'wire'
#                         width = get_port_width(sub_member, macros)
#                         ports.append(f"{name}: {direction} {data_type} {width}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed net port: {name} ({direction} {data_type} {width})")
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText') and name.valueText not in port_names:
#                         name = name.valueText
#                         data_type = str(sub_member.type).strip().lower()
#                         if 'reg' in data_type:
#                             direction = 'output'
#                             width = get_port_width(sub_member, macros)
#                             ports.append(f"{name}: {direction} reg {width}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed reg port: {name} ({direction} reg {width})")
#     except Exception as e:
#         logging.error(f"Error parsing ports for module: {e}")
#     return sorted(ports), port_names

# def process_instantiation(sub_member, loop_vars: Dict[str, str], context: ParserContext, global_connections: Dict[str, Dict]):
#     instances = []
#     connections = {}
#     try:
#         inst_type = getattr(sub_member.type, 'name', None)
#         inst_type = inst_type.valueText if inst_type and hasattr(inst_type, 'valueText') else str(sub_member.type).strip().split()[-1]
#         if inst_type not in context.module_names:
#             logging.debug(f"Instance type {inst_type} not found in module list for {context.module_name}")
#             return instances, connections
#         for inst in sub_member.instances:
#             inst_name = getattr(inst, 'name', None)
#             inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"unknown_{uuid4().hex[:8]}"
#             for var, val in loop_vars.items():
#                 inst_name = inst_name.replace(var, val)
#             inst_key = f"{context.file_path}:{inst_type}_{inst_name}"
#             if inst_key in context.parsed_instances:
#                 continue
#             context.parsed_instances.add(inst_key)
#             port_connections = []
#             for conn in getattr(inst, 'connections', []):
#                 port_name = getattr(conn, 'name', None)
#                 signal = str(conn.expr).strip() if hasattr(conn, 'expr') else None
#                 if port_name and signal and hasattr(port_name, 'valueText'):
#                     port_name = port_name.valueText
#                     for var, val in loop_vars.items():
#                         signal = signal.replace(var, val)
#                     port_connections.append((port_name, signal))
#                     base_signal = signal.split('[')[0]
#                     inst_module_ports = [p for m in context.all_modules if m["name"] == inst_type for p in m["ports"]]
#                     width = get_port_width(None, context.macros)
#                     for p in inst_module_ports:
#                         if port_name in p and ('[' in p or any(m in p for m in context.macros)):
#                             match = re.search(r'\[(\d+):(\d+)\]', p)
#                             if match:
#                                 width = f"[{match.group(1)}:{match.group(2)}]"
#                             break
#                     is_input = any("input" in p and port_name in p for p in inst_module_ports)
#                     is_output = any("output" in p and port_name in p for p in inst_module_ports)
#                     global_connections["wires"].setdefault(base_signal, {"source": None, "sinks": [], "type": width})
#                     if is_input:
#                         global_connections["wires"][base_signal]["sinks"].append(f"{inst_type} instance ({inst_name}.{port_name})")
#                         if base_signal in context.port_names:
#                             global_connections["wires"][base_signal]["source"] = f"top-level port ({base_signal})"
#                     elif is_output:
#                         global_connections["wires"][base_signal]["source"] = f"{inst_type} instance ({inst_name}.{port_name})"
#                         if base_signal in context.port_names:
#                             global_connections["wires"][base_signal]["sinks"].append(f"top-level port ({base_signal})")
#             instances.append(f"{inst_type} instance: {inst_name}, ports={', '.join(f'{p}={s}' for p,s in port_connections)}")
#             connections[inst_name] = {"module": inst_type, "ports": dict(port_connections)}
#             logging.debug(f"Parsed instance: {inst_type} {inst_name}, ports={port_connections}")
#     except AttributeError as e:
#         logging.error(f"Error processing instantiation in {context.module_name}: {e}")
#     return instances, connections

# def parse_blocks_wise(member, context: ComponentParserContext, global_connections: Dict[str, Dict]):
#     instances = []
#     connections = {}
#     def traverse_generate_block(gen_block, loop_vars=None):
#         nonlocal instances, connections
#         loop_vars = loop_vars or {}
#         for sub_member in gen_block.members:
#             if sub_member.kind == pyslang.SyntaxKind.GenerateBlock:
#                 traverse_generate_block(sub_member, loop_vars)
#             elif sub_member.kind == pyslang.SyntaxKind.LoopGenerate:
#                 loop_var = getattr(sub_member.loopVar, 'name', None)
#                 if not loop_var:
#                     logging.debug(f"Skipping loop generate with no loop variable in {context.module_name}")
#                     continue
#                 loop_var = loop_var.valueText
#                 try:
#                     start = int(str(sub_member.initialExpr).strip().split(':')[-1] or 0)
#                     stop = int(str(sub_member.stopExpr).strip().split(':')[0] or context.macros.get('DEPTH', 1))
#                     step = int(str(sub_member.stepExpr).strip() or 1)
#                     gen_range = range(start, stop, step) if start < stop else range(start, stop - 1, -step)
#                     for i in gen_range:
#                         new_loop_vars = loop_vars | {loop_var: str(i)}
#                         if hasattr(sub_member, 'block'):
#                             traverse_generate_block(sub_member.block, new_loop_vars)
#                 except (ValueError, AttributeError) as e:
#                     logging.error(f"Error processing loop generate in {context.module_name}: {e}")
#             elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
#                 inst_context = ComponentParserContext(
#                     file_path=context.file_path,
#                     source_text=context.source_text,
#                     port_names=context.port_names,
#                     module_name=context.module_name,
#                     all_modules=context.all_modules,
#                     syntax_tree=context.syntax_tree,
#                     parsed_instances=context.parsed_instances,
#                     module_names=context.module_names,
#                     macros=context.macros
#                 )
#                 insts, conns = process_instantiation(sub_member, loop_vars, inst_context, global_connections)
#                 instances.extend(insts)
#                 connections.update(conns)
#     for sub_member in member.members:
#         if sub_member.kind in [pyslang.SyntaxKind.GenerateBlock, pyslang.SyntaxKind.LoopGenerate]:
#             traverse_generate_block(sub_member)
#         elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
#             inst_context = ComponentParserContext(
#                 file_path=context.file_path,
#                 source_text=context.source_text,
#                 port_names=context.port_names,
#                 module_name=context.module_name,
#                 all_modules=context.all_modules,
#                 syntax_tree=context.syntax_tree,
#                 parsed_instances=context.parsed_instances,
#                 module_names=context.module_names,
#                 macros=context.macros
#             )
#             insts, conns = process_instantiation(sub_member, {}, inst_context, global_connections)
#             instances.extend(insts)
#             connections.update(conns)
#     return instances, connections

# def parse_components(context: ComponentParserContext):
#     components = {"gates": [], "flip_flops": [], "wires": [], "registers": [], "counters": [], "instances": [], "muxes": []}
#     connections = {"wires": {}, "registers": {}, "gates": {}, "flip_flops": {}, "instances": {}, "muxes": {}}
#     connectivity_report = []
#     module_connectivity = []
#     unconnected_wires = []
#     unused_gates = []
#     parsed_ff_outputs = set()
#     parsed_gates = set()
#     parsed_muxes = set()
#     parsed_registers = set()
#     macros = context.macros

#     logging.debug(f"Starting component parsing for {context.module_name}")
#     # Find the module declaration
#     module_member = None
#     for member in context.syntax_tree.root.members:
#         if member.kind == pyslang.SyntaxKind.ModuleDeclaration and getattr(member.header, 'name', None) and member.header.name.valueText == context.module_name:
#             module_member = member
#             break
#     if not module_member:
#         logging.error(f"Module {context.module_name} not found in syntax tree for {context.file_path}")
#         return components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates

#     logging.debug(f"Parsing components for module: {context.module_name}")
#     logging.debug(f"Syntax tree members for {context.module_name}: {[str(m.kind) for m in module_member.members]}")

#     # Wires
#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#             for declarator in getattr(sub_member, 'declarators', []):
#                 name = getattr(declarator, 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     width = get_port_width(sub_member, macros)
#                     components["wires"].append(f"{name}: wire {width}")
#                     connections["wires"][name] = {"source": None, "sinks": [], "type": width}
#                     connectivity_report.append(f"Wire {name} ({width}): source={None}, sinks=none")
#                     logging.debug(f"Detected wire: {name} ({width})")

#     # Registers and counters
#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#             data_type = str(sub_member.type).strip().lower()
#             if "integer" in data_type:
#                 logging.debug(f"Skipping integer declaration: {str(sub_member)}")
#                 continue
#             for declarator in getattr(sub_member, 'declarators', []) or []:
#                 name = getattr(declarator, 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     if name in parsed_registers:
#                         logging.debug(f"Skipping duplicate register: {name}")
#                         continue
#                     parsed_registers.add(name)
#                     width = get_port_width(sub_member, macros)
#                     is_array = bool(getattr(declarator, 'dimensions', None) or '[' in str(sub_member))
#                     if is_array:
#                         dim_str = f"0:{macros.get('DEPTH', 1)-1}"
#                         width = f"{width} [{dim_str}]"
#                     if "reg" in data_type:
#                         if detect_counter(name, context.source_text):
#                             components["counters"].append(f"{name}: counter {width}")
#                             connections["registers"][name] = {"source": "counter_logic", "sinks": []}
#                             logging.debug(f"Detected counter: {name} ({width})")
#                         else:
#                             display_type = f"reg array {width}" if is_array else f"reg {width}"
#                             components["registers"].append(f"{name}: {display_type}")
#                             connections["registers"][name] = {"source": None, "sinks": []}
#                             logging.debug(f"Detected register: {name} ({display_type})")
#             for port in context.port_names:
#                 for port_desc in [p for m in context.all_modules if m["name"] == context.module_name for p in m["ports"]]:
#                     if port in port_desc and "reg" in port_desc.lower() and port not in parsed_registers:
#                         width = get_port_width(sub_member, macros)
#                         components["registers"].append(f"{port}: reg {width}")
#                         connections["registers"][port] = {"source": None, "sinks": []}
#                         parsed_registers.add(port)
#                         logging.debug(f"Detected output reg port: {port} ({width})")

#     # Instances
#     inst_list, inst_connections = parse_blocks_wise(module_member, context, connections)
#     components["instances"].extend(inst_list)
#     connections["instances"].update(inst_connections)
#     for inst_name, inst_conn in inst_connections.items():
#         for port_name, signal in inst_conn["ports"].items():
#             base_signal = signal.split('[')[0]
#             if base_signal in context.port_names:
#                 module_connectivity.append(f"{inst_conn['module']} instance ({inst_name}.{port_name}) -> top-level port ({signal})")
#             inst_module_ports = [p for m in context.all_modules if m["name"] == inst_conn["module"] for p in m["ports"]]
#             width = get_port_width(None, macros)
#             for p in inst_module_ports:
#                 if port_name in p and ('[' in p or any(m in p for m in macros)):
#                     match = re.search(r'\[(\d+):(\d+)\]', p)
#                     if match:
#                         width = f"[{match.group(1)}:{match.group(2)}]"
#                     break
#             is_input = any("input" in p and port_name in p for p in inst_module_ports)
#             is_output = any("output" in p and port_name in p for p in inst_module_ports)
#             connections["wires"].setdefault(base_signal, {"source": None, "sinks": [], "type": width})
#             if is_input:
#                 connections["wires"][base_signal]["sinks"].append(f"{inst_conn['module']} instance ({inst_name}.{port_name})")
#                 if base_signal in context.port_names:
#                     connections["wires"][base_signal]["source"] = f"top-level port ({base_signal})"
#             elif is_output:
#                 connections["wires"][base_signal]["source"] = f"{inst_conn['module']} instance ({inst_name}.{port_name})"
#                 if base_signal in context.port_names:
#                     connections["wires"][base_signal]["sinks"].append(f"top-level port ({base_signal})")
#             # Cross-instance connectivity
#             for other_inst_name, other_inst_conn in inst_connections.items():
#                 if other_inst_name != inst_name:
#                     for other_port_name, other_signal in other_inst_conn["ports"].items():
#                         if other_signal.split('[')[0] == base_signal:
#                             module_connectivity.append(f"{inst_conn['module']} instance ({inst_name}.{port_name}) -> {other_inst_conn['module']} instance ({other_inst_name}.{other_port_name})")

#     # Gates and Muxes
#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
#             assign_text = str(sub_member).strip()
#             if assign_text not in parsed_gates and assign_text not in parsed_muxes:
#                 match = re.match(r'assign\s+([\w\[\]:]+)\s*=\s*([^;]+);', assign_text)
#                 if match:
#                     output, input_expr = match.groups()
#                     gate_type = "MUX" if " ? " in input_expr else "assign"
#                     input_signals = []
#                     for sig in re.split(r'[\s,|&~^]+', input_expr):
#                         sig = sig.strip()
#                         if sig and not sig.startswith(('1\'b', '0\'b', '(', ')', '<', '5\'h')):
#                             sig_type = "register" if sig in connections["registers"] else "port" if sig in context.port_names else "wire"
#                             input_signals.append((sig, sig_type))
#                             if sig_type not in ("register", "port"):
#                                 connections["wires"].setdefault(sig, {"source": None, "sinks": [], "type": "1"})
#                                 connections["wires"][sig]["sinks"].append(f"{gate_type} gate ({output})")
#                     width = get_port_width(None, macros)
#                     components["gates" if gate_type == "assign" else "muxes"].append(f"{gate_type} gate: output={output}, inputs={', '.join(i[0] for i in input_signals) or 'none'}")
#                     connections["gates" if gate_type == "assign" else "muxes"][output] = {"type": gate_type, "inputs": input_signals, "drives": []}
#                     parsed_gates.add(assign_text) if gate_type == "assign" else parsed_muxes.add(assign_text)
#                     if output in connections["wires"]:
#                         connections["wires"][output]["source"] = f"{gate_type} gate ({output})"
#                     elif output in context.port_names:
#                         connections["gates" if gate_type == "assign" else "muxes"][output]["drives"].append(f"top-level port ({output})")
#                     else:
#                         connections["wires"][output] = {"source": f"{gate_type} gate ({output})", "sinks": [], "type": width}
#                     for input_signal, input_type in input_signals:
#                         base_signal = input_signal.split('[')[0]
#                         if base_signal in connections["registers"]:
#                             connections["registers"][base_signal]["sinks"].append(f"{gate_type} gate ({output})")
#                         elif base_signal in connections["wires"]:
#                             connections["wires"][base_signal]["sinks"].append(f"{gate_type} gate ({output})")
#                         elif base_signal in context.port_names:
#                             connections["wires"][base_signal] = {"source": f"top-level port ({base_signal})", "sinks": [f"{gate_type} gate ({output})"], "type": width}

#     # Flip-flops
#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
#             trigger = str(sub_member).split('@')[1].split(')')[0].strip() if '@' in str(sub_member) else ""
#             clock = trigger.split(" or ")[0].replace("posedge ", "") if "posedge" in trigger else "unknown"
#             reset = trigger.split(" or ")[1].replace("posedge ", "").replace("negedge ", "") if " or " in trigger else "none"
#             width = get_port_width(None, macros)
#             def traverse_statements(stmts, loop_vars=None):
#                 loop_vars = loop_vars or {}
#                 stmts = stmts if hasattr(stmts, '__iter__') else [stmts]
#                 for stmt in stmts:
#                     logging.debug(f"Statement kind: {stmt.kind}, text={str(stmt)[:200]}")
#                     if stmt.kind == pyslang.SyntaxKind.ForLoop:
#                         loop_var = getattr(stmt.loopVar, 'name', None).valueText if getattr(stmt.loopVar, 'name', None) else None
#                         if loop_var:
#                             try:
#                                 initial_expr = str(stmt.initialExpr).strip()
#                                 stop_expr = str(stmt.stopExpr).strip()
#                                 step_expr = str(stmt.stepExpr).strip() or "1"
#                                 start = int(initial_expr.split('=')[-1].strip()) if '=' in initial_expr else 0
#                                 stop = macros.get('DEPTH', 1) if 'DEPTH' in stop_expr or '< DEPTH' in stop_expr else int(stop_expr.split('<')[-1].strip().split(';')[0])
#                                 step = int(step_expr.split('=')[-1].strip()) if '=' in step_expr else 1
#                                 gen_range = range(start, stop, step)
#                                 logging.debug(f"For loop: var={loop_var}, start={start}, stop={stop}, step={step}")
#                                 for i in gen_range:
#                                     new_loop_vars = loop_vars | {loop_var: str(i)}
#                                     traverse_statements(getattr(stmt, 'stmts', []), new_loop_vars)
#                             except (ValueError, AttributeError) as e:
#                                 logging.error(f"Error processing for loop in {context.module_name}: {e}")
#                         else:
#                             logging.debug(f"Skipping for loop with no loop variable: {str(stmt)[:200]}")
#                     elif stmt.kind == pyslang.SyntaxKind.ConditionalStatement:
#                         for branch in getattr(stmt, 'branches', []) or []:
#                             traverse_statements(getattr(branch, 'stmts', []), loop_vars)
#                     elif stmt.kind == pyslang.SyntaxKind.BlockStatement:
#                         traverse_statements(getattr(stmt, 'stmts', []), loop_vars)
#                     elif stmt.kind == pyslang.SyntaxKind.TimedStatement:
#                         traverse_statements(getattr(stmt, 'stmt', []), loop_vars)
#                     elif stmt.kind == pyslang.SyntaxKind.ExpressionStatement and stmt.expr.kind == pyslang.SyntaxKind.NonblockingAssignment:
#                         output = str(stmt.expr.left).strip()
#                         input_signal = str(stmt.expr.right).strip()
#                         for var, val in loop_vars.items():
#                             output = output.replace(var, val)
#                             input_signal = input_signal.replace(var, val)
#                         if output and output not in parsed_ff_outputs and input_signal != "0":
#                             components["flip_flops"].append(f"D flip-flop: output={output}, input={input_signal}, clock={clock}, reset={reset}")
#                             connections["flip_flops"][output] = {"input": input_signal, "drives": [], "clock": clock, "reset": reset}
#                             parsed_ff_outputs.add(output)
#                             base_input = input_signal.split('[')[0]
#                             width = get_port_width(None, macros)
#                             if base_input in context.port_names:
#                                 for p in [p for m in context.all_modules if m["name"] == context.module_name for p in m["ports"]]:
#                                     if base_input in p and ('[' in p or any(m in p for m in context.macros)):
#                                         match = re.search(r'\[(\d+):(\d+)\]', p)
#                                         if match:
#                                             width = f"[{match.group(1)}:{match.group(2)}]"
#                                         break
#                             connections["wires"].setdefault(base_input, {"source": None, "sinks": [], "type": width})
#                             connections["wires"][base_input]["sinks"].append(f"D flip-flop ({output})")
#                             if base_input in context.port_names:
#                                 connections["wires"][base_input]["source"] = f"top-level port ({base_input})"
#                             if output.split('[')[0] in connections["registers"]:
#                                 connections["registers"][output.split('[')[0]]["source"] = f"D flip-flop ({output})"
#                             if output in context.port_names:
#                                 connections["wires"].setdefault(output, {"source": None, "sinks": [], "type": width})
#                                 connections["wires"][output]["source"] = f"D flip-flop ({output})"
#                                 connections["wires"][output]["sinks"].append(f"top-level port ({output})")
#                             logging.debug(f"Detected flip-flop: output={output}, input={input_signal}, clock={clock}, reset={reset}")
#             if hasattr(sub_member, 'statements') and sub_member.statements:
#                 traverse_statements(sub_member.statements, {})
#             if hasattr(sub_member, 'stmt') and sub_member.stmt:
#                 traverse_statements(sub_member.stmt, {})
#             # Enhanced text-based fallback
#             always_pattern = re.compile(r'always\s*@\s*\(\s*(posedge\s+\w+|negedge\s+\w+)\s*(?:or\s+(?:posedge|negedge)\s+\w+\s*)?\)\s*begin([\s\S]*?)end', re.MULTILINE | re.DOTALL)
#             assign_pattern = re.compile(r'(\w+(?:\[\d+\])?)\s*<=\s*([^;]+);', re.MULTILINE)
#             for match in always_pattern.finditer(context.source_text):
#                 trigger = match.group(1)
#                 clock = trigger.replace("posedge ", "").replace("negedge ", "") if trigger else "unknown"
#                 reset = match.group(2).split(" or ")[1].replace("posedge ", "").replace("negedge ", "") if " or " in match.group(0) else "none"
#                 block = match.group(2)
#                 for assign in assign_pattern.finditer(block):
#                     output = assign.group(1)
#                     input_signal = assign.group(2).strip()
#                     if output and output not in parsed_ff_outputs and input_signal != "0":
#                         components["flip_flops"].append(f"D flip-flop: output={output}, input={input_signal}, clock={clock}, reset={reset}")
#                         connections["flip_flops"][output] = {"input": input_signal, "drives": [], "clock": clock, "reset": reset}
#                         parsed_ff_outputs.add(output)
#                         base_input = input_signal.split('[')[0]
#                         width = get_port_width(None, macros)
#                         if base_input in context.port_names:
#                             for p in [p for m in context.all_modules if m["name"] == context.module_name for p in m["ports"]]:
#                                 if base_input in p and ('[' in p or any(m in p for m in context.macros)):
#                                     match = re.search(r'\[(\d+):(\d+)\]', p)
#                                     if match:
#                                         width = f"[{match.group(1)}:{match.group(2)}]"
#                                         break
#                         connections["wires"].setdefault(base_input, {"source": None, "sinks": [], "type": width})
#                         connections["wires"][base_input]["sinks"].append(f"D flip-flop ({output})")
#                         if base_input in context.port_names:
#                             connections["wires"][base_input]["source"] = f"top-level port ({base_input})"
#                         if output.split('[')[0] in connections["registers"]:
#                             connections["registers"][output.split('[')[0]]["source"] = f"D flip-flop ({output})"
#                         if output in context.port_names:
#                             connections["wires"].setdefault(output, {"source": None, "sinks": [], "type": width})
#                             connections["wires"][output]["source"] = f"D flip-flop ({output})"
#                             connections["wires"][output]["sinks"].append(f"top-level port ({output})")
#                         logging.debug(f"Text-based flip-flop: output={output}, input={input_signal}, clock={clock}, reset={reset}")

#     # Enhanced connectivity
#     for ff_output, ff_conn in connections["flip_flops"].items():
#         base_ff_output = ff_output.split('[')[0]
#         for inst_name, inst_conn in connections["instances"].items():
#             for port_name, signal in inst_conn["ports"].items():
#                 if signal.split('[')[0] == base_ff_output:
#                     ff_conn["drives"].append(f"{inst_conn['module']} instance ({inst_name}.{port_name})")
#         for gate_output, gate_conn in connections["gates"].items():
#             for input_signal, _ in gate_conn["inputs"]:
#                 if input_signal.split('[')[0] == base_ff_output:
#                     ff_conn["drives"].append(f"{gate_conn['type']} gate ({gate_output})")
#                     gate_conn["drives"].append(f"D flip-flop ({ff_output})")
#         for wire, conn in connections["wires"].items():
#             if conn["source"] and conn["source"].startswith("D flip-flop") and wire == base_ff_output:
#                 conn["sinks"].extend(ff_conn["drives"])

#     for wire, conn in connections["wires"].items():
#         for gate_output, gate_conn in connections["gates"].items():
#             for input_signal, _ in gate_conn["inputs"]:
#                 if input_signal.split('[')[0] == wire:
#                     conn["sinks"].append(f"{gate_conn['type']} gate ({gate_output})")
#         for inst_name, inst_conn in connections["instances"].items():
#             for port_name, signal in inst_conn["ports"].items():
#                 if signal.split('[')[0] == wire:
#                     for mod in context.all_modules:
#                         if mod["name"] == inst_conn["module"]:
#                             for port_desc in mod["ports"]:
#                                 if port_name in port_desc and "input" in port_desc:
#                                     conn["sinks"].append(f"{inst_conn['module']} instance ({inst_name}.{port_name})")
#                                 elif port_name in port_desc and "output" in port_desc:
#                                     conn["source"] = f"{inst_conn['module']} instance ({inst_name}.{port_name})"
#         if not conn["source"] and not conn["sinks"]:
#             unconnected_wires.append(wire)
#         connectivity_report.append(f"Wire {wire} ({conn['type']}): source={conn['source'] or 'unconnected'}, sinks={', '.join(set(conn['sinks'])) or 'none'}")

#     for gate_output, gate_conn in connections["gates"].items():
#         if not gate_conn["drives"]:
#             for wire, conn in connections["wires"].items():
#                 if conn["source"] == f"{gate_conn['type']} gate ({gate_output})" and conn["sinks"]:
#                     gate_conn["drives"] = conn["sinks"]
#                 elif gate_output.split('[')[0] == wire:
#                     gate_conn["drives"].extend(conn["sinks"])
#             if not gate_conn["drives"]:
#                 unused_gates.append(gate_output)
#             connectivity_report.append(f"{gate_conn['type']} gate ({gate_output}): inputs={', '.join(f'{sig} ({t})' for sig, t in gate_conn['inputs'] or []) or 'none'}, drives={', '.join(set(gate_conn['drives'])) or 'none'}")

#     for mux_output, mux_conn in connections["muxes"].items():
#         if not mux_conn["drives"]:
#             for wire, conn in connections["wires"].items():
#                 if conn["source"] == f"{mux_conn['type']} gate ({mux_output})" and conn["sinks"]:
#                     mux_conn["drives"] = conn["sinks"]
#                 elif mux_output.split('[')[0] == wire:
#                     mux_conn["drives"].extend(conn["sinks"])
#             if not mux_conn["drives"]:
#                 unused_gates.append(mux_output)
#             connectivity_report.append(f"{mux_conn['type']} gate ({mux_output}): inputs={', '.join(f'{sig} ({t})' for sig, t in mux_conn['inputs']) or 'none'}, drives={', '.join(set(mux_conn['drives'])) or 'none'}")

#     return components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output):
#     detailed_output.append(f"\nProcessing {file_path}")
#     modules_processed = 0
#     modules_data = []

#     for member in syntax_tree.root.members:
#         if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#             module_name = getattr(member.header, 'name', None)
#             if module_name is None or not hasattr(module_name, 'valueText'):
#                 logging.warning(f"Skipping module with no name or invalid name token in {file_path}: {getattr(member.header, 'name', 'None')}")
#                 continue
#             module_name = module_name.valueText
#             if module_name not in [m["name"] for m in all_modules]:
#                 logging.warning(f"Skipping module {module_name} in {file_path}: not found in all_modules list")
#                 continue
#             detailed_output.append(f"  Module: {module_name}")

#             ports, port_names = parse_module_ports(member, macros)
#             detailed_output.append("  Ports:")
#             for port_def in ports or ["(none)"]:
#                 detailed_output.append(f"    - {port_def}")

#             detailed_output.append("  Components:")
#             context = ComponentParserContext(
#                 file_path=file_path,
#                 source_text=source_text,
#                 port_names=port_names,
#                 module_name=module_name,
#                 all_modules=all_modules,
#                 syntax_tree=syntax_tree,
#                 parsed_instances=parsed_instances,
#                 module_names=module_names,
#                 macros=macros
#             )
#             try:
#                 components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates = parse_components(context)
#             except Exception as e:
#                 logging.error(f"Error parsing components for {module_name} in {file_path}: {e}")
#                 components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates = (
#                     {"gates": [], "flip_flops": [], "wires": [], "registers": [], "counters": [], "instances": [], "muxes": []},
#                     {"wires": {}, "registers": {}, "gates": {}, "flip_flops": {}, "instances": {}, "muxes": {}},
#                     [], [], [], []
#                 )
#             for comp_type, comp_list in components.items():
#                 comp_type_display = "Flip_flops" if comp_type == "flip_flops" else comp_type.capitalize()
#                 detailed_output.append(f"    {comp_type_display}:")
#                 for comp in comp_list or ["(none)"]:
#                     detailed_output.append(f"      - {comp}")

#             detailed_output.append("  Connectivity Report:")
#             for line in connectivity_report or ["(none)"]:
#                 detailed_output.append(f"    - {line}")

#             detailed_output.append("  Module-to-Module Connectivity:")
#             for line in module_connectivity or ["(none)"]:
#                 detailed_output.append(f"    - {line}")

#             detailed_output.append("  Connectivity Issues:")
#             issues = False
#             for wire in unconnected_wires:
#                 detailed_output.append(f"    - Unconnected wire: {wire}")
#                 issues = True
#             for gate in unused_gates:
#                 detailed_output.append(f"    - Unused gate: {gate}")
#                 issues = True
#             if not issues:
#                 detailed_output.append("    (none)")

#             global_connections = {"wires": {}, "registers": {}, "gates": {}, "flip_flops": {}, "instances": {}, "muxes": {}}
#             for wire, conn in connections["wires"].items():
#                 if wire not in global_connections["wires"]:
#                     global_connections["wires"][wire] = {"source": None, "sinks": [], "type": conn["type"]}
#                 if conn["source"]:
#                     global_connections["wires"][wire]["source"] = conn["source"]
#                 global_connections["wires"][wire]["sinks"].extend([s for s in conn["sinks"] if s not in global_connections["wires"][wire]["sinks"]])
#             for reg, conn in connections["registers"].items():
#                 if reg not in global_connections["registers"]:
#                     global_connections["registers"][reg] = {"source": None, "sinks": []}
#                 if conn["source"]:
#                     global_connections["registers"][reg]["source"] = conn["source"]
#                 global_connections["registers"][reg]["sinks"].extend([s for s in conn["sinks"] if s not in global_connections["registers"][reg]["sinks"]])
#             for comp_type in ("gates", "flip_flops", "instances", "muxes"):
#                 global_connections[comp_type].update(connections[comp_type])

#             modules_processed += 1
#             modules_data.append((module_name, global_connections, components))

#     if modules_processed == 0:
#         detailed_output.append(f"  No valid modules found ({modules_processed} modules processed)")
#         logging.warning(f"No valid modules found in {file_path}")
#         return None
#     return modules_data
























# # tested1

# import re
# import logging
# import pyslang
# import os
# from uuid import uuid4
# from utility import detect_counter
# from ContextClasses import ParserContext, ComponentParserContext
# from typing import Dict, Set, Tuple, List

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     if included_files is None:
#         included_files = set()
#     try:
#         if file_path in included_files:
#             logging.warning(f"Skipping recursive include of {file_path}")
#             return source_text
#         included_files.add(file_path)
#         include_pattern = re.compile(r'`include\s+"([^"]+)"')
#         while include_pattern.search(source_text):
#             for match in include_pattern.finditer(source_text):
#                 include_file = match.group(1)
#                 include_path = os.path.join(os.path.dirname(file_path), include_file)
#                 logging.debug(f"Processing include: {include_file} -> {include_path}")
#                 try:
#                     with open(include_path, 'r', encoding='utf-8') as inc_file:
#                         include_content = inc_file.read()
#                     include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                     source_text = source_text.replace(match.group(0), include_content)
#                 except FileNotFoundError:
#                     logging.error(f"Include file not found: {include_path}")
#                     return source_text
#                 except Exception as e:
#                     logging.error(f"Error processing include {include_file}: {e}")
#                     return source_text
#         for macro_name, macro_value in macros.items():
#             macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#             def replace_macro(match):
#                 suffix = match.group(1)
#                 if suffix.startswith('-'):
#                     try:
#                         return str(int(macro_value) + int(suffix))
#                     except ValueError:
#                         return match.group(0)
#                 return str(macro_value)
#             source_text = macro_pattern.sub(replace_macro, source_text)
#             logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#         return source_text
#     except Exception as e:
#         logging.error(f"Error preprocessing {file_path}: {e}")
#         return source_text

# def get_port_width(port, macros: Dict[str, str]) -> str:
#     try:
#         port_name = getattr(port, 'name', None)
#         port_name = port_name.valueText if port_name and hasattr(port_name, 'valueText') else 'unknown'
#         # Check for explicit dimensions in the port or declarator
#         if hasattr(port, 'dimensions') and port.dimensions and len(port.dimensions) > 0:
#             dim = port.dimensions[0]
#             msb = str(dim.msb.valueText) if hasattr(dim.msb, 'valueText') else str(dim.msb)
#             lsb = str(dim.lsb.valueText) if hasattr(dim.lsb, 'valueText') else str(dim.lsb)
#             msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
#             lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
#             try:
#                 msb, lsb = int(msb), int(lsb)
#                 return f"[{msb}:{lsb}]"
#             except ValueError:
#                 logging.warning(f"Non-integer dimension in port {port_name}: msb={msb}, lsb={lsb}")
#                 return "1"
#         # Check for type-based dimensions
#         if hasattr(port, 'type') and port.type and hasattr(port.type, 'dimensions') and port.type.dimensions:
#             dim = port.type.dimensions[0]
#             msb = str(dim.msb.valueText) if hasattr(dim.msb, 'valueText') else str(dim.msb)
#             lsb = str(dim.lsb.valueText) if hasattr(dim.lsb, 'valueText') else str(dim.lsb)
#             msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
#             lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
#             try:
#                 msb, lsb = int(msb), int(lsb)
#                 return f"[{msb}:{lsb}]"
#             except ValueError:
#                 logging.warning(f"Non-integer type dimension in port {port_name}: msb={msb}, lsb={lsb}")
#                 return "1"
#         # Fallback based on port name conventions
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[15:0]"
#         if 'clk' in port_name.lower() or 'rst' in port_name.lower() or 'we' in port_name.lower() or 're' in port_name.lower() or 'ack' in port_name.lower() or 'err' in port_name.lower():
#             return "1"
#         # Check for macro-based widths
#         for macro_name, macro_value in macros.items():
#             if macro_name.lower() in port_name.lower():
#                 try:
#                     width = int(macro_value) - 1
#                     return f"[{width}:0]"
#                 except ValueError:
#                     pass
#         logging.debug(f"Default width for {port_name}: 1")
#         return "1"
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_name}: {e}")
#         return "1"



# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     ports = []
#     port_names = set()
#     try:
#         logging.debug(f"Parsing ports for module: {getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'}")
#         # Handle ANSI-style ports in the module header
#         if hasattr(member, 'header') and hasattr(member.header, 'ports'):
#             for port in member.header.ports:
#                 logging.debug(f"Found port node: kind={port.kind}, text={str(port)}")
#                 if port.kind in (pyslang.SyntaxKind.AnsiPortDeclaration, pyslang.SyntaxKind.NonAnsiPort):
#                     name = getattr(port, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         direction = str(getattr(port, 'direction', 'unknown')).lower().split()[0]
#                         data_type = str(getattr(port, 'type', 'wire')).strip() or 'wire'
#                         width = get_port_width(port, macros)
#                         ports.append(f"{name}: {direction} {data_type} {width}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed ANSI port: {name} ({direction} {data_type} {width})")
#                     else:
#                         logging.warning(f"Skipping port with no valid name: {str(port)}")

#         # Handle non-ANSI ports (declarations inside the module body)
#         for sub_member in member.members:
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 direction = str(getattr(sub_member, 'direction', 'unknown')).lower().split()[0]
#                 data_type = str(getattr(sub_member, 'type', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         width = get_port_width(declarator, macros)
#                         ports.append(f"{name}: {direction} {data_type} {width}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed non-ANSI port: {name} ({direction} {data_type} {width})")
#                     else:
#                         logging.warning(f"Skipping non-ANSI port declarator with no valid name: {str(declarator)}")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 # Cross-check with module header to confirm ports
#                 net_type = str(getattr(sub_member, 'netType', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         is_port = any(p.name.valueText == name for p in getattr(member.header, 'ports', []) if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                         if is_port:
#                             direction = "input" if "input" in str(sub_member).lower() else "output" if "output" in str(sub_member).lower() else "inout"
#                             width = get_port_width(declarator, macros)
#                             ports.append(f"{name}: {direction} {net_type} {width}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed net port: {name} ({direction} {net_type} {width})")
#         if not ports:
#             logging.warning(f"No ports found for module")
#         return sorted(ports), port_names
#     except Exception as e:
#         logging.error(f"Error parsing ports for module: {e}")
#         return ports, port_names




# def parse_blocks_wise(module_member, context: ComponentParserContext, connections):
#     inst_list = []
#     inst_connections = {}
#     try:
#         # Track all signals to identify sinks
#         signal_sinks = {}
#         for sub_member in module_member.members:
#             if sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
#                 inst_type = getattr(sub_member.type, 'name', None)
#                 inst_type = inst_type.valueText if inst_type and hasattr(inst_type, 'valueText') else str(sub_member.type).strip().split()[-1]
#                 for inst in sub_member.instances:
#                     inst_name = getattr(inst, 'name', None)
#                     inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"unknown_{uuid4().hex[:8]}"
#                     port_connections = {}
#                     for conn in getattr(inst, 'connections', []):
#                         port_name = getattr(conn, 'name', None)
#                         signal = str(conn.expr).strip() if hasattr(conn, 'expr') and conn.expr else None
#                         if port_name and signal and hasattr(port_name, 'valueText') and signal != "None":
#                             port_name = port_name.valueText
#                             # Clean up signal name (remove trailing underscores or invalid characters)
#                             signal = signal.rstrip('_').strip()
#                             port_connections[port_name] = signal
#                             base_signal = signal.split('[')[0]
#                             width = get_port_width(None, context.macros)
#                             connections["wires"].setdefault(base_signal, {"source": None, "sinks": [], "type": width})
#                             is_input = any(port_name in p and "input" in p.lower() for p in next((m["ports"] for m in context.all_modules if m["name"] == inst_type), []))
#                             if is_input:
#                                 connections["wires"][base_signal]["sinks"].append(f"{inst_type} instance ({inst_name}.{port_name})")
#                                 signal_sinks.setdefault(base_signal, []).append(f"{inst_type} instance ({inst_name}.{port_name})")
#                             else:
#                                 connections["wires"][base_signal]["source"] = f"{inst_type} instance ({inst_name}.{port_name})"
#                     if "SDK_" in inst_type:
#                         if "DFF" in inst_type.upper():
#                             components["flip_flops"].append(f"{inst_type} flip_flop: output={port_connections.get('Q', 'unknown')}, inputs={list(port_connections.values())}")
#                             connections["flip_flops"][port_connections.get('Q', inst_name)] = {"type": inst_type, "inputs": list(port_connections.values()), "drives": []}
#                         else:
#                             components["gates"].append(f"{inst_type} gate: output={port_connections.get('Z', 'unknown')}, inputs={list(port_connections.values())}")
#                             connections["gates"][port_connections.get('Z', inst_name)] = {"type": inst_type, "inputs": list(port_connections.values()), "drives": []}
#                     else:
#                         inst_list.append(f"{inst_type} instance ({inst_name})")
#                         inst_connections[inst_name] = {"module": inst_type, "ports": port_connections}
#                         logging.debug(f"Parsed instance: {inst_type} {inst_name}, ports={port_connections}")
#             elif sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
#                 assign_text = str(sub_member).strip()
#                 match = re.match(r'assign\s+([\w\[\]:]+)\s*=\s*([^;]+);', assign_text)
#                 if match:
#                     output, input_expr = match.groups()
#                     input_signals = re.findall(r'[\w\[\]:]+', input_expr)
#                     input_signals = [s.strip().rstrip('_') for s in input_signals if s.strip() and s not in ('!', '&', '|', '^', '~')]
#                     connections["gates"].setdefault(output, {"type": "assign", "inputs": input_signals, "drives": []})
#                     for signal in input_signals:
#                         base_signal = signal.split('[')[0]
#                         signal_sinks.setdefault(base_signal, []).append(f"Gate {output}")
#             elif sub_member.kind in (pyslang.SyntaxKind.AlwaysBlock, pyslang.SyntaxKind.AlwaysFFBlock):
#                 def traverse_statements(stmts):
#                     for stmt in stmts:
#                         if stmt.kind == pyslang.SyntaxKind.ExpressionStatement and stmt.expr.kind == pyslang.SyntaxKind.NonblockingAssignment:
#                             output = str(stmt.expr.left).strip().rstrip('_')
#                             input_expr = str(stmt.expr.right).strip()
#                             input_signals = re.findall(r'[\w\[\]:]+', input_expr)
#                             input_signals = [s.strip().rstrip('_') for s in input_signals if s.strip() and s not in ('!', '&', '|', '^', '~')]
#                             for signal in input_signals:
#                                 base_signal = signal.split('[')[0]
#                                 signal_sinks.setdefault(base_signal, []).append(f"Flip-flop {output}")
#                         elif hasattr(stmt, 'stmts'):
#                             traverse_statements(stmt.stmts)
#                 if hasattr(sub_member, 'statement'):
#                     traverse_statements([sub_member.statement])

#         # Update sinks for all wires
#         for wire, sinks in signal_sinks.items():
#             if wire in connections["wires"]:
#                 connections["wires"][wire]["sinks"].extend(sinks)
#         # Mark top-level ports as connected if they are module inputs/outputs
#         module_name = getattr(module_member.header, 'name', None).valueText if hasattr(module_member.header, 'name') else 'unknown'
#         module = next((m for m in context.all_modules if m["name"] == module_name), None)
#         if module:
#             for port in module.get("ports", []):
#                 port_name = port.split(':')[0].strip()
#                 if port_name in connections["wires"]:
#                     if "input" in port.lower():
#                         connections["wires"][port_name]["source"] = f"Top-level input {port_name}"
#                     elif "output" in port.lower():
#                         connections["wires"][port_name]["sinks"].append(f"Top-level output {port_name}")
#         return inst_list, inst_connections
#     except Exception as e:
#         logging.error(f"Error parsing instances: {e}")
#         return inst_list, inst_connections



# def parse_components(context: ComponentParserContext):
#     components = {"gates": [], "flip_flops": [], "wires": [], "registers": [], "counters": [], "instances": [], "muxes": []}
#     connections = {"wires": {}, "registers": {}, "gates": {}, "flip_flops": {}, "instances": {}, "muxes": {}}
#     connectivity_report = []
#     module_connectivity = []
#     unconnected_wires = []
#     unused_gates = []
#     parsed_ff_outputs = set()
#     parsed_gates = set()
#     parsed_muxes = set()
#     parsed_registers = set()
#     macros = context.macros

#     logging.debug(f"Starting component parsing for {context.module_name}")
#     module_member = None
#     for member in context.syntax_tree.root.members:
#         if member.kind == pyslang.SyntaxKind.ModuleDeclaration and getattr(member.header, 'name', None) and member.header.name.valueText == context.module_name:
#             module_member = member
#             break
#     if not module_member:
#         logging.error(f"Module {context.module_name} not found in syntax tree for {context.file_path}")
#         return components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates

#     logging.debug(f"Parsing components for module: {context.module_name}")
#     logging.debug(f"Syntax tree members for {context.module_name}: {[str(m.kind) for m in module_member.members]}")

#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#             for declarator in getattr(sub_member, 'declarators', []):
#                 name = getattr(declarator, 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     width = get_port_width(sub_member, macros)
#                     components["wires"].append(f"{name}: wire {width}")
#                     connections["wires"][name] = {"source": None, "sinks": [], "type": width}
#                     connectivity_report.append(f"Wire {name} ({width}): source=None, sinks=none")
#                     logging.debug(f"Detected wire: {name} ({width})")

#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#             data_type = str(sub_member.type).strip().lower()
#             if "integer" in data_type:
#                 logging.debug(f"Skipping integer declaration: {str(sub_member)}")
#                 continue
#             for declarator in getattr(sub_member, 'declarators', []) or []:
#                 name = getattr(declarator, 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     if name in parsed_registers:
#                         logging.debug(f"Skipping duplicate register: {name}")
#                         continue
#                     parsed_registers.add(name)
#                     width = get_port_width(sub_member, macros)
#                     is_array = bool(getattr(declarator, 'dimensions', None) or '[' in str(sub_member))
#                     if is_array:
#                         dim_str = f"0:{macros.get('DEPTH', 1)-1}"
#                         width = f"{width} [{dim_str}]"
#                     if "reg" in data_type:
#                         if detect_counter(name, context.source_text):
#                             components["counters"].append(f"{name}: counter {width}")
#                             connections["registers"][name] = {"source": "counter_logic", "sinks": []}
#                             logging.debug(f"Detected counter: {name} ({width})")
#                         else:
#                             display_type = f"reg array {width}" if is_array else f"reg {width}"
#                             components["registers"].append(f"{name}: {display_type}")
#                             connections["registers"][name] = {"source": None, "sinks": []}
#                             logging.debug(f"Detected register: {name} ({display_type})")

#     inst_list, inst_connections = parse_blocks_wise(module_member, context, connections)
#     components["instances"].extend(inst_list)
#     connections["instances"].update(inst_connections)

#     for sub_member in module_member.members:
#         if sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
#             assign_text = str(sub_member).strip()
#             match = re.match(r'assign\s+([\w\[\]:]+)\s*=\s*([^;]+);', assign_text)
#             if match:
#                 output, input_expr = match.groups()
#                 gate_type = "MUX" if " ?" in input_expr else "assign"
#                 input_signals = re.split(r'[\s,|&~^]+', input_expr) if gate_type == "assign" else input_expr.split(' ? ')[1].split(' : ')
#                 input_signals = [s.strip() for s in input_signals if s.strip()]
#                 components["gates" if gate_type == "assign" else "muxes"].append(f"{gate_type} gate: output={output}, inputs={input_signals}")
#                 connections["gates" if gate_type == "assign" else "muxes"][output] = {"type": gate_type, "inputs": input_signals, "drives": []}
#                 logging.debug(f"Detected {gate_type} gate: {output} = {input_expr}")

#     for sub_member in module_member.members:
#         if sub_member.kind in [pyslang.SyntaxKind.AlwaysBlock, pyslang.SyntaxKind.AlwaysFFBlock]:
#             sensitivity_list = str(sub_member.sensitivityList) if hasattr(sub_member, 'sensitivityList') else ""
#             clock = "unknown"
#             reset = "none"
#             if "posedge" in sensitivity_list:
#                 clock = sensitivity_list.split("posedge ")[1].split()[0].strip(')')
#             if "negedge" in sensitivity_list:
#                 reset = sensitivity_list.split("negedge ")[1].split()[0].strip(')')
#             def traverse_statements(stmts):
#                 for stmt in stmts:
#                     if stmt.kind == pyslang.SyntaxKind.ExpressionStatement and stmt.expr.kind == pyslang.SyntaxKind.NonblockingAssignment:
#                         output = str(stmt.expr.left).strip()
#                         input_expr = str(stmt.expr.right).strip()
#                         if output not in parsed_ff_outputs:
#                             components["flip_flops"].append(f"D flip-flop: output={output}, input={input_expr}, clock={clock}, reset={reset}")
#                             connections["flip_flops"][output] = {"input": input_expr, "clock": clock, "reset": reset, "drives": []}
#                             parsed_ff_outputs.add(output)
#                             logging.debug(f"Detected flip-flop: {output} <= {input_expr}, clock={clock}")
#                     elif hasattr(stmt, 'stmts'):
#                         traverse_statements(stmt.stmts)
#             if hasattr(sub_member, 'statement'):
#                 traverse_statements([sub_member.statement])

#     for wire, conn in connections["wires"].items():
#         if not conn["source"] and not conn["sinks"]:
#             unconnected_wires.append(wire)
#         connectivity_report.append(f"Wire {wire} ({conn['type']}): source={conn['source']}, sinks={conn['sinks']}")

#     for gate, conn in connections["gates"].items():
#         if not conn["drives"]:
#             unused_gates.append(gate)
#         connectivity_report.append(f"Gate {gate}: inputs={conn['inputs']}, drives={conn['drives']}")

#     for inst_name, inst_conn in connections["instances"].items():
#         module_connectivity.append(f"{context.module_name} -> {inst_conn['module']} instance ({inst_name})")

#     return components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output):
#     module_data = []
#     try:
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, port_names = parse_module_ports(member, macros)
#                 context = ComponentParserContext(
#                     file_path=file_path,
#                     source_text=source_text,
#                     port_names=port_names,
#                     module_name=module_name,
#                     all_modules=all_modules,
#                     syntax_tree=syntax_tree,
#                     parsed_instances=parsed_instances,
#                     module_names=module_names,
#                     macros=macros
#                 )
#                 components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates = parse_components(context)
#                 module_data.append((module_name, connections, components))
#                 detailed_output.append(f"\nModule: {module_name}")
#                 detailed_output.append(f"Ports: {', '.join(ports) if ports else '(none)'}")
#                 for comp_type, comp_list in components.items():
#                     detailed_output.append(f"{comp_type.capitalize()}: {', '.join(comp_list) if comp_list else '(none)'}")
#                 detailed_output.append("Connectivity Report:")
#                 detailed_output.extend([f"  {line}" for line in connectivity_report or ["(none)"]])
#                 detailed_output.append("Module-to-Module Connectivity:")
#                 detailed_output.extend([f"  {line}" for line in module_connectivity or ["(none)"]])
#                 if unconnected_wires:
#                     detailed_output.append(f"Unconnected Wires: {', '.join(unconnected_wires)}")
#                 if unused_gates:
#                     detailed_output.append(f"Unused Gates: {', '.join(unused_gates)}")
#                 if not unconnected_wires and not unused_gates:
#                     detailed_output.append("Connectivity Issues: (none)")
#                 logging.info(f"Processed module {module_name} with {len(ports)} ports and {sum(len(c) for c in components.values())} components")
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return module_data






























# # tested2

# import re
# import logging
# import pyslang
# import os
# from uuid import uuid4
# from utility import detect_counter
# from ContextClasses import ParserContext, ComponentParserContext
# from typing import Dict, Set, Tuple, List

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     if included_files is None:
#         included_files = set()
#     try:
#         if file_path in included_files:
#             logging.warning(f"Skipping recursive include of {file_path}")
#             return source_text
#         included_files.add(file_path)
#         include_pattern = re.compile(r'`include\s+"([^"]+)"')
#         while include_pattern.search(source_text):
#             for match in include_pattern.finditer(source_text):
#                 include_file = match.group(1)
#                 include_path = os.path.join(os.path.dirname(file_path), include_file)
#                 logging.debug(f"Processing include: {include_file} -> {include_path}")
#                 try:
#                     with open(include_path, 'r', encoding='utf-8') as inc_file:
#                         include_content = inc_file.read()
#                     include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                     source_text = source_text.replace(match.group(0), include_content)
#                 except FileNotFoundError:
#                     logging.error(f"Include file not found: {include_path}")
#                     return source_text
#                 except Exception as e:
#                     logging.error(f"Error processing include {include_file}: {e}")
#                     return source_text
#         for macro_name, macro_value in macros.items():
#             macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#             def replace_macro(match):
#                 suffix = match.group(1)
#                 if suffix.startswith('-'):
#                     try:
#                         return str(int(macro_value) + int(suffix))
#                     except ValueError:
#                         return match.group(0)
#                 return str(macro_value)
#             source_text = macro_pattern.sub(replace_macro, source_text)
#             logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#         return source_text
#     except Exception as e:
#         logging.error(f"Error preprocessing {file_path}: {e}")
#         return source_text

# def get_port_width(port, macros: Dict[str, str]) -> str:
#     try:
#         if port is None:
#             return "1"
#         # Handle explicit dimensions
#         if hasattr(port, 'dimensions') and len(port.dimensions) > 0:
#             dim = port.dimensions[0]
#             msb = str(dim.msb.valueText) if hasattr(dim.msb, 'valueText') else str(dim.msb)
#             lsb = str(dim.lsb.valueText) if hasattr(dim.lsb, 'valueText') else str(dim.lsb)
#             if msb in macros:
#                 msb = str(macros[msb])
#             if lsb in macros:
#                 lsb = str(macros[lsb])
#             try:
#                 msb, lsb = int(msb), int(lsb)
#                 return f"[{msb}:{lsb}]"
#             except ValueError:
#                 logging.warning(f"Non-integer dimension in port: msb={msb}, lsb={lsb}")
#         # Handle type-based width
#         if hasattr(port, 'type') and port.type:
#             type_str = str(port.type)
#             match = re.search(r'\[(\d+|`?\w+):(\d+|`?\w+)\]', type_str)
#             if match:
#                 msb, lsb = match.groups()
#                 if msb.startswith('`'):
#                     msb = macros.get(msb[1:], msb)
#                 if lsb.startswith('`'):
#                     lsb = macros.get(lsb[1:], lsb)
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer type dimension: msb={msb}, lsb={lsb}")
#         # Fallback to text-based analysis
#         if hasattr(port, 'getText'):
#             text = port.getText()
#             match = re.search(r'\[(\w+|\d+):(\w+|\d+)\]', text)
#             if match:
#                 msb, lsb = match.groups()
#                 if msb in macros:
#                     msb = str(macros[msb])
#                 if lsb in macros:
#                     lsb = str(macros[lsb])
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer text dimension: msb={msb}, lsb={lsb}")
#         # Check port name for specific widths
#         port_name = getattr(port, 'name', None)
#         port_name = port_name.valueText if port_name and hasattr(port_name, 'valueText') else ''
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[15:0]"
#         if any(macro in port_name for macro in macros):
#             for macro_name, macro_value in macros.items():
#                 if macro_name in port_name:
#                     try:
#                         width = int(macro_value) - 1
#                         return f"[{width}:0]"
#                     except ValueError:
#                         pass
#         # Default to 1 for control signals
#         if port_name in ('clk', 'rst_n', 'valid', 'proc_valid'):
#             return "1"
#         return "1"
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_name}: {e}")
#         return "1"

# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     ports = []
#     port_names = set()
#     try:
#         # Handle ANSI-style ports
#         if hasattr(member, 'header') and hasattr(member.header, 'ports') and member.header.ports:
#             for port in member.header.ports:
#                 name = getattr(port, 'name', None) or getattr(getattr(port, 'declarator', None), 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     direction = "unknown"
#                     if hasattr(port, 'direction'):
#                         direction = str(port.direction).lower().split()[0]
#                     elif hasattr(getattr(port, 'header', None), 'direction'):
#                         direction = str(port.header.direction).lower().split()[0]
#                     data_type = str(getattr(port, 'type', '') or getattr(port.header, 'dataType', '') or 'wire').strip()
#                     width = get_port_width(port, macros)
#                     ports.append(f"{name}: {direction} {data_type} {width}")
#                     port_names.add(name)
#                     logging.debug(f"Parsed ANSI port: {name} ({direction} {data_type} {width})")
#         # Handle non-ANSI-style ports
#         for sub_member in member.members:
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 name = getattr(sub_member, 'name', None) or getattr(getattr(sub_member, 'declarator', None), 'name', None)
#                 if name and hasattr(name, 'valueText') and name.valueText not in port_names:
#                     name = name.valueText
#                     direction = str(getattr(sub_member, 'direction', 'input')).lower().split()[0]
#                     data_type = str(getattr(sub_member, 'type', 'wire')).strip()
#                     width = get_port_width(sub_member, macros)
#                     ports.append(f"{name}: {direction} {data_type} {width}")
#                     port_names.add(name)
#                     logging.debug(f"Parsed non-ANSI port: {name} ({direction} {data_type} {width})")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText') and name.valueText not in port_names:
#                         name = name.valueText
#                         direction = 'input' if name in ('clk', 'rst_n', 'data_in') else 'output'
#                         data_type = 'wire'
#                         width = get_port_width(sub_member, macros)
#                         ports.append(f"{name}: {direction} {data_type} {width}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed net port: {name} ({direction} {data_type} {width})")
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText') and name.valueText not in port_names:
#                         name = name.valueText
#                         data_type = str(sub_member.type).strip().lower()
#                         if 'reg' in data_type:
#                             direction = 'output'
#                             width = get_port_width(sub_member, macros)
#                             ports.append(f"{name}: {direction} reg {width}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed reg port: {name} ({direction} reg {width})")
#     except Exception as e:
#         logging.error(f"Error parsing ports for module: {e}")
#     return sorted(ports), port_names

# def extract_signals(expr_str):
#     signals = re.findall(r'\b[\w\$]+\b(?:\s*\[.*?\])?', expr_str)
#     return [s.strip() for s in signals if not re.match(r"^\d+'[bdhox]\w*$", s) and s.strip() not in ('!', '&', '|', '^', '~', '?', ':')]

# def parse_blocks_wise(module_member, context: ComponentParserContext, connections):
#     inst_list = []
#     inst_connections = {}
#     try:
#         # Track all signals to identify sinks
#         signal_sinks = {}
#         all_sub_members = collect_members(module_member)
#         for sub_member in all_sub_members:
#             if str(sub_member.kind) == 'HierarchyInstantiation':
#                 inst_type = getattr(sub_member.type, 'name', None)
#                 inst_type = inst_type.valueText if inst_type and hasattr(inst_type, 'valueText') else str(sub_member.type).strip().split()[-1]
#                 for inst in sub_member.instances:
#                     inst_name = getattr(inst, 'name', None)
#                     inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"unknown_{uuid4().hex[:8]}"
#                     port_connections = {}
#                     for conn in getattr(inst, 'connections', []):
#                         port_name = getattr(conn, 'name', None)
#                         signal = str(conn.expr).strip() if hasattr(conn, 'expr') and conn.expr else None
#                         if port_name and signal and hasattr(port_name, 'valueText') and signal != "None":
#                             port_name = port_name.valueText
#                             # Clean up signal name (remove trailing underscores or invalid characters)
#                             signal = signal.rstrip('_').strip()
#                             port_connections[port_name] = signal
#                             base_signal = signal.split('[')[0]
#                             signal_sinks.setdefault(base_signal, []).append(f"{inst_type} instance ({inst_name}.{port_name})")
#                     if "SDK_" in inst_type:
#                         if "DFF" in inst_type.upper():
#                             components["flip_flops"].append(f"{inst_type} flip_flop: output={port_connections.get('Q', 'unknown')}, inputs={list(port_connections.values())}")
#                             connections["flip_flops"][port_connections.get('Q', inst_name)] = {"type": inst_type, "inputs": list(port_connections.values()), "drives": []}
#                         else:
#                             components["gates"].append(f"{inst_type} gate: output={port_connections.get('Z', 'unknown')}, inputs={list(port_connections.values())}")
#                             connections["gates"][port_connections.get('Z', inst_name)] = {"type": inst_type, "inputs": list(port_connections.values()), "drives": []}
#                     else:
#                         inst_list.append(f"{inst_type} instance ({inst_name})")
#                         inst_connections[inst_name] = {"module": inst_type, "ports": port_connections}
#                         logging.debug(f"Parsed instance: {inst_type} {inst_name}, ports={port_connections}")
#             elif str(sub_member.kind) == 'ContinuousAssign':
#                 assign_text = str(sub_member).strip()
#                 match = re.match(r'assign\s+([\w\[\]:]+)\s*=\s*([^;]+);', assign_text)
#                 if match:
#                     output, input_expr = match.groups()
#                     input_signals = extract_signals(input_expr)
#                     for sig in input_signals:
#                         base_sig = sig.split('[')[0]
#                         signal_sinks.setdefault(base_sig, []).append(f"Gate {output}")
#             elif str(sub_member.kind) in ('AlwaysBlock', 'AlwaysFFBlock'):
#                 def traverse_statements(stmts):
#                     for stmt in (stmts if isinstance(stmts, list) else [stmts]):
#                         if not hasattr(stmt, 'kind'):
#                             continue
#                         if str(stmt.kind) == 'ExpressionStatement':
#                             expr_kind = str(getattr(stmt.expr, 'kind', ''))
#                             if expr_kind == 'NonblockingAssignment':
#                                 output = str(stmt.expr.left).strip().rstrip('_')
#                                 input_expr = str(stmt.expr.right).strip()
#                                 input_signals = extract_signals(input_expr)
#                                 for sig in input_signals:
#                                     base_sig = sig.split('[')[0]
#                                     signal_sinks.setdefault(base_sig, []).append(f"Flip-flop {output}")
#                             elif expr_kind == 'BlockingAssignment':
#                                 output = str(stmt.expr.left).strip().rstrip('_')
#                                 input_expr = str(stmt.expr.right).strip()
#                                 input_signals = extract_signals(input_expr)
#                                 for sig in input_signals:
#                                     base_sig = sig.split('[')[0]
#                                     signal_sinks.setdefault(base_sig, []).append(f"Gate {output}")
#                         elif hasattr(stmt, 'stmt') or hasattr(stmt, 'stmts'):
#                             sub_stmts = getattr(stmt, 'stmts', [getattr(stmt, 'stmt', None)])
#                             traverse_statements([s for s in sub_stmts if s])
#                         elif hasattr(stmt, 'body'):
#                             traverse_statements([stmt.body])
#                 if hasattr(sub_member, 'statement'):
#                     traverse_statements(sub_member.statement)

#         # Update sinks for all wires
#         for wire, sinks in signal_sinks.items():
#             if wire in connections["wires"]:
#                 connections["wires"][wire]["sinks"].extend(sinks)
#         # Mark top-level ports as connected if they are module inputs/outputs
#         module_name = getattr(module_member.header, 'name', None).valueText if hasattr(module_member.header, 'name') else 'unknown'
#         module = next((m for m in context.all_modules if m["name"] == module_name), None)
#         if module:
#             for port in module.get("ports", []):
#                 port_name = port.split(':')[0].strip()
#                 if port_name in connections["wires"]:
#                     if "input" in port.lower():
#                         connections["wires"][port_name]["source"] = f"Top-level input {port_name}"
#                     elif "output" in port.lower():
#                         connections["wires"][port_name]["sinks"].append(f"Top-level output {port_name}")
#         return inst_list, inst_connections
#     except Exception as e:
#         logging.error(f"Error parsing instances: {e}")
#         return inst_list, inst_connections

# def collect_members(module_member):
#     members = []
#     def recurse(m):
#         members.append(m)
#         if hasattr(m, 'members'):
#             for sub in m.members:
#                 recurse(sub)
#         if str(m.kind) == 'LoopGenerate':
#             if hasattr(m, 'block'):
#                 recurse(m.block)
#         if str(m.kind) == 'IfGenerate':
#             if hasattr(m, 'thenBlock'):
#                 recurse(m.thenBlock)
#             if hasattr(m, 'elseBlock'):
#                 recurse(m.elseBlock)
#         if str(m.kind) == 'CaseGenerate':
#             for item in getattr(m, 'items', []):
#                 if hasattr(item, 'block'):
#                     recurse(item.block)
#     for top_member in module_member.members:
#         recurse(top_member)
#     return members

# def parse_components(context: ComponentParserContext):
#     components = {"gates": [], "flip_flops": [], "wires": [], "registers": [], "counters": [], "instances": [], "muxes": []}
#     connections = {"wires": {}, "registers": {}, "gates": {}, "flip_flops": {}, "instances": {}, "muxes": {}}
#     connectivity_report = []
#     module_connectivity = []
#     unconnected_wires = []
#     unused_gates = []
#     parsed_ff_outputs = set()
#     parsed_gates = set()
#     parsed_muxes = set()
#     parsed_registers = set()
#     macros = context.macros
#     lib_cells = context.lib_cells or []

#     logging.debug(f"Starting component parsing for {context.module_name}")
#     module_member = None
#     for member in context.syntax_tree.root.members:
#         if str(member.kind) == 'ModuleDeclaration' and getattr(member.header, 'name', None) and member.header.name.valueText == context.module_name:
#             module_member = member
#             break
#     if not module_member:
#         logging.error(f"Module {context.module_name} not found in syntax tree for {context.file_path}")
#         return components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates

#     # Wires
#     for sub_member in collect_members(module_member):
#         if str(sub_member.kind) == 'NetDeclaration':
#             for declarator in getattr(sub_member, 'declarators', []):
#                 name = getattr(declarator, 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     width = get_port_width(sub_member, macros)
#                     components["wires"].append(f"{name}: wire {width}")
#                     connections["wires"][name] = {"source": None, "sinks": [], "type": width}
#                     connectivity_report.append(f"Wire {name} ({width}): source=None, sinks=none")
#                     logging.debug(f"Detected wire: {name} ({width})")

#     # Registers and counters
#     for sub_member in collect_members(module_member):
#         if str(sub_member.kind) == 'DataDeclaration':
#             data_type = str(sub_member.type).strip().lower()
#             if "integer" in data_type:
#                 logging.debug(f"Skipping integer declaration: {str(sub_member)}")
#                 continue
#             for declarator in getattr(sub_member, 'declarators', []) or []:
#                 name = getattr(declarator, 'name', None)
#                 if name and hasattr(name, 'valueText'):
#                     name = name.valueText
#                     if name in parsed_registers:
#                         continue
#                     parsed_registers.add(name)
#                     width = get_port_width(sub_member, macros)
#                     is_array = bool(getattr(declarator, 'dimensions', None) or '[' in str(sub_member))
#                     if is_array:
#                         dim_str = f"0:{macros.get('DEPTH', 1)-1}"
#                         width = f"{width} [{dim_str}]"
#                     if "reg" in data_type:
#                         if detect_counter(name, context.source_text):
#                             components["counters"].append(f"{name}: counter {width}")
#                             connections["registers"][name] = {"source": "counter_logic", "sinks": []}
#                             logging.debug(f"Detected counter: {name} ({width})")
#                         else:
#                             display_type = f"reg array {width}" if is_array else f"reg {width}"
#                             components["registers"].append(f"{name}: {display_type}")
#                             connections["registers"][name] = {"source": None, "sinks": []}
#                             logging.debug(f"Detected register: {name} ({display_type})")

#     # Instances and standard cells
#     inst_list, inst_connections = parse_blocks_wise(module_member, context, connections)
#     for inst_name, inst_conn in inst_connections.items():
#         inst_type = inst_conn["module"]
#         if inst_type in lib_cells:  # Check if instance is a standard cell
#             if "DFF" in inst_type.upper():
#                 components["flip_flops"].append(f"{inst_type} flip_flop: output={inst_conn['ports'].get('Q', 'unknown')}, inputs={list(inst_conn['ports'].values())}")
#                 connections["flip_flops"][inst_conn['ports'].get('Q', inst_name)] = {"type": inst_type, "inputs": list(inst_conn['ports'].values()), "drives": []}
#             else:
#                 components["gates"].append(f"{inst_type} gate: output={inst_conn['ports'].get('Z', 'unknown')}, inputs={list(inst_conn['ports'].values())}")
#                 connections["gates"][inst_conn['ports'].get('Z', inst_name)] = {"type": inst_type, "inputs": list(inst_conn['ports'].values()), "drives": []}
#         else:
#             components["instances"].append(f"{inst_type} instance ({inst_name})")
#             connections["instances"][inst_name] = inst_conn
#     components["instances"].extend([i for i in inst_list if not any(c in i for c in lib_cells)])

#     # Gates and Muxes
#     for sub_member in collect_members(module_member):
#         if str(sub_member.kind) == 'ContinuousAssign':
#             assign_text = str(sub_member).strip()
#             match = re.match(r'assign\s+([\w\[\]:]+)\s*=\s*([^;]+);', assign_text)
#             if match:
#                 output, input_expr = match.groups()
#                 gate_type = "MUX" if " ?" in input_expr else "assign"
#                 input_signals = extract_signals(input_expr)
#                 components["gates" if gate_type == "assign" else "muxes"].append(f"{gate_type} gate: output={output}, inputs={input_signals}")
#                 connections["gates" if gate_type == "assign" else "muxes"][output] = {"type": gate_type, "inputs": input_signals, "drives": []}
#                 logging.debug(f"Detected {gate_type} gate: {output} = {input_expr}")

#     # Flip-flops
#     for sub_member in collect_members(module_member):
#         if str(sub_member.kind) in ['AlwaysBlock', 'AlwaysFFBlock']:
#             sensitivity_list = str(sub_member.sensitivityList) if hasattr(sub_member, 'sensitivityList') else ""
#             clock = "unknown"
#             reset = "none"
#             if "posedge" in sensitivity_list:
#                 clock = sensitivity_list.split("posedge ")[1].split()[0].strip(')')
#             if "negedge" in sensitivity_list:
#                 reset = sensitivity_list.split("negedge ")[1].split()[0].strip(')')
#             def traverse_statements(stmts):
#                 for stmt in (stmts if isinstance(stmts, list) else [stmts]):
#                     if not hasattr(stmt, 'kind'):
#                         continue
#                     if str(stmt.kind) == 'ExpressionStatement' and str(getattr(stmt.expr, 'kind', '')) == 'NonblockingAssignment':
#                         output = str(stmt.expr.left).strip()
#                         input_expr = str(stmt.expr.right).strip()
#                         if output not in parsed_ff_outputs:
#                             components["flip_flops"].append(f"D flip-flop: output={output}, input={input_expr}, clock={clock}, reset={reset}")
#                             connections["flip_flops"][output] = {"input": input_expr, "clock": clock, "reset": reset, "drives": []}
#                             parsed_ff_outputs.add(output)
#                             logging.debug(f"Detected flip-flop: {output} <= {input_expr}, clock={clock}")
#             if hasattr(sub_member, 'statement'):
#                 traverse_statements(sub_member.statement)

#     # Connectivity analysis
#     for wire, conn in connections["wires"].items():
#         if not conn["source"] and not conn["sinks"]:
#             unconnected_wires.append(wire)
#         connectivity_report.append(f"Wire {wire} ({conn['type']}): source={conn['source']}, sinks={conn['sinks']}")

#     for gate, conn in connections["gates"].items():
#         if not conn["drives"]:
#             unused_gates.append(gate)
#         connectivity_report.append(f"Gate {gate}: inputs={conn['inputs']}, drives={conn['drives']}")

#     for inst_name, inst_conn in connections["instances"].items():
#         module_connectivity.append(f"{context.module_name} -> {inst_conn['module']} instance ({inst_name})")

#     return components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells=None):
#     module_data = []
#     try:
#         for member in syntax_tree.root.members:
#             if str(member.kind) == 'ModuleDeclaration':
#                 # Fallback for module name extraction
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     member_str = str(member).strip()
#                     match = re.match(r'module\s+(\w+)', member_str)
#                     if match:
#                         module_name = match.group(1)
#                         logging.debug(f"Fallback: Extracted module name {module_name} from text")
#                     else:
#                         logging.warning(f"Skipping module with no valid name in {file_path}")
#                         continue
#                 else:
#                     module_name = module_name.valueText
#                 ports, port_names = parse_module_ports(member, macros)
#                 context = ComponentParserContext(
#                     file_path=file_path,
#                     source_text=source_text,
#                     port_names=port_names,
#                     module_name=module_name,
#                     all_modules=all_modules,
#                     syntax_tree=syntax_tree,
#                     parsed_instances=parsed_instances,
#                     module_names=module_names,
#                     macros=macros,
#                     lib_cells=lib_cells  # Pass lib_cells to context
#                 )
#                 components, connections, connectivity_report, module_connectivity, unconnected_wires, unused_gates = parse_components(context)
#                 module_data.append((module_name, connections, components))
#                 detailed_output.append(f"\nModule: {module_name}")
#                 detailed_output.append(f"Ports: {', '.join(ports) if ports else '(none)'}")
#                 for comp_type, comp_list in components.items():
#                     detailed_output.append(f"{comp_type.capitalize()}: {', '.join(comp_list) if comp_list else '(none)'}")
#                 detailed_output.append("Connectivity Report:")
#                 detailed_output.extend([f"  {line}" for line in connectivity_report or ["(none)"]])
#                 detailed_output.append("Module-to-Module Connectivity:")
#                 detailed_output.extend([f"  {line}" for line in module_connectivity or ["(none)"]])
#                 if unconnected_wires:
#                     detailed_output.append(f"Unconnected Wires: {', '.join(unconnected_wires)}")
#                 if unused_gates:
#                     detailed_output.append(f"Unused Gates: {', '.join(unused_gates)}")
#                 if not unconnected_wires and not unused_gates:
#                     detailed_output.append("Connectivity Issues: (none)")
#                 logging.info(f"Processed module {module_name} with {len(ports)} ports and {sum(len(c) for c in components.values())} components")
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return module_data



































# # tested3

# import re
# import logging
# import pyslang
# import os
# from utility import detect_counter, log_section
# from typing import Dict, Set, Tuple, List

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     if included_files is None:
#         included_files = set()
#     if file_path in included_files:
#         logging.warning(f"Skipping recursive include of {file_path}")
#         return source_text
#     included_files.add(file_path)
#     include_pattern = re.compile(r'`include\s+"([^"]+)"')
#     while include_pattern.search(source_text):
#         for match in include_pattern.finditer(source_text):
#             include_file = match.group(1)
#             include_path = os.path.join(os.path.dirname(file_path), include_file)
#             logging.debug(f"Processing include: {include_file} -> {include_path}")
#             try:
#                 with open(include_path, 'r', encoding='utf-8') as inc_file:
#                     include_content = inc_file.read()
#                 include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                 source_text = source_text.replace(match.group(0), include_content)
#             except Exception as e:
#                 logging.error(f"Error processing include {include_path}: {e}")
#     for macro_name, macro_value in macros.items():
#         macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#         def replace_macro(match):
#             suffix = match.group(1)
#             try:
#                 if suffix:
#                     return str(int(macro_value) + int(suffix))
#                 return str(macro_value)
#             except ValueError:
#                 return macro_value
#         source_text = macro_pattern.sub(replace_macro, source_text)
#         logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#     debug_path = file_path + ".preprocessed"
#     with open(debug_path, 'w', encoding='utf-8') as f:
#         f.write(source_text)
#     logging.debug(f"Saved preprocessed text to {debug_path}")
#     return source_text

# def get_port_width(port, macros: Dict[str, str]) -> str:
#     try:
#         port_name = getattr(port, 'name', None)
#         port_name = port_name.valueText if port_name and hasattr(port_name, 'valueText') else 'unknown'
#         dimensions = getattr(port, 'dimensions', []) or getattr(getattr(port, 'type', None), 'dimensions', []) or []
#         if dimensions:
#             dim = dimensions[0]
#             msb = str(getattr(dim, 'msb', '') or getattr(dim, 'upper', '') or '')
#             lsb = str(getattr(dim, 'lsb', '') or getattr(dim, 'lower', '') or '')
#             msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
#             lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
#             if msb and lsb:
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer dimension in port {port_name}: msb={msb}, lsb={lsb}")
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[15:0]"
#         if 'clk' in port_name.lower() or 'rst' in port_name.lower() or 'we' in port_name.lower() or 're' in port_name.lower() or 'ack' in port_name.lower() or 'err' in port_name.lower():
#             return "1"
#         for macro_name, macro_value in macros.items():
#             if macro_name.lower() in port_name.lower():
#                 try:
#                     width = int(macro_value) - 1
#                     return f"[{width}:0]"
#                 except ValueError:
#                     pass
#         logging.debug(f"Default width for {port_name}: 1")
#         return "1"
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_name}: {e}")
#         return "1"

# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     ports = []
#     port_names = set()
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing ports for module: {module_name}")
#         # Log all available SyntaxKind values
#         import pyslang
#         syntax_kinds = [k for k in dir(pyslang.SyntaxKind) if not k.startswith('_')]
#         logging.debug(f"Available SyntaxKind values: {syntax_kinds}")
#         # Log header and member details
#         header_text = str(getattr(member, 'header', ''))
#         logging.debug(f"Module header text: {header_text}")
#         header_ports = getattr(member.header, 'ports', [])
#         logging.debug(f"Header port kinds: {[p.kind for p in header_ports]}")
#         logging.debug(f"Member kinds: {[m.kind for m in member.members]}")
#         # ANSI ports
#         if header_ports:
#             for port in header_ports:
#                 logging.debug(f"Port node kind: {port.kind}, text={str(port)}")
#                 if port.kind == pyslang.SyntaxKind.AnsiPortList:
#                     for sub_port in getattr(port, 'ports', [port]):
#                         name = getattr(sub_port, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             direction = str(getattr(sub_port, 'direction', 'unknown')).lower().split()[0]
#                             data_type = str(getattr(sub_port, 'type', 'wire')).strip() or 'wire'
#                             width = get_port_width(sub_port, macros)
#                             ports.append(f"{name}: {direction} {data_type} {width}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed ANSI port: {name} ({direction} {data_type} {width})")
#         # Non-ANSI ports and other declarations
#         for sub_member in member.members:
#             logging.debug(f"Sub-member kind: {sub_member.kind}, text={str(sub_member)}")
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 direction = str(getattr(sub_member, 'direction', 'unknown')).lower().split()[0]
#                 data_type = str(getattr(sub_member, 'type', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         width = get_port_width(declarator, macros)
#                         ports.append(f"{name}: {direction} {data_type} {width}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed non-ANSI port: {name} ({direction} {data_type} {width})")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 net_type = str(getattr(sub_member, 'netType', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                         if is_port:
#                             direction = "input" if "input" in str(sub_member).lower() else "output" if "output" in str(sub_member).lower() else "inout"
#                             width = get_port_width(declarator, macros)
#                             ports.append(f"{name}: {direction} {net_type} {width}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed net port: {name} ({direction} {net_type} {width})")
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                             if is_port:
#                                 width = get_port_width(declarator, macros)
#                                 ports.append(f"{name}: output reg {width}")
#                                 port_names.add(name)
#                                 logging.debug(f"Parsed reg port: {name} (output reg {width})")
#         # Fallback: Parse ports from raw header text
#         if not ports:
#             port_match = re.search(r'module\s+\w+\s*(?:\((.*?)\))?\s*;', header_text, re.DOTALL)
#             if port_match and port_match.group(1):
#                 port_list = [p.strip() for p in port_match.group(1).split(',') if p.strip()]
#                 for port in port_list:
#                     # Try to extract direction and type from preceding declarations
#                     direction = "input"
#                     data_type = "wire"
#                     width = "1"
#                     port_name = port
#                     # Check if port is defined in members
#                     for sub_member in member.members:
#                         member_text = str(sub_member).lower()
#                         if port in member_text:
#                             if 'input' in member_text:
#                                 direction = "input"
#                             elif 'output' in member_text:
#                                 direction = "output"
#                             elif 'inout' in member_text:
#                                 direction = "inout"
#                             if 'reg' in member_text:
#                                 data_type = "reg"
#                             elif 'wire' in member_text:
#                                 data_type = "wire"
#                             # Extract width if present
#                             width_match = re.search(rf'{port}\s*\[(\d+):(\d+)\]', member_text)
#                             if width_match:
#                                 msb, lsb = width_match.groups()
#                                 width = f"[{msb}:{lsb}]"
#                     ports.append(f"{port_name}: {direction} {data_type} {width}")
#                     port_names.add(port_name)
#                     logging.debug(f"Parsed fallback port: {port_name} ({direction} {data_type} {width})")
#         if not ports:
#             logging.warning(f"No ports found for module {module_name}. Check port declarations in source.")
#         return sorted(ports), port_names
#     except Exception as e:
#         logging.error(f"Error parsing ports for module {module_name}: {e}")
#         return ports, port_names

# def parse_components(member, source_text, port_names, macros, lib_cells: Dict[str, Dict[str, str]]):
#     components = {"wires": [], "registers": [], "counters": [], "flip_flops": [], "gates": [], "muxes": [], "instances": [], "switches": []}
#     connections = {"wires": {}, "instances": {}}
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing components for module: {module_name}")
#         for sub_member in member.members:
#             logging.debug(f"Processing sub-member kind: {sub_member.kind}, text={str(sub_member)}")
#             # Wires and registers
#             if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         if name not in port_names:
#                             components["wires"].append(name)
#                             connections["wires"][name] = {"source": [], "sinks": []}
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             if name not in port_names:
#                                 components["registers"].append(name)
#                                 connections["wires"][name] = {"source": [], "sinks": []}
#             # Instances
#             elif sub_member.kind in [getattr(pyslang.SyntaxKind, 'ModuleInstance', None), getattr(pyslang.SyntaxKind, 'Instance', None)]:
#                 inst_name = getattr(sub_member, 'name', None)
#                 inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else 'unknown'
#                 module_type = getattr(sub_member, 'moduleName', None)
#                 module_type = module_type.valueText if module_type and hasattr(module_type, 'valueText') else 'unknown'
#                 logging.debug(f"Found instance: {inst_name} ({module_type})")
#                 if module_type in lib_cells:
#                     cell_info = lib_cells[module_type]
#                     cell_type = cell_info['type']
#                     if cell_type == 'flip_flop':
#                         components["flip_flops"].append(f"{inst_name} ({module_type})")
#                     elif cell_type == 'gate':
#                         components["gates"].append(f"{inst_name} ({module_type})")
#                     elif cell_type == 'mux':
#                         components["muxes"].append(f"{inst_name} ({module_type})")
#                     elif cell_type == 'switch':
#                         components["switches"].append(f"{inst_name} ({module_type})")
#                     else:
#                         components["instances"].append(f"{inst_name} ({module_type})")
#                 else:
#                     components["instances"].append(f"{inst_name} ({module_type})")
#                     logging.debug(f"Non-standard cell instance: {inst_name} ({module_type})")
#                 connections["instances"][inst_name] = {"module": module_type, "connections": []}
#             # Always blocks for counters and muxes
#             elif sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
#                 block_text = str(sub_member)
#                 if detect_counter(block_text):
#                     components["counters"].append(f"counter_in_{module_name}")
#                 if 'if' in block_text.lower() and 'else' in block_text.lower():
#                     components["muxes"].append(f"mux_in_{module_name}")
#             # Generate blocks
#             elif sub_member.kind == pyslang.SyntaxKind.GenerateBlock:
#                 sub_components, sub_connections = parse_components(sub_member, source_text, port_names, macros, lib_cells)
#                 for comp_type in components:
#                     components[comp_type].extend(sub_components[comp_type])
#                 for wire in sub_connections["wires"]:
#                     connections["wires"][wire] = sub_connections["wires"][wire]
#                 for inst in sub_connections["instances"]:
#                     connections["instances"][inst] = sub_connections["instances"][inst]
#         # Connectivity analysis
#         for sub_member in member.members:
#             if sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
#                 assign_text = str(sub_member)
#                 match = re.search(r'assign\s+(\w+)\s*=\s*([^;]+);', assign_text)
#                 if match:
#                     wire = match.group(1)
#                     source = match.group(2).strip()
#                     if wire in connections["wires"]:
#                         connections["wires"][wire]["source"].append(source)
#             elif sub_member.kind in [getattr(pyslang.SyntaxKind, 'ModuleInstance', None), getattr(pyslang.SyntaxKind, 'Instance', None)]:
#                 inst_name = getattr(sub_member, 'name', None)
#                 inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else 'unknown'
#                 module_type = getattr(sub_member, 'moduleName', None)
#                 module_type = module_type.valueText if module_type and hasattr(module_type, 'valueText') else 'unknown'
#                 if inst_name in connections["instances"]:
#                     for conn in getattr(sub_member, 'connections', []):
#                         local = getattr(conn, 'local', None)
#                         expr = getattr(conn, 'expr', None)
#                         if local and hasattr(local, 'valueText') and expr and hasattr(expr, 'valueText'):
#                             local_port = local.valueText
#                             expr_signal = expr.valueText
#                             connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                             if expr_signal in connections["wires"]:
#                                 connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                             if module_type in lib_cells:
#                                 cell_info = lib_cells[module_type]
#                                 if local_port in cell_info.get('inputs', []):
#                                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                                 elif local_port in cell_info.get('outputs', []):
#                                     connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#         return components, connections
#     except Exception as e:
#         logging.error(f"Error parsing components for module {module_name}: {e}")
#         return components, connections

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells: Dict[str, Dict[str, str]]):
#     module_data = []
#     try:
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, port_names = parse_module_ports(member, macros)
#                 components, connections = parse_components(member, source_text, port_names, macros, lib_cells)
#                 log_section(f"Module: {module_name}", [
#                     f"Ports: {', '.join(ports) if ports else 'None'}",
#                     f"Components: Wires={len(components['wires'])}, Registers={len(components['registers'])}, "
#                     f"Counters={len(components['counters'])}, Flip-Flops={len(components['flip_flops'])}, "
#                     f"Gates={len(components['gates'])}, Muxes={len(components['muxes'])}, "
#                     f"Switches={len(components['switches'])}, Instances={len(components['instances'])}",
#                     f"Connectivity: {len(connections['wires'])} wires, {len(connections['instances'])} instances"
#                 ], detailed_output)
#                 parsed_instances.add(module_name)
#                 module_data.append((module_name, connections, components))
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return module_data



















# import re
# import logging
# import pyslang
# import os
# from utility import detect_counter, log_section
# from typing import Dict, Set, Tuple, List

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     if included_files is None:
#         included_files = set()
#     if file_path in included_files:
#         logging.warning(f"Skipping recursive include of {file_path}")
#         return source_text
#     included_files.add(file_path)
#     include_pattern = re.compile(r'`include\s+"([^"]+)"')
#     while include_pattern.search(source_text):
#         for match in include_pattern.finditer(source_text):
#             include_file = match.group(1)
#             include_path = os.path.join(os.path.dirname(file_path), include_file)
#             logging.debug(f"Processing include: {include_file} -> {include_path}")
#             try:
#                 with open(include_path, 'r', encoding='utf-8') as inc_file:
#                     include_content = inc_file.read()
#                 include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                 source_text = source_text.replace(match.group(0), include_content)
#             except Exception as e:
#                 logging.error(f"Error processing include {include_path}: {e}")
#     for macro_name, macro_value in macros.items():
#         macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#         def replace_macro(match):
#             suffix = match.group(1)
#             try:
#                 if suffix:
#                     return str(int(macro_value) + int(suffix))
#                 return str(macro_value)
#             except ValueError:
#                 return macro_value
#         source_text = macro_pattern.sub(replace_macro, source_text)
#         logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#     debug_path = file_path + ".preprocessed"
#     with open(debug_path, 'w', encoding='utf-8') as f:
#         f.write(source_text)
#     logging.debug(f"Saved preprocessed text to {debug_path}")
#     return source_text

# def get_port_width(port, macros: Dict[str, str], port_text: str = "") -> str:
#     try:
#         # Prefer regex-extracted width from port_text
#         width_match = re.search(r'\[(\d+):(\d+)\]', port_text)
#         if width_match:
#             msb, lsb = width_match.groups()
#             return f"[{msb}:{lsb}]"
#         # pyslang dimensions
#         dimensions = getattr(port, 'dimensions', []) or getattr(getattr(port, 'type', None), 'dimensions', []) or []
#         if dimensions:
#             dim = dimensions[0]
#             msb = str(getattr(dim, 'msb', '') or getattr(dim, 'upper', '') or '')
#             lsb = str(getattr(dim, 'lsb', '') or getattr(dim, 'lower', '') or '')
#             msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
#             lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
#             if msb and lsb:
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer dimension in port: msb={msb}, lsb={lsb}")
#         # Heuristic defaults
#         port_name = port_text or 'unknown'
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[15:0]"
#         if 'clk' in port_name.lower() or 'rst' in port_name.lower() or 'we' in port_name.lower() or 're' in port_name.lower() or 'ack' in port_name.lower() or 'err' in port_name.lower():
#             return ""
#         for macro_name, macro_value in macros.items():
#             if macro_name.lower() in port_name.lower():
#                 try:
#                     width = int(macro_value) - 1
#                     return f"[{width}:0]"
#                 except ValueError:
#                     pass
#         logging.debug(f"Default width for {port_name}: (single-bit)")
#         return ""
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_text}: {e}")
#         return ""

# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     ports = []
#     port_names = set()
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing ports for module: {module_name}")
#         # Log all available SyntaxKind values
#         import pyslang
#         syntax_kinds = [k for k in dir(pyslang.SyntaxKind) if not k.startswith('_')]
#         logging.debug(f"Available SyntaxKind values: {syntax_kinds}")
#         # Log header and member details
#         header_text = str(getattr(member, 'header', ''))
#         logging.debug(f"Module header text: {header_text}")
#         header_ports = getattr(member.header, 'ports', [])
#         logging.debug(f"Header port kinds: {[p.kind for p in header_ports]}")
#         logging.debug(f"Member kinds: {[m.kind for m in member.members]}")
#         # ANSI ports
#         if header_ports:
#             for port in header_ports:
#                 logging.debug(f"Port node kind: {port.kind}, text={str(port)}")
#                 if port.kind == pyslang.SyntaxKind.AnsiPortList:
#                     for sub_port in getattr(port, 'ports', [port]):
#                         name = getattr(sub_port, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             direction = str(getattr(sub_port, 'direction', 'unknown')).lower().split()[0]
#                             data_type = str(getattr(sub_port, 'type', 'wire')).strip() or 'wire'
#                             width = get_port_width(sub_port, macros, name)
#                             ports.append(f"{direction} {data_type}{width} {name}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed ANSI port: {direction} {data_type}{width} {name}")
#         # Non-ANSI ports and other declarations
#         for sub_member in member.members:
#             logging.debug(f"Sub-member kind: {sub_member.kind}, text={str(sub_member)}")
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 direction = str(getattr(sub_member, 'direction', 'unknown')).lower().split()[0]
#                 data_type = str(getattr(sub_member, 'type', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         width = get_port_width(declarator, macros, name)
#                         ports.append(f"{direction} {data_type}{width} {name}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed non-ANSI port: {direction} {data_type}{width} {name}")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 net_type = str(getattr(sub_member, 'netType', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                         if is_port:
#                             direction = "input" if "input" in str(sub_member).lower() else "output" if "output" in str(sub_member).lower() else "inout"
#                             width = get_port_width(declarator, macros, name)
#                             ports.append(f"{direction} {net_type}{width} {name}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed net port: {direction} {net_type}{width} {name}")
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                             if is_port:
#                                 width = get_port_width(declarator, macros, name)
#                                 ports.append(f"output reg{width} {name}")
#                                 port_names.add(name)
#                                 logging.debug(f"Parsed reg port: output reg{width} {name}")
#         # Fallback: Parse ports from raw header text
#         if not ports:
#             # Improved regex to parse full port declarations
#             port_pattern = re.compile(r'(input|output|inout)\s+(wire|reg)?\s*(\[\d+:\d+\])?\s*(\w+)', re.DOTALL)
#             port_matches = port_pattern.findall(header_text)
#             for direction, data_type, width, port_name in port_matches:
#                 data_type = data_type or 'wire'
#                 width = width or get_port_width(None, macros, port_name)
#                 ports.append(f"{direction} {data_type}{width} {port_name}")
#                 port_names.add(port_name)
#                 logging.debug(f"Parsed fallback port: {direction} {data_type}{width} {port_name}")
#         if not ports:
#             logging.warning(f"No ports found for module {module_name}. Check port declarations in source.")
#         return sorted(ports), port_names
#     except Exception as e:
#         logging.error(f"Error parsing ports for module {module_name}: {e}")
#         return ports, port_names

# def parse_components(member, source_text, port_names, macros, lib_cells: Dict[str, Dict[str, str]]):
#     components = {"wires": [], "registers": [], "counters": [], "flip_flops": [], "gates": [], "muxes": [], "instances": [], "switches": []}
#     connections = {"wires": {}, "instances": {}}
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing components for module: {module_name}")
#         for sub_member in member.members:
#             logging.debug(f"Processing sub-member kind: {sub_member.kind}, text={str(sub_member)}")
#             # Wires and registers
#             if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         if name not in port_names:
#                             components["wires"].append(name)
#                             connections["wires"][name] = {"source": [], "sinks": []}
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             if name not in port_names:
#                                 components["registers"].append(name)
#                                 connections["wires"][name] = {"source": [], "sinks": []}
#             # Instances
#             elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
#                 for instance in getattr(sub_member, 'instances', []):
#                     inst_name = getattr(instance, 'name', None)
#                     inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else 'unknown'
#                     module_type = getattr(sub_member, 'name', None)
#                     module_type = module_type.valueText if module_type and hasattr(module_type, 'valueText') else 'unknown'
#                     logging.debug(f"Found instance: {inst_name} ({module_type})")
#                     # Classify if standard cell
#                     classified = False
#                     if module_type in lib_cells:
#                         cell_info = lib_cells[module_type]
#                         cell_type = cell_info['type']
#                         if cell_type == 'flip_flop':
#                             components["flip_flops"].append(f"{inst_name} ({module_type})")
#                             classified = True
#                         elif cell_type == 'gate':
#                             components["gates"].append(f"{inst_name} ({module_type})")
#                             classified = True
#                         elif cell_type == 'mux':
#                             components["muxes"].append(f"{inst_name} ({module_type})")
#                             classified = True
#                         elif cell_type == 'switch':
#                             components["switches"].append(f"{inst_name} ({module_type})")
#                             classified = True
#                     if not classified:
#                         components["instances"].append(f"{inst_name} ({module_type})")
#                     connections["instances"][inst_name] = {"module": module_type, "connections": []}
#                     # Parse connections
#                     for conn in getattr(instance, 'connections', []):
#                         local = getattr(conn, 'name', None)
#                         expr = getattr(conn, 'expr', None)
#                         if local and hasattr(local, 'valueText') and expr and hasattr(expr, 'valueText'):
#                             local_port = local.valueText
#                             expr_signal = expr.valueText
#                             connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                             if expr_signal in connections["wires"]:
#                                 if local_port in cell_info.get('inputs', []) if module_type in lib_cells else True:
#                                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                                 elif local_port in cell_info.get('outputs', []) if module_type in lib_cells else False:
#                                     connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#             # Always blocks for counters and muxes
#             elif sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
#                 block_text = str(sub_member)
#                 if detect_counter(block_text):
#                     components["counters"].append(f"counter_in_{module_name}")
#                 if 'if' in block_text.lower() and 'else' in block_text.lower():
#                     components["muxes"].append(f"mux_in_{module_name}")
#             # Generate blocks
#             elif sub_member.kind == pyslang.SyntaxKind.GenerateBlock:
#                 sub_components, sub_connections = parse_components(sub_member, source_text, port_names, macros, lib_cells)
#                 for comp_type in components:
#                     components[comp_type].extend(sub_components[comp_type])
#                 for wire in sub_connections["wires"]:
#                     connections["wires"][wire] = sub_connections["wires"][wire]
#                 for inst in sub_connections["instances"]:
#                     connections["instances"][inst] = sub_connections["instances"][inst]
#         # Fallback: Parse instances from source_text if pyslang fails
#         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
#         instance_matches = instance_pattern.findall(source_text)
#         for module_type, inst_name, connections_text in instance_matches:
#             # Filter invalid module_type
#             if module_type in {'module', 'begin', 'generate', 'case', 'if', 'always', 'assign', 'wire', 'reg'}:
#                 logging.debug(f"Filtered invalid instance: {inst_name} ({module_type})")
#                 continue
#             logging.debug(f"Parsed instance (regex): {inst_name} ({module_type})")
#             classified = False
#             if module_type in lib_cells:
#                 cell_info = lib_cells[module_type]
#                 cell_type = cell_info['type']
#                 if cell_type == 'flip_flop':
#                     components["flip_flops"].append(f"{inst_name} ({module_type})")
#                     classified = True
#                 elif cell_type == 'gate':
#                     components["gates"].append(f"{inst_name} ({module_type})")
#                     classified = True
#                 elif cell_type == 'mux':
#                     components["muxes"].append(f"{inst_name} ({module_type})")
#                     classified = True
#                 elif cell_type == 'switch':
#                     components["switches"].append(f"{inst_name} ({module_type})")
#                     classified = True
#             if not classified:
#                 components["instances"].append(f"{inst_name} ({module_type})")
#             connections["instances"][inst_name] = {"module": module_type, "connections": []}
#             # Parse instance connections
#             conn_matches = re.findall(r'\.(\w+)\s*\(\s*(\w+)\s*\)', connections_text)
#             for local_port, expr_signal in conn_matches:
#                 connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                 if expr_signal in connections["wires"]:
#                     is_input = local_port in cell_info.get('inputs', []) if module_type in lib_cells else True
#                     if is_input:
#                         connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                     else:
#                         connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#         return components, connections
#     except Exception as e:
#         logging.error(f"Error parsing components for module {module_name}: {e}")
#         return components, connections

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells: Dict[str, Dict[str, str]]):
#     module_data = []
#     try:
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, port_names = parse_module_ports(member, macros)
#                 components, connections = parse_components(member, source_text, port_names, macros, lib_cells)
#                 log_section(f"Module: {module_name}", [
#                     f"Ports: {', '.join(ports) if ports else 'None'}",
#                     f"Components: Wires={len(components['wires'])}, Registers={len(components['registers'])}, "
#                     f"Counters={len(components['counters'])}, Flip-Flops={len(components['flip_flops'])}, "
#                     f"Gates={len(components['gates'])}, Muxes={len(components['muxes'])}, "
#                     f"Switches={len(components['switches'])}, Instances={len(components['instances'])}",
#                     f"Connectivity: {len(connections['wires'])} wires, {len(connections['instances'])} instances"
#                 ], detailed_output)
#                 parsed_instances.add(module_name)
#                 module_data.append((module_name, connections, components))
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return module_data





























# # parser.py
# import re
# import logging
# import pyslang
# import os
# from utility import detect_counter, log_section
# from typing import Dict, Set, Tuple, List

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     # [Existing code unchanged]
#     if included_files is None:
#         included_files = set()
#     if file_path in included_files:
#         logging.warning(f"Skipping recursive include of {file_path}")
#         return source_text
#     included_files.add(file_path)
#     include_pattern = re.compile(r'`include\s+"([^"]+)"')
#     while include_pattern.search(source_text):
#         for match in include_pattern.finditer(source_text):
#             include_file = match.group(1)
#             include_path = os.path.join(os.path.dirname(file_path), include_file)
#             logging.debug(f"Processing include: {include_file} -> {include_path}")
#             try:
#                 with open(include_path, 'r', encoding='utf-8') as inc_file:
#                     include_content = inc_file.read()
#                 include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                 source_text = source_text.replace(match.group(0), include_content)
#             except Exception as e:
#                 logging.error(f"Error processing include {include_path}: {e}")
#     for macro_name, macro_value in macros.items():
#         macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#         def replace_macro(match):
#             suffix = match.group(1)
#             try:
#                 if suffix:
#                     return str(int(macro_value) + int(suffix))
#                 return str(macro_value)
#             except ValueError:
#                 return macro_value
#         source_text = macro_pattern.sub(replace_macro, source_text)
#         logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#     debug_path = file_path + ".preprocessed"
#     with open(debug_path, 'w', encoding='utf-8') as f:
#         f.write(source_text)
#     logging.debug(f"Saved preprocessed text to {debug_path}")
#     return source_text

# def get_port_width(port, macros: Dict[str, str], port_text: str = "") -> str:
#     # [Existing code unchanged]
#     try:
#         width_match = re.search(r'\[(\d+):(\d+)\]', port_text)
#         if width_match:
#             msb, lsb = width_match.groups()
#             return f"[{msb}:{lsb}]"
#         dimensions = getattr(port, 'dimensions', []) or getattr(getattr(port, 'type', None), 'dimensions', []) or []
#         if dimensions:
#             dim = dimensions[0]
#             msb = str(getattr(dim, 'msb', '') or getattr(dim, 'upper', '') or '')
#             lsb = str(getattr(dim, 'lsb', '') or getattr(dim, 'lower', '') or '')
#             msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
#             lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
#             if msb and lsb:
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer dimension in port: msb={msb}, lsb={lsb}")
#         port_name = port_text or 'unknown'
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[15:0]"
#         if 'clk' in port_name.lower() or 'rst' in port_name.lower() or 'we' in port_name.lower() or 're' in port_name.lower() or 'ack' in port_name.lower() or 'err' in port_name.lower():
#             return ""
#         for macro_name, macro_value in macros.items():
#             if macro_name.lower() in port_name.lower():
#                 try:
#                     width = int(macro_value) - 1
#                     return f"[{width}:0]"
#                 except ValueError:
#                     pass
#         logging.debug(f"Default width for {port_name}: (single-bit)")
#         return ""
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_text}: {e}")
#         return ""

# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     # [Existing code unchanged]
#     ports = []
#     port_names = set()
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing ports for module: {module_name}")
#         import pyslang
#         syntax_kinds = [k for k in dir(pyslang.SyntaxKind) if not k.startswith('_')]
#         logging.debug(f"Available SyntaxKind values: {syntax_kinds}")
#         header_text = str(getattr(member, 'header', ''))
#         logging.debug(f"Module header text: {header_text}")
#         header_ports = getattr(member.header, 'ports', [])
#         logging.debug(f"Header port kinds: {[p.kind for p in header_ports]}")
#         logging.debug(f"Member kinds: {[m.kind for m in member.members]}")
#         if header_ports:
#             for port in header_ports:
#                 logging.debug(f"Port node kind: {port.kind}, text={str(port)}")
#                 if port.kind == pyslang.SyntaxKind.AnsiPortList:
#                     for sub_port in getattr(port, 'ports', [port]):
#                         name = getattr(sub_port, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             direction = str(getattr(sub_port, 'direction', 'unknown')).lower().split()[0]
#                             data_type = str(getattr(sub_port, 'type', 'wire')).strip() or 'wire'
#                             width = get_port_width(sub_port, macros, name)
#                             ports.append(f"{direction} {data_type}{width} {name}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed ANSI port: {direction} {data_type}{width} {name}")
#         for sub_member in member.members:
#             logging.debug(f"Sub-member kind: {sub_member.kind}, text={str(sub_member)}")
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 direction = str(getattr(sub_member, 'direction', 'unknown')).lower().split()[0]
#                 data_type = str(getattr(sub_member, 'type', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         width = get_port_width(declarator, macros, name)
#                         ports.append(f"{direction} {data_type}{width} {name}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed non-ANSI port: {direction} {data_type}{width} {name}")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 net_type = str(getattr(sub_member, 'netType', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                         if is_port:
#                             direction = "input" if "input" in str(sub_member).lower() else "output" if "output" in str(sub_member).lower() else "inout"
#                             width = get_port_width(declarator, macros, name)
#                             ports.append(f"{direction} {net_type}{width} {name}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed net port: {direction} {net_type}{width} {name}")
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                             if is_port:
#                                 width = get_port_width(declarator, macros, name)
#                                 ports.append(f"output reg{width} {name}")
#                                 port_names.add(name)
#                                 logging.debug(f"Parsed reg port: output reg{width} {name}")
#         if not ports:
#             port_pattern = re.compile(r'(input|output|inout)\s+(wire|reg)?\s*(\[\d+:\d+\])?\s*(\w+)', re.DOTALL)
#             port_matches = port_pattern.findall(header_text)
#             for direction, data_type, width, port_name in port_matches:
#                 data_type = data_type or 'wire'
#                 width = width or get_port_width(None, macros, port_name)
#                 ports.append(f"{direction} {data_type}{width} {port_name}")
#                 port_names.add(port_name)
#                 logging.debug(f"Parsed fallback port: {direction} {data_type}{width} {port_name}")
#         if not ports:
#             logging.warning(f"No ports found for module {module_name}. Check port declarations in source.")
#         return sorted(ports), port_names
#     except Exception as e:
#         logging.error(f"Error parsing ports for module {module_name}: {e}")
#         return ports, port_names

# def parse_components(member, source_text, port_names, macros, lib_cells: Dict[str, Dict[str, str]], module_names: Set[str]):
#     components = {"wires": [], "registers": [], "counters": [], "flip_flops": [], "gates": [], "muxes": [], "instances": [], "switches": []}
#     connections = {"wires": {}, "instances": {}}
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing components for module: {module_name}")

#         # Parse wires and registers
#         for sub_member in member.members:
#             if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         if name not in port_names:
#                             components["wires"].append(name)
#                             connections["wires"][name] = {"source": [], "sinks": []}
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             if name not in port_names:
#                                 components["registers"].append(name)
#                                 connections["wires"][name] = {"source": [], "sinks": []}

#             # Parse continuous assignments
#             elif sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
#                 for assign in getattr(sub_member, 'assignments', []):
#                     lhs = getattr(assign, 'left', None)
#                     rhs = getattr(assign, 'right', None)
#                     if lhs and rhs and hasattr(lhs, 'valueText'):
#                         lhs_name = lhs.valueText
#                         rhs_signals = []
#                         if hasattr(rhs, 'valueText'):
#                             rhs_signals = [rhs.valueText]
#                         elif rhs.kind == pyslang.SyntaxKind.BinaryExpression:
#                             left = getattr(rhs, 'left', None)
#                             right = getattr(rhs, 'right', None)
#                             if left and right and hasattr(left, 'valueText') and hasattr(right, 'valueText'):
#                                 rhs_signals = [left.valueText, right.valueText]
#                         connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
#                         connections["wires"][lhs_name]["source"].append(str(rhs))
#                         for sig in rhs_signals:
#                             if sig in connections["wires"] or sig in port_names:
#                                 connections["wires"][lhs_name]["sinks"].append(sig)
#                         logging.debug(f"Parsed assign: {lhs_name} = {rhs_signals}")

#             # Parse instances
#             elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
#                 for instance in getattr(sub_member, 'instances', []):
#                     inst_name = getattr(instance, 'name', None)
#                     inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"inst_{len(connections['instances'])}"
#                     module_type_node = getattr(sub_member, 'name', None)
#                     module_type = module_type_node.valueText if module_type_node and hasattr(module_type_node, 'valueText') else None
#                     if not module_type:
#                         # Fallback to parsing source_text for module type
#                         instance_text = str(sub_member)
#                         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\(', re.MULTILINE)
#                         match = instance_pattern.search(instance_text)
#                         module_type = match.group(1) if match else 'unknown'
#                     logging.debug(f"Found instance: {inst_name} ({module_type})")

#                     # Classify instance
#                     classified = False
#                     if module_type in lib_cells:
#                         cell_info = lib_cells[module_type]
#                         cell_type = cell_info['type']
#                         components[cell_type + "s"].append(f"{inst_name} ({module_type})")
#                         classified = True
#                     elif module_type in module_names:
#                         components["instances"].append(f"{inst_name} ({module_type})")
#                         classified = True
#                     if not classified:
#                         logging.warning(f"Unclassified instance: {inst_name} ({module_type})")
#                         components["instances"].append(f"{inst_name} ({module_type})")
#                     connections["instances"][inst_name] = {"module": module_type, "connections": []}

#                     # Parse instance connections
#                     for conn in getattr(instance, 'connections', []):
#                         local = getattr(conn, 'name', None)
#                         expr = getattr(conn, 'expr', None)
#                         if local and expr and hasattr(local, 'valueText') and hasattr(expr, 'valueText'):
#                             local_port = local.valueText
#                             expr_signal = expr.valueText
#                             connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                             connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
#                             if module_type in lib_cells:
#                                 cell_info = lib_cells[module_type]
#                                 if local_port in cell_info.get('inputs', []):
#                                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                                 elif local_port in cell_info.get('outputs', []):
#                                     connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#                             else:
#                                 connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

#             # Parse always blocks for procedural assignments
#             elif sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
#                 block_text = str(sub_member)
#                 if detect_counter(block_text):
#                     components["counters"].append(f"counter_in_{module_name}")
#                 if 'if' in block_text.lower() and 'else' in block_text.lower():
#                     components["muxes"].append(f"mux_in_{module_name}")
#                 for statement in getattr(sub_member, 'statements', []):
#                     if statement.kind in [pyslang.SyntaxKind.AssignStatement, pyslang.SyntaxKind.NonblockingAssign]:
#                         lhs = getattr(statement, 'left', None)
#                         rhs = getattr(statement, 'right', None)
#                         if lhs and rhs and hasattr(lhs, 'valueText'):
#                             lhs_name = lhs.valueText
#                             rhs_signals = []
#                             if hasattr(rhs, 'valueText'):
#                                 rhs_signals = [rhs.valueText]
#                             elif rhs.kind == pyslang.SyntaxKind.BinaryExpression:
#                                 left = getattr(rhs, 'left', None)
#                                 right = getattr(rhs, 'right', None)
#                                 if left and right and hasattr(left, 'valueText') and hasattr(right, 'valueText'):
#                                     rhs_signals = [left.valueText, right.valueText]
#                             connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
#                             connections["wires"][lhs_name]["source"].append(str(rhs))
#                             for sig in rhs_signals:
#                                 if sig in connections["wires"] or sig in port_names:
#                                     connections["wires"][lhs_name]["sinks"].append(sig)
#                             logging.debug(f"Parsed always assign: {lhs_name} = {rhs_signals}")

#         # Fallback regex parsing for instances
#         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
#         instance_matches = instance_pattern.findall(source_text)
#         for module_type, inst_name, connections_text in instance_matches:
#             if module_type in {'module', 'begin', 'generate', 'case', 'if', 'always', 'assign', 'wire', 'reg'}:
#                 logging.debug(f"Filtered invalid instance: {inst_name} ({module_type})")
#                 continue
#             if inst_name not in connections["instances"]:
#                 logging.debug(f"Parsed instance (regex): {inst_name} ({module_type})")
#                 classified = False
#                 if module_type in lib_cells:
#                     cell_info = lib_cells[module_type]
#                     cell_type = cell_info['type']
#                     components[cell_type + "s"].append(f"{inst_name} ({module_type})")
#                     classified = True
#                 elif module_type in module_names:
#                     components["instances"].append(f"{inst_name} ({module_type})")
#                     classified = True
#                 if not classified:
#                     logging.warning(f"Unclassified instance (regex): {inst_name} ({module_type})")
#                     components["instances"].append(f"{inst_name} ({module_type})")
#                 connections["instances"][inst_name] = {"module": module_type, "connections": []}
#                 conn_matches = re.findall(r'\.(\w+)\s*\(\s*(\w+)\s*\)', connections_text)
#                 for local_port, expr_signal in conn_matches:
#                     connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                     connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
#                     if module_type in lib_cells:
#                         cell_info = lib_cells[module_type]
#                         if local_port in cell_info.get('inputs', []):
#                             connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                         elif local_port in cell_info.get('outputs', []):
#                             connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#                     else:
#                         connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

#         return components, connections
#     except Exception as e:
#         logging.error(f"Error parsing components for module {module_name}: {e}")
#         return components, connections

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells: Dict[str, Dict[str, str]]):
#     module_data = []
#     try:
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, port_names = parse_module_ports(member, macros)
#                 components, connections = parse_components(member, source_text, port_names, macros, lib_cells, module_names)
#                 log_section(f"Module: {module_name}", [
#                     f"Ports: {', '.join(ports) if ports else 'None'}",
#                     f"Components: Wires={len(components['wires'])}, Registers={len(components['registers'])}, "
#                     f"Counters={len(components['counters'])}, Flip-Flops={len(components['flip_flops'])}, "
#                     f"Gates={len(components['gates'])}, Muxes={len(components['muxes'])}, "
#                     f"Switches={len(components['switches'])}, Instances={len(components['instances'])}",
#                     f"Connectivity: {len(connections['wires'])} wires, {len(connections['instances'])} instances"
#                 ], detailed_output)
#                 parsed_instances.add(module_name)
#                 module_data.append((module_name, connections, components))
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return module_data















# import logging
# import re
# import pyslang

# def parse_module_ports(member, macros):
#     try:
#         ports = []
#         connections = {"wires": {}, "instances": {}}
#         for port in member.ports:
#             direction = port.direction.text.lower() if hasattr(port, 'direction') else 'unknown'
#             data_type = port.type.text if hasattr(port, 'type') else 'wire'
#             width = port.dimensions.text if hasattr(port, 'dimensions') else '1'
#             name = port.name.text if hasattr(port, 'name') else 'unknown'
#             ports.append(f"{direction} {data_type}{width} {name}")
#         logging.debug(f"Parsed ports for module {member.header.name.valueText}: {ports}")
#         return ports, connections
#     except Exception as e:
#         logging.error(f"Error parsing module ports: {e}")
#         return [], connections

# def parse_components(member, source_text, macros, lib_cells):
#     try:
#         components = {
#             "wires": [],
#             "registers": [],
#             "counters": [],
#             "flip_flops": [],
#             "gates": [],
#             "muxes": [],
#             "instances": [],
#             "switches": []
#         }
#         connections = {"wires": {}, "instances": {}}

#         def extract_name(node):
#             return node.name.text if hasattr(node, 'name') and node.name else 'unknown'

#         def add_connection(wire, source=None, sink=None):
#             if wire not in connections["wires"]:
#                 connections["wires"][wire] = {"source": [], "sinks": []}
#             if source:
#                 connections["wires"][wire]["source"].append(source)
#             if sink:
#                 connections["wires"][wire]["sinks"].append(sink)

#         for item in member.members:
#             if item.kind == pyslang.SyntaxKind.WireDeclaration:
#                 wire_name = extract_name(item)
#                 components["wires"].append(wire_name)
#                 add_connection(wire_name)
#                 logging.debug(f"Found wire: {wire_name}")
#             elif item.kind == pyslang.SyntaxKind.RegisterDeclaration:
#                 reg_name = extract_name(item)
#                 components["registers"].append(reg_name)
#                 add_connection(reg_name)
#                 logging.debug(f"Found register: {reg_name}")
#             elif item.kind == pyslang.SyntaxKind.Instance:
#                 inst_name = extract_name(item)
#                 module_name = item.module.text if hasattr(item, 'module') else 'unknown'
#                 components["instances"].append(f"{inst_name} ({module_name})")
#                 connections["instances"][inst_name] = {"module": module_name}
#                 logging.debug(f"Found instance: {inst_name} ({module_name})")
#             elif item.kind == pyslang.SyntaxKind.GenerateBlock:
#                 # Handle generate blocks for instances like ctrl[0:14]
#                 for gen_item in item.members:
#                     if gen_item.kind == pyslang.SyntaxKind.Instance:
#                         inst_name = extract_name(gen_item)
#                         module_name = gen_item.module.text if hasattr(gen_item, 'module') else 'unknown'
#                         # Extract generate index if available
#                         if hasattr(item, 'name') and item.name.text:
#                             gen_index = item.name.text
#                             inst_name = f"{inst_name}[{gen_index}]"
#                         components["instances"].append(f"{inst_name} ({module_name})")
#                         connections["instances"][inst_name] = {"module": module_name}
#                         logging.debug(f"Found generate instance: {inst_name} ({module_name})")
#             elif item.kind == pyslang.SyntaxKind.AlwaysBlock:
#                 block_text = source_text[item.location.offset:item.location.offset + item.location.length]
#                 if "counter" in block_text.lower() or detect_counter(block_text):
#                     components["counters"].append(f"counter_in_{member.header.name.valueText}")
#                     logging.debug(f"Found counter in always block")
#                 elif "ff" in block_text.lower():
#                     components["flip_flops"].append(f"ff_in_{member.header.name.valueText}")
#                     logging.debug(f"Found flip-flop in always block")

#         # Check for gates and muxes from library cells
#         for inst_name, inst in connections["instances"].items():
#             if inst["module"] in lib_cells:
#                 cell = lib_cells[inst["module"]]
#                 if cell["type"] == "gate":
#                     components["gates"].append(f"{inst_name} ({inst['module']})")
#                     logging.debug(f"Found gate: {inst_name} ({inst['module']})")
#                 elif "mux" in inst["module"].lower():
#                     components["muxes"].append(f"{inst_name} ({inst['module']})")
#                     logging.debug(f"Found mux: {inst_name} ({inst['module']})")
#                 elif "tran" in inst["module"].lower():
#                     components["switches"].append(f"{inst_name} ({inst['module']})")
#                     logging.debug(f"Found switch: {inst_name} ({inst['module']})")

#         logging.debug(f"Components for module {member.header.name.valueText}: {components}")
#         return components, connections
#     except Exception as e:
#         logging.error(f"Error parsing components: {e}")
#         return components, connections

# def preprocess_verilog(file_path, source_text, macros):
#     try:
#         for macro, value in macros.items():
#             source_text = re.sub(rf'`{macro}\b', value, source_text)
#         logging.debug(f"Preprocessed Verilog file: {file_path}")
#         return source_text
#     except Exception as e:
#         logging.error(f"Error preprocessing Verilog: {e}")
#         return source_text

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells):
#     try:
#         module_data = []
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = member.header.name.valueText if hasattr(member.header, 'name') else 'unknown'
#                 if module_name == 'unknown':
#                     logging.warning(f"Skipping module with no name in {file_path}")
#                     continue
#                 ports, connections = parse_module_ports(member, macros)
#                 components, connections = parse_components(member, source_text, macros, lib_cells)
#                 module_data.append((module_name, connections, components))
#                 parsed_instances.add(module_name)
#                 logging.info(f"Processed module {module_name} in {file_path}")
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return []








# # updated1
# # identifies counters, registers, muxes, and gates in both .v files (Verilog/SystemVerilog files) and .lib files (library files)

# # parser.py
# import re
# import logging
# import pyslang
# import os
# from utility import detect_counter, log_section
# from typing import Dict, Set, Tuple, List

# def preprocess_verilog(file_path, source_text, macros, included_files=None):
#     if included_files is None:
#         included_files = set()
#     if file_path in included_files:
#         logging.warning(f"Skipping recursive include of {file_path}")
#         return source_text
#     included_files.add(file_path)
#     include_pattern = re.compile(r'`include\s+"([^"]+)"')
#     while include_pattern.search(source_text):
#         for match in include_pattern.finditer(source_text):
#             include_file = match.group(1)
#             include_path = os.path.join(os.path.dirname(file_path), include_file)
#             logging.debug(f"Processing include: {include_file} -> {include_path}")
#             try:
#                 with open(include_path, 'r', encoding='utf-8') as inc_file:
#                     include_content = inc_file.read()
#                 include_content = preprocess_verilog(include_path, include_content, macros, included_files)
#                 source_text = source_text.replace(match.group(0), include_content)
#             except Exception as e:
#                 logging.error(f"Error processing include {include_path}: {e}")
#     for macro_name, macro_value in macros.items():
#         macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
#         def replace_macro(match):
#             suffix = match.group(1)
#             try:
#                 if suffix:
#                     return str(int(macro_value) + int(suffix))
#                 return str(macro_value)
#             except ValueError:
#                 return macro_value
#         source_text = macro_pattern.sub(replace_macro, source_text)
#         logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")
#     debug_path = file_path + ".preprocessed"
#     with open(debug_path, 'w', encoding='utf-8') as f:
#         f.write(source_text)
#     logging.debug(f"Saved preprocessed text to {debug_path}")
#     return source_text

# def get_port_width(port, macros: Dict[str, str], port_text: str = "") -> str:
#     try:
#         width_match = re.search(r'\[(\d+):(\d+)\]', port_text)
#         if width_match:
#             msb, lsb = width_match.groups()
#             return f"[{msb}:{lsb}]"
#         dimensions = getattr(port, 'dimensions', []) or getattr(getattr(port, 'type', None), 'dimensions', []) or []
#         if dimensions:
#             dim = dimensions[0]
#             msb = str(getattr(dim, 'msb', '') or getattr(dim, 'upper', '') or '')
#             lsb = str(getattr(dim, 'lsb', '') or getattr(dim, 'lower', '') or '')
#             msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
#             lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
#             if msb and lsb:
#                 try:
#                     msb, lsb = int(msb), int(lsb)
#                     return f"[{msb}:{lsb}]"
#                 except ValueError:
#                     logging.warning(f"Non-integer dimension in port: msb={msb}, lsb={lsb}")
#         port_name = port_text or 'unknown'
#         if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
#             return "[31:0]"
#         if 'addr' in port_name.lower():
#             return "[15:0]"
#         if 'clk' in port_name.lower() or 'rst' in port_name.lower() or 'we' in port_name.lower() or 're' in port_name.lower() or 'ack' in port_name.lower() or 'err' in port_name.lower():
#             return ""
#         for macro_name, macro_value in macros.items():
#             if macro_name.lower() in port_name.lower():
#                 try:
#                     width = int(macro_value) - 1
#                     return f"[{width}:0]"
#                 except ValueError:
#                     pass
#         logging.debug(f"Default width for {port_name}: (single-bit)")
#         return ""
#     except Exception as e:
#         logging.error(f"Error extracting port width for {port_text}: {e}")
#         return ""

# def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
#     ports = []
#     port_names = set()
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing ports for module: {module_name}")
#         import pyslang
#         syntax_kinds = [k for k in dir(pyslang.SyntaxKind) if not k.startswith('_')]
#         logging.debug(f"Available SyntaxKind values: {syntax_kinds}")
#         header_text = str(getattr(member, 'header', ''))
#         logging.debug(f"Module header text: {header_text}")
#         header_ports = getattr(member.header, 'ports', [])
#         logging.debug(f"Header port kinds: {[p.kind for p in header_ports]}")
#         logging.debug(f"Member kinds: {[m.kind for m in member.members]}")
#         if header_ports:
#             for port in header_ports:
#                 logging.debug(f"Port node kind: {port.kind}, text={str(port)}")
#                 if port.kind == pyslang.SyntaxKind.AnsiPortList:
#                     for sub_port in getattr(port, 'ports', [port]):
#                         name = getattr(sub_port, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             direction = str(getattr(sub_port, 'direction', 'unknown')).lower().split()[0]
#                             data_type = str(getattr(sub_port, 'type', 'wire')).strip() or 'wire'
#                             width = get_port_width(sub_port, macros, name)
#                             ports.append(f"{direction} {data_type}{width} {name}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed ANSI port: {direction} {data_type}{width} {name}")
#         for sub_member in member.members:
#             logging.debug(f"Sub-member kind: {sub_member.kind}, text={str(sub_member)}")
#             if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
#                 direction = str(getattr(sub_member, 'direction', 'unknown')).lower().split()[0]
#                 data_type = str(getattr(sub_member, 'type', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         width = get_port_width(declarator, macros, name)
#                         ports.append(f"{direction} {data_type}{width} {name}")
#                         port_names.add(name)
#                         logging.debug(f"Parsed non-ANSI port: {direction} {data_type}{width} {name}")
#             elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 net_type = str(getattr(sub_member, 'netType', 'wire')).strip() or 'wire'
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                         if is_port:
#                             direction = "input" if "input" in str(sub_member).lower() else "output" if "output" in str(sub_member).lower() else "inout"
#                             width = get_port_width(declarator, macros, name)
#                             ports.append(f"{direction} {net_type}{width} {name}")
#                             port_names.add(name)
#                             logging.debug(f"Parsed net port: {direction} {net_type}{width} {name}")
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
#                             if is_port:
#                                 width = get_port_width(declarator, macros, name)
#                                 ports.append(f"output reg{width} {name}")
#                                 port_names.add(name)
#                                 logging.debug(f"Parsed reg port: output reg{width} {name}")
#         if not ports:
#             port_pattern = re.compile(r'(input|output|inout)\s+(wire|reg)?\s*(\[\d+:\d+\])?\s*(\w+)', re.DOTALL)
#             port_matches = port_pattern.findall(header_text)
#             for direction, data_type, width, port_name in port_matches:
#                 data_type = data_type or 'wire'
#                 width = width or get_port_width(None, macros, port_name)
#                 ports.append(f"{direction} {data_type}{width} {port_name}")
#                 port_names.add(port_name)
#                 logging.debug(f"Parsed fallback port: {direction} {data_type}{width} {port_name}")
#         if not ports:
#             logging.warning(f"No ports found for module {module_name}. Check port declarations in source.")
#         return sorted(ports), port_names
#     except Exception as e:
#         logging.error(f"Error parsing ports for module {module_name}: {e}")
#         return ports, port_names

# def parse_components(member, source_text, port_names, macros, lib_cells: Dict[str, Dict[str, any]], module_names: Set[str]):
#     components = {"wires": [], "registers": [], "counters": [], "flip_flops": [], "gates": [], "muxes": [], "instances": [], "switches": []}
#     connections = {"wires": {}, "instances": {}}
#     try:
#         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
#         logging.debug(f"Parsing components for module: {module_name}")

#         # Parse wires and registers
#         for sub_member in member.members:
#             if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
#                 for declarator in getattr(sub_member, 'declarators', []):
#                     name = getattr(declarator, 'name', None)
#                     if name and hasattr(name, 'valueText'):
#                         name = name.valueText
#                         if name not in port_names:
#                             components["wires"].append(name)
#                             connections["wires"][name] = {"source": [], "sinks": []}
#             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
#                 if 'reg' in str(sub_member).lower():
#                     for declarator in getattr(sub_member, 'declarators', []):
#                         name = getattr(declarator, 'name', None)
#                         if name and hasattr(name, 'valueText'):
#                             name = name.valueText
#                             if name not in port_names:
#                                 components["registers"].append(name)
#                                 connections["wires"][name] = {"source": [], "sinks": []}

#             # Parse continuous assignments
#             elif sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
#                 for assign in getattr(sub_member, 'assignments', []):
#                     lhs = getattr(assign, 'left', None)
#                     rhs = getattr(assign, 'right', None)
#                     if lhs and rhs and hasattr(lhs, 'valueText'):
#                         lhs_name = lhs.valueText
#                         rhs_signals = []
#                         def extract_signals(node):
#                             if hasattr(node, 'valueText'):
#                                 return [node.valueText]
#                             elif node.kind == pyslang.SyntaxKind.BinaryExpression:
#                                 left = getattr(node, 'left', None)
#                                 right = getattr(node, 'right', None)
#                                 signals = []
#                                 if left:
#                                     signals.extend(extract_signals(left))
#                                 if right:
#                                     signals.extend(extract_signals(right))
#                                 return []
#                             elif node.kind == pyslang.SyntaxKind.ElementSelect:
#                                 base = getattr(node, 'expr', None)
#                                 if base and hasattr(base, 'valueText'):
#                                     return [base.valueText]
#                                 return []
#                         rhs_signals = extract_signals(rhs)
#                         connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
#                         connections["wires"][lhs_name]["source"].append(str(rhs))
#                         for sig in rhs_signals:
#                             if sig in connections["wires"] or sig in port_names:
#                                 connections["wires"][lhs_name]["sinks"].append(sig)
#                         logging.debug(f"Parsed assign: {lhs_name} = {rhs_signals}")

#             # Parse instances
#             elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
#                 for instance in getattr(sub_member, 'instances', []):
#                     inst_name = getattr(instance, 'name', None)
#                     inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"inst_{len(connections['instances'])}"
#                     module_type_node = getattr(sub_member, 'name', None)
#                     module_type = module_type_node.valueText if module_type_node and hasattr(module_type_node, 'valueText') else None
#                     if not module_type:
#                         instance_text = str(sub_member)
#                         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\(', re.MULTILINE)
#                         match = instance_pattern.search(instance_text)
#                         module_type = match.group(1) if match else 'unknown'
#                     logging.debug(f"Found instance: {inst_name} ({module_type})")
#                     if inst_name in connections["instances"]:
#                         logging.debug(f"Skipping duplicate instance: {inst_name} ({module_type})")
#                         continue
#                     classified = False
#                     if module_type in lib_cells:
#                         cell_info = lib_cells[module_type]
#                         cell_type = cell_info['type']
#                         components[cell_type + "s"].append(f"{inst_name} ({module_type})")
#                         classified = True
#                     elif module_type in module_names:
#                         components["instances"].append(f"{inst_name} ({module_type})")
#                         classified = True
#                     if not classified:
#                         logging.warning(f"Unclassified instance: {inst_name} ({module_type})")
#                         components["instances"].append(f"{inst_name} ({module_type})")
#                     connections["instances"][inst_name] = {"module": module_type, "connections": []}
#                     for conn in getattr(instance, 'connections', []):
#                         local = getattr(conn, 'name', None)
#                         expr = getattr(conn, 'expr', None)
#                         if local and expr and hasattr(local, 'valueText') and hasattr(expr, 'valueText'):
#                             local_port = local.valueText
#                             expr_signal = expr.valueText
#                             connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                             connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
#                             if module_type in lib_cells:
#                                 cell_info = lib_cells[module_type]
#                                 if local_port in cell_info.get('inputs', []):
#                                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                                 elif local_port in cell_info.get('outputs', []):
#                                     connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#                             else:
#                                 connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

#             # Parse always blocks for procedural assignments and behavioral flip-flops
#             elif sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
#                 block_text = str(sub_member)
#                 if detect_counter(block_text):
#                     components["counters"].append(f"counter_in_{module_name}")
#                 if 'if' in block_text.lower() and 'else' in block_text.lower():
#                     components["muxes"].append(f"mux_in_{module_name}")
#                 if '@(posedge' in block_text.lower() or '@(negedge' in block_text.lower():
#                     components["flip_flops"].append(f"ff_in_{module_name}")
#                     logging.debug(f"Detected behavioral flip-flop in {module_name}")
#                 for statement in getattr(sub_member, 'statements', []):
#                     if statement.kind in [pyslang.SyntaxKind.AssignStatement, pyslang.SyntaxKind.NonblockingAssign]:
#                         lhs = getattr(statement, 'left', None)
#                         rhs = getattr(statement, 'right', None)
#                         if lhs and rhs and hasattr(lhs, 'valueText'):
#                             lhs_name = lhs.valueText
#                             rhs_signals = []
#                             def extract_signals(node):
#                                 if hasattr(node, 'valueText'):
#                                     return [node.valueText]
#                                 elif node.kind == pyslang.SyntaxKind.BinaryExpression:
#                                     left = getattr(node, 'left', None)
#                                     right = getattr(node, 'right', None)
#                                     signals = []
#                                     if left:
#                                         signals.extend(extract_signals(left))
#                                     if right:
#                                         signals.extend(extract_signals(right))
#                                     return []
#                                 elif node.kind == pyslang.SyntaxKind.ElementSelect:
#                                     base = getattr(node, 'expr', None)
#                                     if base and hasattr(base, 'valueText'):
#                                         return [base.valueText]
#                                     return []
#                             rhs_signals = extract_signals(rhs)
#                             connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
#                             connections["wires"][lhs_name]["source"].append(str(rhs))
#                             for sig in rhs_signals:
#                                 if sig in connections["wires"] or sig in port_names:
#                                     connections["wires"][lhs_name]["sinks"].append(sig)
#                             logging.debug(f"Parsed always assign: {lhs_name} = {rhs_signals}")

#         # Fallback regex for registers
#         reg_pattern = re.compile(r'reg\s*(\[\d+:\d+\])?\s*(\w+)\s*;', re.DOTALL)
#         reg_matches = reg_pattern.findall(source_text)
#         for width, name in reg_matches:
#             if name not in port_names and name not in components["registers"]:
#                 components["registers"].append(name)
#                 connections["wires"].setdefault(name, {"source": [], "sinks": []})
#                 logging.debug(f"Parsed register (regex): {name}")

#         # Fallback regex for instances
#         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
#         instance_matches = instance_pattern.findall(source_text)
#         for module_type, inst_name, connections_text in instance_matches:
#             if module_type in {'module', 'begin', 'generate', 'case', 'if', 'always', 'assign', 'wire', 'reg'}:
#                 logging.debug(f"Filtered invalid instance: {inst_name} ({module_type})")
#                 continue
#             if inst_name in connections["instances"]:
#                 logging.debug(f"Skipping duplicate instance (regex): {inst_name} ({module_type})")
#                 continue
#             logging.debug(f"Parsed instance (regex): {inst_name} ({module_type})")
#             classified = False
#             if module_type in lib_cells:
#                 cell_info = lib_cells[module_type]
#                 cell_type = cell_info['type']
#                 components[cell_type + "s"].append(f"{inst_name} ({module_type})")
#                 classified = True
#             elif module_type in module_names:
#                 components["instances"].append(f"{inst_name} ({module_type})")
#                 classified = True
#             if not classified:
#                 logging.warning(f"Unclassified instance (regex): {inst_name} ({module_type})")
#                 components["instances"].append(f"{inst_name} ({module_type})")
#             connections["instances"][inst_name] = {"module": module_type, "connections": []}
#             conn_matches = re.findall(r'\.(\w+)\s*\(\s*(\w+)\s*\)', connections_text)
#             for local_port, expr_signal in conn_matches:
#                 connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
#                 connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
#                 if module_type in lib_cells:
#                     cell_info = lib_cells[module_type]
#                     if local_port in cell_info.get('inputs', []):
#                         connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
#                     elif local_port in cell_info.get('outputs', []):
#                         connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
#                 else:
#                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

#         return components, connections
#     except Exception as e:
#         logging.error(f"Error parsing components for module {module_name}: {e}")
#         return components, connections

# # def parse_components(member, source_text, port_names, macros, lib_cells: Dict[str, Dict[str, str]], module_names: Set[str]):
# #     components = {"wires": [], "registers": [], "counters": [], "flip_flops": [], "gates": [], "muxes": [], "instances": [], "switches": []}
# #     connections = {"wires": {}, "instances": {}}
# #     try:
# #         module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
# #         logging.debug(f"Parsing components for module: {module_name}")

# #         # Parse wires and registers
# #         for sub_member in member.members:
# #             if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
# #                 for declarator in getattr(sub_member, 'declarators', []):
# #                     name = getattr(declarator, 'name', None)
# #                     if name and hasattr(name, 'valueText'):
# #                         name = name.valueText
# #                         if name not in port_names:
# #                             components["wires"].append(name)
# #                             connections["wires"][name] = {"source": [], "sinks": []}
# #             elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
# #                 if 'reg' in str(sub_member).lower():
# #                     for declarator in getattr(sub_member, 'declarators', []):
# #                         name = getattr(declarator, 'name', None)
# #                         if name and hasattr(name, 'valueText'):
# #                             name = name.valueText
# #                             if name not in port_names:
# #                                 components["registers"].append(name)
# #                                 connections["wires"][name] = {"source": [], "sinks": []}

# #             # Parse continuous assignments
# #             elif sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
# #                 for assign in getattr(sub_member, 'assignments', []):
# #                     lhs = getattr(assign, 'left', None)
# #                     rhs = getattr(assign, 'right', None)
# #                     if lhs and rhs and hasattr(lhs, 'valueText'):
# #                         lhs_name = lhs.valueText
# #                         rhs_signals = []
# #                         def extract_signals(node):
# #                             if hasattr(node, 'valueText'):
# #                                 return [node.valueText]
# #                             elif node.kind == pyslang.SyntaxKind.BinaryExpression:
# #                                 left = getattr(node, 'left', None)
# #                                 right = getattr(node, 'right', None)
# #                                 signals = []
# #                                 if left:
# #                                     signals.extend(extract_signals(left))
# #                                 if right:
# #                                     signals.extend(extract_signals(right))
# #                                 return signals
# #                             elif node.kind == pyslang.SyntaxKind.ElementSelect:
# #                                 base = getattr(node, 'expr', None)
# #                                 if base and hasattr(base, 'valueText'):
# #                                     return [base.valueText]
# #                                 return []
# #                         rhs_signals = extract_signals(rhs)
# #                         connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
# #                         connections["wires"][lhs_name]["source"].append(str(rhs))
# #                         for sig in rhs_signals:
# #                             if sig in connections["wires"] or sig in port_names:
# #                                 connections["wires"][lhs_name]["sinks"].append(sig)
# #                         logging.debug(f"Parsed assign: {lhs_name} = {rhs_signals}")

# #             # Parse instances
# #             elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
# #                 for instance in getattr(sub_member, 'instances', []):
# #                     inst_name = getattr(instance, 'name', None)
# #                     inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"inst_{len(connections['instances'])}"
# #                     module_type_node = getattr(sub_member, 'name', None)
# #                     module_type = module_type_node.valueText if module_type_node and hasattr(module_type_node, 'valueText') else None
# #                     if not module_type:
# #                         instance_text = str(sub_member)
# #                         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\(', re.MULTILINE)
# #                         match = instance_pattern.search(instance_text)
# #                         module_type = match.group(1) if match else 'unknown'
# #                     logging.debug(f"Found instance: {inst_name} ({module_type})")
# #                     if inst_name in connections["instances"]:
# #                         logging.debug(f"Skipping duplicate instance: {inst_name} ({module_type})")
# #                         continue
# #                     classified = False
# #                     if module_type in lib_cells:
# #                         cell_info = lib_cells[module_type]
# #                         cell_type = cell_info['type']
# #                         components[cell_type + "s"].append(f"{inst_name} ({module_type})")
# #                         classified = True
# #                     elif module_type in module_names:
# #                         components["instances"].append(f"{inst_name} ({module_type})")
# #                         classified = True
# #                     if not classified:
# #                         logging.warning(f"Unclassified instance: {inst_name} ({module_type})")
# #                         components["instances"].append(f"{inst_name} ({module_type})")
# #                     connections["instances"][inst_name] = {"module": module_type, "connections": []}
# #                     for conn in getattr(instance, 'connections', []):
# #                         local = getattr(conn, 'name', None)
# #                         expr = getattr(conn, 'expr', None)
# #                         if local and expr and hasattr(local, 'valueText') and hasattr(expr, 'valueText'):
# #                             local_port = local.valueText
# #                             expr_signal = expr.valueText
# #                             connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
# #                             connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
# #                             if module_type in lib_cells:
# #                                 cell_info = lib_cells[module_type]
# #                                 if local_port in cell_info.get('inputs', []):
# #                                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
# #                                 elif local_port in cell_info.get('outputs', []):
# #                                     connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
# #                             else:
# #                                 connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

# #             # Parse always blocks for procedural assignments
# #             elif sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
# #                 block_text = str(sub_member)
# #                 if detect_counter(block_text):
# #                     components["counters"].append(f"counter_in_{module_name}")
# #                 if 'if' in block_text.lower() and 'else' in block_text.lower():
# #                     components["muxes"].append(f"mux_in_{module_name}")
# #                 for statement in getattr(sub_member, 'statements', []):
# #                     if statement.kind in [pyslang.SyntaxKind.AssignStatement, pyslang.SyntaxKind.NonblockingAssign]:
# #                         lhs = getattr(statement, 'left', None)
# #                         rhs = getattr(statement, 'right', None)
# #                         if lhs and rhs and hasattr(lhs, 'valueText'):
# #                             lhs_name = lhs.valueText
# #                             rhs_signals = []
# #                             def extract_signals(node):
# #                                 if hasattr(node, 'valueText'):
# #                                     return [node.valueText]
# #                                 elif node.kind == pyslang.SyntaxKind.BinaryExpression:
# #                                     left = getattr(node, 'left', None)
# #                                     right = getattr(node, 'right', None)
# #                                     signals = []
# #                                     if left:
# #                                         signals.extend(extract_signals(left))
# #                                     if right:
# #                                         signals.extend(extract_signals(right))
# #                                     return signals
# #                                 elif node.kind == pyslang.SyntaxKind.ElementSelect:
# #                                     base = getattr(node, 'expr', None)
# #                                     if base and hasattr(base, 'valueText'):
# #                                         return [base.valueText]
# #                                     return []
# #                             rhs_signals = extract_signals(rhs)
# #                             connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
# #                             connections["wires"][lhs_name]["source"].append(str(rhs))
# #                             for sig in rhs_signals:
# #                                 if sig in connections["wires"] or sig in port_names:
# #                                     connections["wires"][lhs_name]["sinks"].append(sig)
# #                             logging.debug(f"Parsed always assign: {lhs_name} = {rhs_signals}")

# #         # Fallback regex parsing for instances, with duplicate check
# #         instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
# #         instance_matches = instance_pattern.findall(source_text)
# #         for module_type, inst_name, connections_text in instance_matches:
# #             if module_type in {'module', 'begin', 'generate', 'case', 'if', 'always', 'assign', 'wire', 'reg'}:
# #                 logging.debug(f"Filtered invalid instance: {inst_name} ({module_type})")
# #                 continue
# #             if inst_name in connections["instances"]:
# #                 logging.debug(f"Skipping duplicate instance (regex): {inst_name} ({module_type})")
# #                 continue
# #             logging.debug(f"Parsed instance (regex): {inst_name} ({module_type})")
# #             classified = False
# #             if module_type in lib_cells:
# #                 cell_info = lib_cells[module_type]
# #                 cell_type = cell_info['type']
# #                 components[cell_type + "s"].append(f"{inst_name} ({module_type})")
# #                 classified = True
# #             elif module_type in module_names:
# #                 components["instances"].append(f"{inst_name} ({module_type})")
# #                 classified = True
# #             if not classified:
# #                 logging.warning(f"Unclassified instance (regex): {inst_name} ({module_type})")
# #                 components["instances"].append(f"{inst_name} ({module_type})")
# #             connections["instances"][inst_name] = {"module": module_type, "connections": []}
# #             conn_matches = re.findall(r'\.(\w+)\s*\(\s*(\w+)\s*\)', connections_text)
# #             for local_port, expr_signal in conn_matches:
# #                 connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
# #                 connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
# #                 if module_type in lib_cells:
# #                     cell_info = lib_cells[module_type]
# #                     if local_port in cell_info.get('inputs', []):
# #                         connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
# #                     elif local_port in cell_info.get('outputs', []):
# #                         connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
# #                 else:
# #                     connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

# #         return components, connections
# #     except Exception as e:
# #         logging.error(f"Error parsing components for module {module_name}: {e}")
# #         return components, connections

# def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells: Dict[str, Dict[str, str]]):
#     module_data = []
#     try:
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, port_names = parse_module_ports(member, macros)
#                 components, connections = parse_components(member, source_text, port_names, macros, lib_cells, module_names)
#                 total_instances = len(components["instances"]) + len(components["flip_flops"]) + len(components["gates"])
#                 log_section(f"Module: {module_name}", [
#                     f"Ports: {', '.join(ports) if ports else 'None'}",
#                     f"Components: Wires={len(components['wires'])}, Registers={len(components['registers'])}, "
#                     f"Counters={len(components['counters'])}, Flip-Flops={len(components['flip_flops'])}, "
#                     f"Gates={len(components['gates'])}, Muxes={len(components['muxes'])}, "
#                     f"Switches={len(components['switches'])}, Instances={total_instances}",
#                     f"Connectivity: {len(connections['wires'])} wires, {len(connections['instances'])} instances"
#                 ], detailed_output)
#                 parsed_instances.add(module_name)
#                 module_data.append((module_name, connections, components))
#         return module_data
#     except Exception as e:
#         logging.error(f"Error processing file {file_path}: {e}")
#         return module_data






# updated2



# parser.py
import re
import logging
import pyslang
import os
from .utility import detect_counter, log_section
from typing import Dict, Set, Tuple, List

# Cache for preprocessed Verilog text
_preprocess_cache = {}

def preprocess_verilog(file_path, source_text, macros, included_files=None):
    if included_files is None:
        included_files = set()
    if file_path in included_files:
        logging.warning(f"Skipping recursive include of {file_path}")
        return source_text
    included_files.add(file_path)

    # Check cache
    cache_key = (file_path, tuple(sorted(macros.items())))
    if cache_key in _preprocess_cache:
        logging.debug(f"Using cached preprocessed text for {file_path}")
        return _preprocess_cache[cache_key]

    include_pattern = re.compile(r'`include\s+"([^"]+)"')
    while include_pattern.search(source_text):
        for match in include_pattern.finditer(source_text):
            include_file = match.group(1)
            include_path = os.path.join(os.path.dirname(file_path), include_file)
            logging.debug(f"Processing include: {include_file} -> {include_path}")
            try:
                with open(include_path, 'r', encoding='utf-8') as inc_file:
                    include_content = inc_file.read()
                include_content = preprocess_verilog(include_path, include_content, macros, included_files)
                source_text = source_text.replace(match.group(0), include_content)
            except FileNotFoundError:
                logging.error(f"Include file {include_path} not found")
                continue
            except Exception as e:
                logging.error(f"Error processing include {include_path}: {e}")
                continue

    for macro_name, macro_value in macros.items():
        macro_pattern = re.compile(r'`' + re.escape(macro_name) + r'([-]?\d*)')
        def replace_macro(match):
            suffix = match.group(1)
            try:
                if suffix:
                    return str(int(macro_value) + int(suffix))
                return str(macro_value)
            except ValueError:
                return macro_value
        source_text = macro_pattern.sub(replace_macro, source_text)
        logging.debug(f"Replaced macro `{macro_name}` with `{macro_value}` in {file_path}")

    debug_path = file_path + ".preprocessed"
    try:
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(source_text)
        logging.debug(f"Saved preprocessed text to {debug_path}")
    except Exception as e:
        logging.error(f"Error saving preprocessed text to {debug_path}: {e}")

    # Store in cache
    _preprocess_cache[cache_key] = source_text
    return source_text

def get_port_width(port, macros: Dict[str, str], port_text: str = "") -> str:
    try:
        width_match = re.search(r'\[(\d+):(\d+)\]', port_text)
        if width_match:
            msb, lsb = width_match.groups()
            return f"[{msb}:{lsb}]"
        dimensions = getattr(port, 'dimensions', []) or getattr(getattr(port, 'type', None), 'dimensions', []) or []
        if dimensions:
            dim = dimensions[0]
            msb = str(getattr(dim, 'msb', '') or getattr(dim, 'upper', '') or '')
            lsb = str(getattr(dim, 'lsb', '') or getattr(dim, 'lower', '') or '')
            msb = macros.get(msb.strip('`'), msb) if msb.startswith('`') else msb
            lsb = macros.get(lsb.strip('`'), lsb) if lsb.startswith('`') else lsb
            if msb and lsb:
                try:
                    msb, lsb = int(msb), int(lsb)
                    return f"[{msb}:{lsb}]"
                except ValueError:
                    logging.warning(f"Non-integer dimension in port: msb={msb}, lsb={lsb}")
        port_name = port_text or 'unknown'
        if 'data' in port_name.lower() or 'din' in port_name.lower() or 'dout' in port_name.lower():
            return "[31:0]"
        if 'addr' in port_name.lower():
            return "[15:0]"
        if 'clk' in port_name.lower() or 'rst' in port_name.lower() or 'we' in port_name.lower() or 're' in port_name.lower() or 'ack' in port_name.lower() or 'err' in port_name.lower():
            return ""
        for macro_name, macro_value in macros.items():
            if macro_name.lower() in port_name.lower():
                try:
                    width = int(macro_value) - 1
                    return f"[{width}:0]"
                except ValueError:
                    pass
        logging.debug(f"Default width for {port_name}: (single-bit)")
        return ""
    except Exception as e:
        logging.error(f"Error extracting port width for {port_text}: {e}")
        return ""

def parse_module_ports(member, macros: Dict[str, str]) -> Tuple[List[str], Set[str]]:
    ports = []
    port_names = set()
    try:
        module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
        logging.debug(f"Parsing ports for module: {module_name}")
        import pyslang
        syntax_kinds = [k for k in dir(pyslang.SyntaxKind) if not k.startswith('_')]
        logging.debug(f"Available SyntaxKind values: {syntax_kinds}")
        header_text = str(getattr(member, 'header', ''))
        # logging.debug(f"Module header text: {header_text}")
        header_ports = getattr(member.header, 'ports', [])
        # logging.debug(f"Header port kinds: {[p.kind for p in header_ports]}")
        # logging.debug(f"Member kinds: {[m.kind for m in member.members]}")
        if header_ports:
            for port in header_ports:
                # logging.debug(f"Port node kind: {port.kind}, text={str(port)}")
                if port.kind == pyslang.SyntaxKind.AnsiPortList:
                    for sub_port in getattr(port, 'ports', [port]):
                        name = getattr(sub_port, 'name', None)
                        if name and hasattr(name, 'valueText'):
                            name = name.valueText
                            direction = str(getattr(sub_port, 'direction', 'unknown')).lower().split()[0]
                            data_type = str(getattr(sub_port, 'type', 'wire')).strip() or 'wire'
                            width = get_port_width(sub_port, macros, name)
                            ports.append(f"{direction} {data_type}{width} {name}")
                            port_names.add(name)
                            logging.debug(f"Parsed ANSI port: {direction} {data_type}{width} {name}")
        for sub_member in member.members:
            # logging.debug(f"Sub-member kind: {sub_member.kind}, text={str(sub_member)}")
            if sub_member.kind == pyslang.SyntaxKind.PortDeclaration:
                direction = str(getattr(sub_member, 'direction', 'unknown')).lower().split()[0]
                data_type = str(getattr(sub_member, 'type', 'wire')).strip() or 'wire'
                for declarator in getattr(sub_member, 'declarators', []):
                    name = getattr(declarator, 'name', None)
                    if name and hasattr(name, 'valueText'):
                        name = name.valueText
                        width = get_port_width(declarator, macros, name)
                        ports.append(f"{direction} {data_type}{width} {name}")
                        port_names.add(name)
                        logging.debug(f"Parsed non-ANSI port: {direction} {data_type}{width} {name}")
            elif sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
                net_type = str(getattr(sub_member, 'netType', 'wire')).strip() or 'wire'
                for declarator in getattr(sub_member, 'declarators', []):
                    name = getattr(declarator, 'name', None)
                    if name and hasattr(name, 'valueText'):
                        name = name.valueText
                        is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
                        if is_port:
                            direction = "input" if "input" in str(sub_member).lower() else "output" if "output" in str(sub_member).lower() else "inout"
                            width = get_port_width(declarator, macros, name)
                            ports.append(f"{direction} {net_type}{width} {name}")
                            port_names.add(name)
                            logging.debug(f"Parsed net port: {direction} {net_type}{width} {name}")
            elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
                if 'reg' in str(sub_member).lower():
                    for declarator in getattr(sub_member, 'declarators', []):
                        name = getattr(declarator, 'name', None)
                        if name and hasattr(name, 'valueText'):
                            name = name.valueText
                            is_port = any(p.name.valueText == name for p in header_ports if hasattr(p, 'name') and hasattr(p.name, 'valueText'))
                            if is_port:
                                width = get_port_width(declarator, macros, name)
                                ports.append(f"output reg{width} {name}")
                                port_names.add(name)
                                logging.debug(f"Parsed reg port: output reg{width} {name}")
        if not ports:
            port_pattern = re.compile(r'(input|output|inout)\s+(wire|reg)?\s*(\[\d+:\d+\])?\s*(\w+)', re.DOTALL)
            port_matches = port_pattern.findall(header_text)
            for direction, data_type, width, port_name in port_matches:
                data_type = data_type or 'wire'
                width = width or get_port_width(None, macros, port_name)
                ports.append(f"{direction} {data_type}{width} {port_name}")
                port_names.add(port_name)
                logging.debug(f"Parsed fallback port: {direction} {data_type}{width} {port_name}")
        if not ports:
            logging.warning(f"No ports found for module {module_name}. Check port declarations in source.")
        return sorted(ports), port_names
    except Exception as e:
        logging.error(f"Error parsing ports for module {module_name}: {e}")
        return ports, port_names

def parse_components(member, source_text, port_names, macros, lib_cells: Dict[str, Dict[str, any]], module_names: Set[str]):
    components = {"wires": [], "registers": [], "counters": [], "flip_flops": [], "gates": [], "muxes": [], "instances": [], "switches": []}
    connections = {"wires": {}, "instances": {}}
    try:
        module_name = getattr(member.header, 'name', None).valueText if hasattr(member.header, 'name') else 'unknown'
        logging.debug(f"Parsing components for module: {module_name}")

        # Parse wires and registers
        for sub_member in member.members:
            if sub_member.kind == pyslang.SyntaxKind.NetDeclaration:
                for declarator in getattr(sub_member, 'declarators', []):
                    name = getattr(declarator, 'name', None)
                    if name and hasattr(name, 'valueText'):
                        name = name.valueText
                        if name not in port_names:
                            components["wires"].append(name)
                            connections["wires"][name] = {"source": [], "sinks": []}
            elif sub_member.kind == pyslang.SyntaxKind.DataDeclaration:
                if 'reg' in str(sub_member).lower():
                    for declarator in getattr(sub_member, 'declarators', []):
                        name = getattr(declarator, 'name', None)
                        if name and hasattr(name, 'valueText'):
                            name = name.valueText
                            if name not in port_names:
                                components["registers"].append(name)
                                connections["wires"][name] = {"source": [], "sinks": []}

            # Parse continuous assignments
            elif sub_member.kind == pyslang.SyntaxKind.ContinuousAssign:
                for assign in getattr(sub_member, 'assignments', []):
                    lhs = getattr(assign, 'left', None)
                    rhs = getattr(assign, 'right', None)
                    if lhs and rhs and hasattr(lhs, 'valueText'):
                        lhs_name = lhs.valueText
                        rhs_signals = []
                        def extract_signals(node):
                            if hasattr(node, 'valueText'):
                                return [node.valueText]
                            elif node.kind == pyslang.SyntaxKind.BinaryExpression:
                                left = getattr(node, 'left', None)
                                right = getattr(node, 'right', None)
                                signals = []
                                if left:
                                    signals.extend(extract_signals(left))
                                if right:
                                    signals.extend(extract_signals(right))
                                return []
                            elif node.kind == pyslang.SyntaxKind.ElementSelect:
                                base = getattr(node, 'expr', None)
                                if base and hasattr(base, 'valueText'):
                                    return [base.valueText]
                                return []
                        rhs_signals = extract_signals(rhs)
                        connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
                        connections["wires"][lhs_name]["source"].append(str(rhs))
                        for sig in rhs_signals:
                            if sig in connections["wires"] or sig in port_names:
                                connections["wires"][lhs_name]["sinks"].append(sig)
                        logging.debug(f"Parsed assign: {lhs_name} = {rhs_signals}")

            # Parse instances
            elif sub_member.kind == pyslang.SyntaxKind.HierarchyInstantiation:
                for instance in getattr(sub_member, 'instances', []):
                    inst_name = getattr(instance, 'name', None)
                    inst_name = inst_name.valueText if inst_name and hasattr(inst_name, 'valueText') else f"inst_{len(connections['instances'])}"
                    module_type_node = getattr(sub_member, 'name', None)
                    module_type = module_type_node.valueText if module_type_node and hasattr(module_type_node, 'valueText') else None
                    if not module_type:
                        instance_text = str(sub_member)
                        instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\(', re.MULTILINE)
                        match = instance_pattern.search(instance_text)
                        module_type = match.group(1) if match else 'unknown'
                    logging.debug(f"Found instance: {inst_name} ({module_type})")
                    if inst_name in connections["instances"]:
                        logging.debug(f"Skipping duplicate instance: {inst_name} ({module_type})")
                        continue
                    classified = False
                    if module_type in lib_cells:
                        cell_info = lib_cells[module_type]
                        cell_type = cell_info['type']
                        components[cell_type + "s"].append(f"{inst_name} ({module_type})")
                        classified = True
                    elif module_type in module_names:
                        components["instances"].append(f"{inst_name} ({module_type})")
                        classified = True
                    if not classified:
                        logging.warning(f"Unclassified instance: {inst_name} ({module_type})")
                        components["instances"].append(f"{inst_name} ({module_type})")
                    connections["instances"][inst_name] = {"module": module_type, "connections": []}
                    for conn in getattr(instance, 'connections', []):
                        local = getattr(conn, 'name', None)
                        expr = getattr(conn, 'expr', None)
                        if local and expr and hasattr(local, 'valueText') and hasattr(expr, 'valueText'):
                            local_port = local.valueText
                            expr_signal = expr.valueText
                            connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
                            connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
                            if module_type in lib_cells:
                                cell_info = lib_cells[module_type]
                                if local_port in cell_info.get('inputs', []):
                                    connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
                                elif local_port in cell_info.get('outputs', []):
                                    connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
                            else:
                                connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

            # Parse always blocks for procedural assignments and behavioral flip-flops
            elif sub_member.kind == pyslang.SyntaxKind.AlwaysBlock:
                block_text = str(sub_member)
                if detect_counter(block_text):
                    components["counters"].append(f"counter_in_{module_name}")
                if 'if' in block_text.lower() and 'else' in block_text.lower():
                    components["muxes"].append(f"mux_in_{module_name}")
                if '@(posedge' in block_text.lower() or '@(negedge' in block_text.lower():
                    components["flip_flops"].append(f"ff_in_{module_name}")
                    logging.debug(f"Detected behavioral flip-flop in {module_name}")
                for statement in getattr(sub_member, 'statements', []):
                    if statement.kind in [pyslang.SyntaxKind.AssignStatement, pyslang.SyntaxKind.NonblockingAssign]:
                        lhs = getattr(statement, 'left', None)
                        rhs = getattr(statement, 'right', None)
                        if lhs and rhs and hasattr(lhs, 'valueText'):
                            lhs_name = lhs.valueText
                            rhs_signals = []
                            def extract_signals(node):
                                if hasattr(node, 'valueText'):
                                    return [node.valueText]
                                elif node.kind == pyslang.SyntaxKind.BinaryExpression:
                                    left = getattr(node, 'left', None)
                                    right = getattr(node, 'right', None)
                                    signals = []
                                    if left:
                                        signals.extend(extract_signals(left))
                                    if right:
                                        signals.extend(extract_signals(right))
                                    return []
                                elif node.kind == pyslang.SyntaxKind.ElementSelect:
                                    base = getattr(node, 'expr', None)
                                    if base and hasattr(base, 'valueText'):
                                        return [base.valueText]
                                    return []
                            rhs_signals = extract_signals(rhs)
                            connections["wires"].setdefault(lhs_name, {"source": [], "sinks": []})
                            connections["wires"][lhs_name]["source"].append(str(rhs))
                            for sig in rhs_signals:
                                if sig in connections["wires"] or sig in port_names:
                                    connections["wires"][lhs_name]["sinks"].append(sig)
                            logging.debug(f"Parsed always assign: {lhs_name} = {rhs_signals}")

        # Fallback regex for registers
        reg_pattern = re.compile(r'reg\s*(\[\d+:\d+\])?\s*(\w+)\s*;', re.DOTALL)
        reg_matches = reg_pattern.findall(source_text)
        for width, name in reg_matches:
            if name not in port_names and name not in components["registers"]:
                components["registers"].append(name)
                connections["wires"].setdefault(name, {"source": [], "sinks": []})
                logging.debug(f"Parsed register (regex): {name}")

        # Fallback regex for instances
        instance_pattern = re.compile(r'(\w+)\s+(\w+)\s*\((.*?)\)\s*;', re.DOTALL)
        instance_matches = instance_pattern.findall(source_text)
        for module_type, inst_name, connections_text in instance_matches:
            if module_type in {'module', 'begin', 'generate', 'case', 'if', 'always', 'assign', 'wire', 'reg'}:
                logging.debug(f"Filtered invalid instance: {inst_name} ({module_type})")
                continue
            if inst_name in connections["instances"]:
                logging.debug(f"Skipping duplicate instance (regex): {inst_name} ({module_type})")
                continue
            logging.debug(f"Parsed instance (regex): {inst_name} ({module_type})")
            classified = False
            if module_type in lib_cells:
                cell_info = lib_cells[module_type]
                cell_type = cell_info['type']
                components[cell_type + "s"].append(f"{inst_name} ({module_type})")
                classified = True
            elif module_type in module_names:
                components["instances"].append(f"{inst_name} ({module_type})")
                classified = True
            if not classified:
                logging.warning(f"Unclassified instance (regex): {inst_name} ({module_type})")
                components["instances"].append(f"{inst_name} ({module_type})")
            connections["instances"][inst_name] = {"module": module_type, "connections": []}
            conn_matches = re.findall(r'\.(\w+)\s*\(\s*(\w+)\s*\)', connections_text)
            for local_port, expr_signal in conn_matches:
                connections["instances"][inst_name]["connections"].append(f"{local_port} -> {expr_signal}")
                connections["wires"].setdefault(expr_signal, {"source": [], "sinks": []})
                if module_type in lib_cells:
                    cell_info = lib_cells[module_type]
                    if local_port in cell_info.get('inputs', []):
                        connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")
                    elif local_port in cell_info.get('outputs', []):
                        connections["wires"][expr_signal]["source"].append(f"{inst_name}.{local_port}")
                else:
                    connections["wires"][expr_signal]["sinks"].append(f"{inst_name}.{local_port}")

        return components, connections
    except Exception as e:
        logging.error(f"Error parsing components for module {module_name}: {e}")
        return components, connections

def process_file(file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output, lib_cells: Dict[str, Dict[str, str]]):
    module_data = []
    try:
        for member in syntax_tree.root.members:
            if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
                module_name = getattr(member.header, 'name', None)
                if module_name is None or not hasattr(module_name, 'valueText'):
                    continue
                module_name = module_name.valueText
                ports, port_names = parse_module_ports(member, macros)
                components, connections = parse_components(member, source_text, port_names, macros, lib_cells, module_names)
                total_instances = len(components["instances"]) + len(components["flip_flops"]) + len(components["gates"])
                log_section(f"Module: {module_name}", [
                    f"Ports: {', '.join(ports) if ports else 'None'}",
                    f"Components: Wires={len(components['wires'])}, Registers={len(components['registers'])}, "
                    f"Counters={len(components['counters'])}, Flip-Flops={len(components['flip_flops'])}, "
                    f"Gates={len(components['gates'])}, Muxes={len(components['muxes'])}, "
                    f"Switches={len(components['switches'])}, Instances={total_instances}",
                    f"Connectivity: {len(connections['wires'])} wires, {len(connections['instances'])} instances"
                ], detailed_output)
                parsed_instances.add(module_name)
                module_data.append((module_name, connections, components))
        return module_data
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return module_data