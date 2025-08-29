# import os
# import argparse
# import time
# import logging
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh")):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()

#     # Collect files
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))

#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file provided: {lib_file}" if lib_file else "No library file provided",
#         f"Found {len(files_to_process)} files to process"
#     ])

#     # Extract macros from .vh files
#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith('.vh'):
#             try:
#                 file_macros = extract_macros(file_path)
#                 macros.update(file_macros)
#                 logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#             except Exception as e:
#                 logging.error(f"Failed to extract macros from {file_path}: {e}")
#     logging.info(f"Total macros extracted: {len(macros)}")

#     # Parse syntax trees with preprocessing
#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 # Extract message safely
#                 message = getattr(diag, 'note', None)
#                 if message and hasattr(message, 'valueText'):
#                     message = message.valueText
#                 else:
#                     message = str(diag)  # Fallback to string representation

#                 # Extract line number safely
#                 line = 'Unknown'
#                 if hasattr(diag, 'location') and diag.location:
#                     if hasattr(diag.location, 'line'):
#                         line = diag.location.line
#                     elif hasattr(diag.location, 'lineNumber'):
#                         line = diag.location.lineNumber

#                 logging.error(f"Diagnostic for {file_path}: {message} at line {line}")
#         except Exception as e:
#             logging.error(f"Failed to load or parse {file_path}: {e}")
#         # try:
#         #     with open(file_path, 'r', encoding='utf-8') as f:
#         #         source_text = f.read()
#         #     preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#         #     source_buffer = source_manager.assignText(file_path, preprocessed_text)
#         #     syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#         #     syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#         #     for diag in syntax_tree.diagnostics:
#         #         # Safely handle diagnostics without assuming 'note' exists
#         #         message = getattr(diag, 'note', None)
#         #         if message and hasattr(message, 'valueText'):
#         #             message = message.valueText
#         #         else:
#         #             message = str(diag)  # Fallback to string representation
#         #         line = getattr(diag, 'location', None)
#         #         line = line.lineNumber if line and hasattr(line, 'lineNumber') else 'Unknown'
#         #         logging.error(f"Diagnostic for {file_path}: {message} at line {line}")
#         # except Exception as e:
#         #     logging.error(f"Failed to load or parse {file_path}: {e}")

#     # Extract modules
#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     logging.warning(f"Skipping module with no name in {file_path}")
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#             else:
#                 logging.debug(f"Non-module member in {file_path}: {member.kind}")
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     logging.info(f"Total modules parsed: {module_count_total}")

#     # Log module names
#     detailed_output.append("\nModule Names:")
#     if not all_modules:
#         detailed_output.append("- (none)")
#         logging.info("No modules found in any files")
#     else:
#         for module in sorted(all_modules, key=lambda x: x['name']):
#             detailed_output.append(f"- {module['name']} (file: {module['file']})")
#         logging.info(f"Total modules found: {len(all_modules)}")

#     # Process files and collect output
#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         log_section(f"Module Processing for {file_path}", [])
#         module_data = process_file(
#             file_path, source_text, all_modules, syntax_tree, macros, parsed_instances, module_names, detailed_output
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 logging.info(f"Processed module {module_name} in {file_path}: "
#                             f"{len(components.get('registers', []))} registers, "
#                             f"{len(components.get('wires', []))} wires")
#                 logging.debug(f"Module {module_name} components: {components}")
#         else:
#             logging.warning(f"No valid module processed in {file_path}")
#         logging.info(f"Finished module processing for {file_path}")

#     # Generate hierarchy and log summary
#     log_section("Module Hierarchy", [])
#     generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     log_section("Execution Summary", [f"Total execution time: {time.time() - start_time:.2f} seconds"])

#     # Print console output
#     for line in detailed_output:
#         print(line)
#     print(f"Total execution time: {time.time() - start_time:.2f} seconds")

# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     process_path(os.path.abspath(args.path), args.lib)

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()





























# # tested1

# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     """Generate IP-XACT XML files for each module."""
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 port_name = port.split(":")[0].strip()
#                 direction = port.split(":")[1].strip().split()[0] if ":" in port else "unknown"
#                 width = port.split(":")[1].strip().split()[-1] if ":" in port else "1"
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 ET.SubElement(port_elem, "spirit:wire").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file,
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     try:
#         if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#             files_to_process.append(lib_file)
#         if os.path.isfile(path) and path.endswith(extensions):
#             files_to_process.append(path)
#         elif os.path.isdir(path):
#             for root, _, files in os.walk(path):
#                 for file in files:
#                     if file.endswith(extensions):
#                         files_to_process.append(os.path.join(root, file))

#         parsed_data["file_processing"]["files_found"] = len(files_to_process)
#         log_section("File Processing", [
#             f"Starting processing of path: {path}",
#             f"Library file provided: {lib_file}" if lib_file else "No library file provided",
#             f"Found {len(files_to_process)} files to process"
#         ])

#         log_section("Macro Extraction", [])
#         include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#         for file_path in files_to_process:
#             if file_path.endswith('.vh'):
#                 file_macros = extract_macros(file_path)
#                 macros.update(file_macros)
#                 parsed_data["macro_extraction"]["macros"].update(file_macros)
#                 logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#         parsed_data["macro_extraction"]["total_macros"] = len(macros)
#         logging.info(f"Total macros extracted: {len(macros)}")

#         log_section("Syntax Tree Parsing", [])
#         import pyslang
#         source_manager = pyslang.SourceManager()
#         for include_dir in include_dirs:
#             source_manager.addUserDirectories(include_dir)
#         for file_path in files_to_process:
#             if not file_path.endswith(('.sv', '.v')):
#                 continue
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = diag.location.lineNumber if hasattr(diag.location, 'lineNumber') else 'Unknown'
#                 column = diag.location.columnNumber if hasattr(diag.location, 'columnNumber') else 'Unknown'
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#                 detailed_output.append(f"Diagnostic for {file_path} at line {line}:{column}: {message}")

#         log_section("Module Analysis", [])
#         module_count_total = 0
#         for file_path, syntax_tree, _ in syntax_trees:
#             module_count = 0
#             for member in syntax_tree.root.members:
#                 if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                     module_name = getattr(member.header, 'name', None)
#                     if module_name is None or not hasattr(module_name, 'valueText'):
#                         logging.warning(f"Skipping module with no valid name in {file_path}")
#                         continue
#                     module_name = module_name.valueText
#                     ports, _ = parse_module_ports(member, macros)
#                     all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                     parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                     module_names.add(module_name)
#                     module_count += 1
#                     module_count_total += 1
#             logging.info(f"Parsed {module_count} modules in {file_path}")
#         parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#         logging.info(f"Total modules parsed: {module_count_total}")

#         log_section("Module Processing", [])
#         for file_path, syntax_tree, source_text in syntax_trees:
#             module_data = process_file(
#                 file_path=file_path,
#                 source_text=source_text,
#                 all_modules=all_modules,
#                 syntax_tree=syntax_tree,
#                 macros=macros,
#                 parsed_instances=parsed_instances,
#                 module_names=module_names,
#                 detailed_output=detailed_output
#             )
#             if module_data:
#                 for module_name, connections, components in module_data:
#                     if file_path not in connections_by_module:
#                         connections_by_module[file_path] = []
#                     connections_by_module[file_path].append({
#                         "name": module_name,
#                         "connections": connections,
#                         "components": components
#                     })
#                     module_entry = {
#                         "name": module_name,
#                         "ports": ports,
#                         "components": components,
#                         "connectivity_report": connections["wires"],
#                         "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items()],
#                         "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                     }
#                     parsed_data["modules"].append(module_entry)
#                     logging.info(f"Processed module {module_name} in {file_path}")

#         log_section("Module Hierarchy", [])
#         hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#         parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#         parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#         parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

#         # Convert sets to lists for JSON
#         parsed_data = convert_sets_to_lists(parsed_data)

#         # Print console output
#         for line in detailed_output:
#             print(line)
#         print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#         with open("output.json", "w") as json_file:
#             json.dump(parsed_data, json_file, indent=4)
#         logging.info("Exported parsed data to output.json")

#         if generate_ipxact_flag:
#             generate_ipxact(parsed_data)
#     except Exception as e:
#         logging.error(f"Error in process_path: {e}")
#         raise

# # def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
# #     start_time = time.time()
# #     all_modules = []
# #     files_to_process = []
# #     syntax_trees = []
# #     connections_by_module = {}
# #     module_names = set()
# #     detailed_output = []
# #     macros = {}
# #     parsed_instances = set()
# #     parsed_data = {
# #         "system_usage": {},
# #         "file_processing": {
# #             "path": path,
# #             "library_file": lib_file,
# #             "files_found": 0
# #         },
# #         "macro_extraction": {
# #             "total_macros": 0,
# #             "macros": {}
# #         },
# #         "module_analysis": {
# #             "total_modules_parsed": 0,
# #             "module_names": []
# #         },
# #         "modules": [],
# #         "hierarchy": {
# #             "top_level_modules": [],
# #             "structure": {}
# #         },
# #         "execution_summary": {
# #             "execution_time": 0.0
# #         }
# #     }

# #     try:
# #         if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
# #             files_to_process.append(lib_file)
# #         if os.path.isfile(path) and path.endswith(extensions):
# #             files_to_process.append(path)
# #         elif os.path.isdir(path):
# #             for root, _, files in os.walk(path):
# #                 for file in files:
# #                     if file.endswith(extensions):
# #                         files_to_process.append(os.path.join(root, file))

# #         parsed_data["file_processing"]["files_found"] = len(files_to_process)
# #         log_section("File Processing", [
# #             f"Starting processing of path: {path}",
# #             f"Library file provided: {lib_file}" if lib_file else "No library file provided",
# #             f"Found {len(files_to_process)} files to process"
# #         ])

# #         log_section("Macro Extraction", [])
# #         include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
# #         for file_path in files_to_process:
# #             if file_path.endswith('.vh'):
# #                 file_macros = extract_macros(file_path)
# #                 macros.update(file_macros)
# #                 parsed_data["macro_extraction"]["macros"].update(file_macros)
# #                 logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
# #         parsed_data["macro_extraction"]["total_macros"] = len(macros)
# #         logging.info(f"Total macros extracted: {len(macros)}")

# #         log_section("Syntax Tree Parsing", [])
# #         import pyslang
# #         source_manager = pyslang.SourceManager()
# #         for include_dir in include_dirs:
# #             source_manager.addUserDirectories(include_dir)
# #         for file_path in files_to_process:
# #             if not file_path.endswith(('.sv', '.v')):
# #                 continue
# #             with open(file_path, 'r', encoding='utf-8') as f:
# #                 source_text = f.read()
# #             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
# #             source_buffer = source_manager.assignText(file_path, preprocessed_text)
# #             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
# #             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
# #             for diag in syntax_tree.diagnostics:
# #                 message = str(diag) if not hasattr(diag, 'note') else diag.note.valueText if hasattr(diag.note, 'valueText') else str(diag.note)
# #                 line = diag.location.lineNumber if hasattr(diag.location, 'lineNumber') else 'Unknown'
# #                 column = diag.location.columnNumber if hasattr(diag.location, 'columnNumber') else 'Unknown'
# #                 logging.error(f"Diagnostic for {file_path}: {message} at line {line}:{column}")

# #         log_section("Module Analysis", [])
# #         module_count_total = 0
# #         for file_path, syntax_tree, _ in syntax_trees:
# #             module_count = 0
# #             for member in syntax_tree.root.members:
# #                 if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
# #                     module_name = getattr(member.header, 'name', None)
# #                     if module_name is None or not hasattr(module_name, 'valueText'):
# #                         continue
# #                     module_name = module_name.valueText
# #                     ports, _ = parse_module_ports(member, macros)
# #                     all_modules.append({"name": module_name, "ports": ports, "file": file_path})
# #                     parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
# #                     module_names.add(module_name)
# #                     module_count += 1
# #                     module_count_total += 1
# #             logging.info(f"Parsed {module_count} modules in {file_path}")
# #         parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
# #         logging.info(f"Total modules parsed: {module_count_total}")

# #         log_section("Module Processing", [])
# #         for file_path, syntax_tree, source_text in syntax_trees:
# #             module_data = process_file(
# #                 file_path=file_path,  # Fixed syntax: changed 'file DVFilePath: file_path' to 'file_path=file_path'
# #                 source_text=source_text,
# #                 all_modules=all_modules,
# #                 syntax_tree=syntax_tree,
# #                 macros=macros,
# #                 parsed_instances=parsed_instances,
# #                 module_names=module_names,
# #                 detailed_output=detailed_output
# #             )
# #             if module_data:
# #                 for module_name, connections, components in module_data:
# #                     if file_path not in connections_by_module:
# #                         connections_by_module[file_path] = []
# #                     connections_by_module[file_path].append({
# #                         "name": module_name,
# #                         "connections": connections,
# #                         "components": components
# #                     })
# #                     module_entry = {
# #                         "name": module_name,
# #                         "ports": ports,
# #                         "components": components,
# #                         "connectivity_report": connections["wires"],
# #                         "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items()],
# #                         "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
# #                     }
# #                     parsed_data["modules"].append(module_entry)
# #                     logging.info(f"Processed module {module_name} in {file_path}")

# #         log_section("Module Hierarchy", [])
# #         hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
# #         parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
# #         parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

# #         parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

# #         # Convert sets to lists for JSON
# #         parsed_data = convert_sets_to_lists(parsed_data)

# #         # Print console output
# #         for line in detailed_output:
# #             print(line)
# #         print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

# #         with open("output.json", "w") as json_file:
# #             json.dump(parsed_data, json_file, indent=4)
# #         logging.info("Exported parsed data to output.json")

# #         if generate_ipxact_flag:
# #             generate_ipxact(parsed_data)
# #     except Exception as e:
# #         logging.error(f"Error in process_path: {e}")
# #         raise

# def main():
#     try:
#         parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#         parser.add_argument("path", help="Path to a Verilog file or directory")
#         parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#         parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                             help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#         parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#         args = parser.parse_args()
#         setup_logging(args.verbosity)
#         logging.info("Starting main execution")
#         process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)
#     except Exception as e:
#         logging.error(f"Error in main: {e}")
#         raise

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()












# # tested3

# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring
# from lib_parser import parse_lib_file

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 port_name = port.split(":")[0].strip()
#                 direction = port.split(":")[1].strip().split()[0] if ":" in port else "unknown"
#                 width = port.split(":")[1].strip().split()[-1] if ":" in port else "1"
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 wire_elem = ET.SubElement(port_elem, "spirit:wire")
#                 ET.SubElement(wire_elem, "spirit:vector").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     lib_cells = {} if not lib_file else parse_lib_file(lib_file)
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file if lib_file else "None",
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     # Collecting files
#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file: {lib_file}" if lib_file else "No library file provided",
#     ])
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))
#     parsed_data["file_processing"]["files_found"] = len(files_to_process)
#     log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

#     # Extract macros
#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith('.vh'):
#             file_macros = extract_macros(file_path)
#             macros.update(file_macros)
#             parsed_data["macro_extraction"]["macros"].update(file_macros)
#             logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#     parsed_data["macro_extraction"]["total_macros"] = len(macros)
#     logging.info(f"Total macros extracted: {len(macros)}")

#     # Parse syntax trees
#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = getattr(diag.location, 'lineNumber', 'Unknown')
#                 column = getattr(diag.location, 'columnNumber', 'Unknown')
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#         except Exception as e:
#             logging.error(f"Error parsing {file_path}: {e}")

#     # Module analysis
#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#     logging.info(f"Total modules parsed: {module_count_total}")

#     # Module processing
#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         module_data = process_file(
#             file_path=file_path,
#             source_text=source_text,
#             all_modules=all_modules,
#             syntax_tree=syntax_tree,
#             macros=macros,
#             parsed_instances=parsed_instances,
#             module_names=module_names,
#             detailed_output=detailed_output,
#             lib_cells=lib_cells
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 module_entry = {
#                     "name": module_name,
#                     "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
#                     "components": components,
#                     "connectivity_report": connections["wires"],
#                     "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items()],
#                     "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                 }
#                 parsed_data["modules"].append(module_entry)
#                 logging.info(f"Processed module {module_name} in {file_path}")

#     # Hierarchy
#     log_section("Module Hierarchy", [])
#     hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     if hierarchy_data is None:
#         logging.error("Failed to generate hierarchy data, setting defaults")
#         hierarchy_data = {"top_level_modules": [], "structure": {}}
#     parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#     parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#     parsed_data["execution_summary"]["execution_time"] = time.time() - start_time
#     parsed_data = convert_sets_to_lists(parsed_data)

#     # Output results
#     for line in detailed_output:
#         print(line)
#     print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#     with open("output.json", "w") as json_file:
#         json.dump(parsed_data, json_file, indent=4)
#     logging.info("Exported parsed data to output.json")

#     if generate_ipxact_flag:
#         generate_ipxact(parsed_data)

# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     logging.info("Starting main execution")
#     process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()






















































# # tested2


# import os
# import argparse
# import time
# import logging
# import json
# import re
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def parse_lib(lib_file):
#     cells = set()
#     if lib_file and os.path.isfile(lib_file):
#         try:
#             with open(lib_file, 'r', encoding='utf-8') as f:
#                 content = f.read()
#                 # logging.debug(f"Library file content: {content[:500]}...")  # Log first 500 chars
#             # Extract module names from Verilog-style library files
#             for match in re.finditer(r'module\s+(\w+)\s*(?:\(|#|\n)', content):
#                 cells.add(match.group(1))
#             logging.info(f"Extracted {len(cells)} cells from library file {lib_file}")
#         except Exception as e:
#             logging.error(f"Error parsing library file {lib_file}: {e}")
#     else:
#         logging.warning(f"Library file {lib_file} not found or not specified")
#     return cells

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 port_name = port.split(":")[0].strip()
#                 direction = port.split(":")[1].strip().split()[0] if ":" in port else "unknown"
#                 width = port.split(":")[1].strip().split()[-1] if ":" in port else "1"
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 ET.SubElement(port_elem, "spirit:wire").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()  # Initialize parsed_instances
#     lib_cells = parse_lib(lib_file)
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file,
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     try:
#         if lib_file and os.path.isfile(lib_file):
#             files_to_process.append(lib_file)
#         if os.path.isfile(path):
#             files_to_process.append(path)
#         elif os.path.isdir(path):
#             for root, _, files in os.walk(path):
#                 for file in files:
#                     if file.endswith(extensions):
#                         files_to_process.append(os.path.join(root, file))

#         parsed_data["file_processing"]["files_found"] = len(files_to_process)
#         log_section("File Processing", [
#             f"Starting processing of path: {path}",
#             f"Library file provided: {lib_file}" if lib_file else "No library file provided",
#             f"Found {len(files_to_process)} files to process"
#         ])

#         log_section("Macro Extraction", [])
#         include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#         for file_path in files_to_process:
#             if file_path.endswith('.vh'):
#                 file_macros = extract_macros(file_path)
#                 macros.update(file_macros)
#                 parsed_data["macro_extraction"]["macros"].update(file_macros)
#                 logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#         parsed_data["macro_extraction"]["total_macros"] = len(macros)
#         logging.info(f"Total macros extracted: {len(macros)}")

#         log_section("Syntax Tree Parsing", [])
#         import pyslang
#         source_manager = pyslang.SourceManager()
#         for include_dir in include_dirs:
#             source_manager.addUserDirectories(include_dir)
#         for file_path in files_to_process:
#             if not file_path.endswith(('.sv', '.v')):
#                 continue
#             try:
#                 with open(file_path, 'r', encoding='utf-8') as f:
#                     source_text = f.read()
#                     # logging.debug(f"File content ({file_path}): {source_text[:500]}...")
#                 preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#                 source_buffer = source_manager.assignText(file_path, preprocessed_text)
#                 syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#                 syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#                 for diag in syntax_tree.diagnostics:
#                     try:
#                         message = str(diag.message) if hasattr(diag, 'message') else str(diag.note) if hasattr(diag, 'note') else str(diag)
#                         line = diag.location.line() if hasattr(diag.location, 'line') else 'Unknown'
#                         column = diag.location.column() if hasattr(diag.location, 'column') else 'Unknown'
#                         logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#                         detailed_output.append(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#                     except Exception as diag_err:
#                         logging.error(f"Error processing diagnostic for {file_path}: {diag_err}")
#             except Exception as e:
#                 logging.error(f"Error reading or parsing {file_path}: {e}")
#                 detailed_output.append(f"Error reading or parsing {file_path}: {e}")

#         log_section("Module Analysis", [])
#         module_count_total = 0
#         for file_path, syntax_tree, _ in syntax_trees:
#             module_count = 0
#             logging.debug(f"Syntax tree members for {file_path}: {[str(m.kind) for m in syntax_tree.root.members]}")
#             for member in syntax_tree.root.members:
#                 if str(member.kind) == 'ModuleDeclaration':
#                     module_name = None
#                     try:
#                         if hasattr(member, 'header') and hasattr(member.header, 'name') and hasattr(member.header.name, 'valueText'):
#                             module_name = member.header.name.valueText
#                         elif hasattr(member, 'name') and hasattr(member.name, 'valueText'):
#                             module_name = member.name.valueText
#                         else:
#                             # Fallback: Extract module name from string representation
#                             member_str = str(member)
#                             match = re.match(r'module\s+(\w+)', member_str)
#                             if match:
#                                 module_name = match.group(1)
#                                 logging.debug(f"Fallback module name extracted: {module_name}")
#                             else:
#                                 logging.warning(f"No valid name for module in {file_path}: {member_str[:200]}...")
#                             continue
#                         logging.debug(f"Found module: {module_name}")
#                         ports, _ = parse_module_ports(member, macros)
#                         all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                         parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                         module_names.add(module_name)
#                         module_count += 1
#                         module_count_total += 1
#                     except Exception as e:
#                         logging.error(f"Error extracting module name in {file_path}: {e}")
#             logging.info(f"Parsed {module_count} modules in {file_path}")
#         parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#         logging.info(f"Total modules parsed: {module_count_total}")

#         log_section("Module Processing", [])
#         for file_path, syntax_tree, source_text in syntax_trees:
#             module_data = process_file(
#                 file_path=file_path,
#                 source_text=source_text,
#                 all_modules=all_modules,
#                 syntax_tree=syntax_tree,
#                 macros=macros,
#                 parsed_instances=parsed_instances,
#                 module_names=module_names,
#                 detailed_output=detailed_output,
#                 lib_cells=lib_cells
#             )
#             if module_data:
#                 for module_name, connections, components in module_data:
#                     if file_path not in connections_by_module:
#                         connections_by_module[file_path] = []
#                     connections_by_module[file_path].append({
#                         "name": module_name,
#                         "connections": connections,
#                         "components": components
#                     })
#                     module_entry = {
#                         "name": module_name,
#                         "ports": ports,
#                         "components": components,
#                         "connectivity_report": connections["wires"],
#                         "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items()],
#                         "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                     }
#                     parsed_data["modules"].append(module_entry)
#                     logging.info(f"Processed module {module_name} in {file_path}")

#         log_section("Module Hierarchy", [])
#         hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#         parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#         parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#         parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

#         # Log and print system_usage and execution_summary
#         logging.info(f"System Usage: {parsed_data['system_usage']}")
#         logging.info(f"Execution Time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")
#         print(f"System Usage: {parsed_data['system_usage']}")
#         print(f"Execution Time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#         # Exempt them from output.json
#         del parsed_data['system_usage']
#         del parsed_data['execution_summary']

#         # Convert sets to lists for JSON
#         parsed_data = convert_sets_to_lists(parsed_data)

#         # Print console output
#         for line in detailed_output:
#             print(line)

#         with open("output.json", "w") as json_file:
#             json.dump(parsed_data, json_file, indent=4)
#         logging.info("Exported parsed data to output.json")

#         if generate_ipxact_flag:
#             generate_ipxact(parsed_data)
#     except Exception as e:
#         logging.error(f"Error in process_path: {e}")
#         raise

# def main():
#     try:
#         parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#         parser.add_argument("path", help="Path to a Verilog file or directory")
#         parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#         parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                             help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#         parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#         args = parser.parse_args()
#         setup_logging(args.verbosity)
#         logging.info("Starting main execution")
#         process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)
#     except Exception as e:
#         logging.error(f"Error in main: {e}")
#         raise

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()




















# tested3


# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring
# from lib_parser import parse_lib_file

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 port_name = port.split(":")[0].strip()
#                 port_info = port.split(":")[1].strip() if ":" in port else ""
#                 direction = port_info.split()[0] if port_info else "unknown"
#                 width = port_info.split()[-1] if port_info and len(port_info.split()) > 2 else "1"
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 wire_elem = ET.SubElement(port_elem, "spirit:wire")
#                 ET.SubElement(wire_elem, "spirit:vector").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     lib_cells = {} if not lib_file else parse_lib_file(lib_file)
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file if lib_file else "None",
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     # Collecting files
#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file: {lib_file}" if lib_file else "No library file provided",
#     ])
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))
#     parsed_data["file_processing"]["files_found"] = len(files_to_process)
#     log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

#     # Extract macros
#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith('.vh'):
#             file_macros = extract_macros(file_path)
#             macros.update(file_macros)
#             parsed_data["macro_extraction"]["macros"].update(file_macros)
#             logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#     parsed_data["macro_extraction"]["total_macros"] = len(macros)
#     logging.info(f"Total macros extracted: {len(macros)}")

#     # Parse syntax trees
#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = getattr(diag.location, 'lineNumber', 'Unknown')
#                 column = getattr(diag.location, 'columnNumber', 'Unknown')
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#         except Exception as e:
#             logging.error(f"Error parsing {file_path}: {e}")

#     # Module analysis
#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#     logging.info(f"Total modules parsed: {module_count_total}")

#     # Module processing
#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         module_data = process_file(
#             file_path=file_path,
#             source_text=source_text,
#             all_modules=all_modules,
#             syntax_tree=syntax_tree,
#             macros=macros,
#             parsed_instances=parsed_instances,
#             module_names=module_names,
#             detailed_output=detailed_output,
#             lib_cells=lib_cells
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 module_entry = {
#                     "name": module_name,
#                     "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
#                     "components": components,
#                     "connectivity_report": connections["wires"],
#                     "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items()],
#                     "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                 }
#                 parsed_data["modules"].append(module_entry)
#                 logging.info(f"Processed module {module_name} in {file_path}")

#     # Hierarchy
#     log_section("Module Hierarchy", [])
#     hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     if hierarchy_data is None:
#         logging.error("Failed to generate hierarchy data, setting defaults")
#         hierarchy_data = {"top_level_modules": [], "structure": {}}
#     parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#     parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#     parsed_data["execution_summary"]["execution_time"] = time.time() - start_time
#     parsed_data = convert_sets_to_lists(parsed_data)

#     # Output results
#     for line in detailed_output:
#         print(line)
#     print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#     with open("output.json", "w") as json_file:
#         json.dump(parsed_data, json_file, indent=4)
#     logging.info("Exported parsed data to output.json")

#     if generate_ipxact_flag:
#         generate_ipxact(parsed_data)

# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     logging.info("Starting main execution")
#     process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()

















# # main.py
# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring
# from lib_parser import parse_lib_file

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 parts = port.split(' ')
#                 direction = parts[0]
#                 data_type = parts[1]
#                 width = parts[2] if len(parts) > 2 else '1'
#                 port_name = parts[-1]
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 wire_elem = ET.SubElement(port_elem, "spirit:wire")
#                 ET.SubElement(wire_elem, "spirit:vector").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     lib_cells = {} if not lib_file else parse_lib_file(lib_file)
#     parsed_data = {
#         # "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file if lib_file else "None",
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         # "execution_summary": {
#         #     "execution_time": 0.0
#         # }
#     }

#     # Collecting files
#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file: {lib_file}" if lib_file else "No library file provided",
#     ])
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))
#     parsed_data["file_processing"]["files_found"] = len(files_to_process)
#     log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

#     # Extract macros
#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith('.vh'):
#             file_macros = extract_macros(file_path)
#             macros.update(file_macros)
#             parsed_data["macro_extraction"]["macros"].update(file_macros)
#             logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#     parsed_data["macro_extraction"]["total_macros"] = len(macros)
#     logging.info(f"Total macros extracted: {len(macros)}")

#     # Parse syntax trees
#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = getattr(diag.location, 'lineNumber', 'Unknown')
#                 column = getattr(diag.location, 'columnNumber', 'Unknown')
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#         except Exception as e:
#             logging.error(f"Error parsing {file_path}: {e}")

#     # Module analysis
#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#     logging.info(f"Total modules parsed: {module_count_total}")

#     # Module processing
#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         module_data = process_file(
#             file_path=file_path,
#             source_text=source_text,
#             all_modules=all_modules,
#             syntax_tree=syntax_tree,
#             macros=macros,
#             parsed_instances=parsed_instances,
#             module_names=module_names,
#             detailed_output=detailed_output,
#             lib_cells=lib_cells
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 module_entry = {
#                     "name": module_name,
#                     "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
#                     "components": components,
#                     "connectivity_report": connections["wires"],
#                     "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items() if inst['module'] != 'unknown'],
#                     "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                 }
#                 parsed_data["modules"].append(module_entry)
#                 logging.info(f"Processed module {module_name} in {file_path}")

#     # Hierarchy
#     log_section("Module Hierarchy", [])
#     hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     if hierarchy_data is None:
#         logging.error("Failed to generate hierarchy data, setting defaults")
#         hierarchy_data = {"top_level_modules": [], "structure": {}}
#     parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#     parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#     # Ensure execution_summary is always populated
#     # parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

#     # Output results
#     for line in detailed_output:
#         print(line)
#     # print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#     with open("output.json", "w") as json_file:
#         json.dump(parsed_data, json_file, indent=4)
#     logging.info("Exported parsed data to output.json")

#     if generate_ipxact_flag:
#         generate_ipxact(parsed_data)

#     return parsed_data

# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     logging.info("Starting main execution")
#     process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()










# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring
# from lib_parser import parse_lib_file

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 parts = port.split(' ')
#                 direction = parts[0]
#                 data_type = parts[1]
#                 width = parts[2] if len(parts) > 2 else '1'
#                 port_name = parts[-1]
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 wire_elem = ET.SubElement(port_elem, "spirit:wire")
#                 ET.SubElement(wire_elem, "spirit:vector").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     lib_cells = {} if not lib_file else parse_lib_file(lib_file)
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file if lib_file else "None",
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     # Log lib_cells content
#     if lib_cells:
#         logging.debug(f"Parsed library cells: {lib_cells}")

#     # Collecting files
#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file: {lib_file}" if lib_file else "No library file provided",
#     ])
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))
#     parsed_data["file_processing"]["files_found"] = len(files_to_process)
#     log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

#     # Extract macros
#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith('.vh'):
#             file_macros = extract_macros(file_path)
#             macros.update(file_macros)
#             parsed_data["macro_extraction"]["macros"].update(file_macros)
#             logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#     parsed_data["macro_extraction"]["total_macros"] = len(macros)
#     logging.info(f"Total macros extracted: {len(macros)}")

#     # Parse syntax trees
#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = getattr(diag.location, 'lineNumber', 'Unknown')
#                 column = getattr(diag.location, 'columnNumber', 'Unknown')
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#         except Exception as e:
#             logging.error(f"Error parsing {file_path}: {e}")

#     # Module analysis
#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#     logging.info(f"Total modules parsed: {module_count_total}")

#     # Module processing
#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         module_data = process_file(
#             file_path=file_path,
#             source_text=source_text,
#             all_modules=all_modules,
#             syntax_tree=syntax_tree,
#             macros=macros,
#             parsed_instances=parsed_instances,
#             module_names=module_names,
#             detailed_output=detailed_output,
#             lib_cells=lib_cells
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 module_entry = {
#                     "name": module_name,
#                     "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
#                     "components": components,
#                     "connectivity_report": connections["wires"],
#                     "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items() if inst['module'] != 'unknown'],
#                     "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                 }
#                 parsed_data["modules"].append(module_entry)
#                 logging.info(f"Processed module {module_name} in {file_path}")

#     # Hierarchy
#     log_section("Module Hierarchy", [])
#     hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     if hierarchy_data is None:
#         logging.error("Failed to generate hierarchy data, setting defaults")
#         hierarchy_data = {"top_level_modules": [], "structure": {}}
#     parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#     parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#     # Populate execution_summary
#     parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

#     # Output results
#     for line in detailed_output:
#         print(line)
#     print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#     with open("output.json", "w") as json_file:
#         json.dump(convert_sets_to_lists(parsed_data), json_file, indent=4)
#     logging.info("Exported parsed data to output.json")

#     if generate_ipxact_flag:
#         generate_ipxact(parsed_data)

#     return parsed_data

# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     logging.info("Starting main execution")
#     process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()









# # updated1
# # adding re pattern to extract required data from.v files also
# # identifies counters, registers, muxes, and gates in both .v files (Verilog/SystemVerilog files) and .lib files (library files)



# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring
# from lib_parser import parse_lib_file

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 parts = port.split(' ')
#                 direction = parts[0]
#                 data_type = parts[1]
#                 width = parts[2] if len(parts) > 2 else '1'
#                 port_name = parts[-1]
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 wire_elem = ET.SubElement(port_elem, "spirit:wire")
#                 ET.SubElement(wire_elem, "spirit:vector").text = width
#             tree = ET.ElementTree(root)
#             tree.write(os.path.join(output_dir, f"{module_name}.xml"))
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_dir}/{module_name}.xml")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     lib_cells = {} if not lib_file else parse_lib_file(lib_file)
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file if lib_file else "None",
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     # Log lib_cells content
#     if lib_cells:
#         logging.debug(f"Parsed library cells: {lib_cells}")

#     # Collecting files
#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file: {lib_file}" if lib_file else "No library file provided",
#     ])
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))
#     parsed_data["file_processing"]["files_found"] = len(files_to_process)
#     log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

#     # Extract macros
#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith('.vh'):
#             file_macros = extract_macros(file_path)
#             macros.update(file_macros)
#             parsed_data["macro_extraction"]["macros"].update(file_macros)
#             logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#     parsed_data["macro_extraction"]["total_macros"] = len(macros)
#     logging.info(f"Total macros extracted: {len(macros)}")

#     # Parse syntax trees
#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = getattr(diag.location, 'lineNumber', 'Unknown')
#                 column = getattr(diag.location, 'columnNumber', 'Unknown')
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#         except Exception as e:
#             logging.error(f"Error parsing {file_path}: {e}")

#     # Module analysis
#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#     logging.info(f"Total modules parsed: {module_count_total}")

#     # Module processing
#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         module_data = process_file(
#             file_path=file_path,
#             source_text=source_text,
#             all_modules=all_modules,
#             syntax_tree=syntax_tree,
#             macros=macros,
#             parsed_instances=parsed_instances,
#             module_names=module_names,
#             detailed_output=detailed_output,
#             lib_cells=lib_cells
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 module_entry = {
#                     "name": module_name,
#                     "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
#                     "components": components,
#                     "connectivity_report": connections["wires"],
#                     "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items() if inst['module'] != 'unknown'],
#                     "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                 }
#                 parsed_data["modules"].append(module_entry)
#                 logging.info(f"Processed module {module_name} in {file_path}")

#     # Hierarchy
#     log_section("Module Hierarchy", [])
#     hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     if hierarchy_data is None:
#         logging.error("Failed to generate hierarchy data, setting defaults")
#         hierarchy_data = {"top_level_modules": [], "structure": {}}
#     parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#     parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#     # Populate execution_summary
#     parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

#     # Output results
#     for line in detailed_output:
#         print(line)
#     print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")


#     # # Save output.json in generated_op_files folder
#     os.makedirs("generated_op_files", exist_ok=True)
#     with open(os.path.join("generated_op_files", "output.json"), "w") as json_file:
#         json.dump(convert_sets_to_lists(parsed_data), json_file, indent=4)
#     # with open("output.json", "w") as json_file:
#     #     json.dump(convert_sets_to_lists(parsed_data), json_file, indent=4)
#     logging.info("Exported parsed data to output.json")

#     if generate_ipxact_flag:
#         generate_ipxact(parsed_data)

#     return parsed_data



# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     logging.info("Starting main execution")
#     logging.debug("Debug test: main function started with path=%s, lib=%s, verbosity=%s",
#                   args.path, args.lib, args.verbosity)  # added
#     process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)



# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()











# updated2
# before adding new commands

# # main.py
# import os
# import argparse
# import time
# import logging
# import json
# from parser import parse_module_ports, parse_components, process_file, preprocess_verilog
# from utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
# from monitor import start_monitoring
# from lib_parser import parse_lib_file

# def convert_sets_to_lists(data):
#     if isinstance(data, dict):
#         return {k: convert_sets_to_lists(v) for k, v in data.items()}
#     elif isinstance(data, set):
#         return list(data)
#     elif isinstance(data, list):
#         return [convert_sets_to_lists(item) for item in data]
#     else:
#         return data

# def generate_ipxact(parsed_data, output_dir="ipxact_output"):
#     try:
#         import xml.etree.ElementTree as ET
#         os.makedirs(output_dir, exist_ok=True)
#         for module in parsed_data["modules"]:
#             module_name = module["name"]
#             root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
#             ET.SubElement(root, "spirit:name").text = module_name
#             ET.SubElement(root, "spirit:version").text = "1.0"
#             ports_elem = ET.SubElement(root, "spirit:ports")
#             for port in module.get("ports", []):
#                 port_elem = ET.SubElement(ports_elem, "spirit:port")
#                 parts = port.split(' ')
#                 direction = parts[0]
#                 data_type = parts[1]
#                 width = parts[2] if len(parts) > 2 else '1'
#                 port_name = parts[-1]
#                 ET.SubElement(port_elem, "spirit:name").text = port_name
#                 ET.SubElement(port_elem, "spirit:direction").text = direction
#                 wire_elem = ET.SubElement(port_elem, "spirit:wire")
#                 ET.SubElement(wire_elem, "spirit:vector").text = width
#             tree = ET.ElementTree(root)
#             output_path = os.path.join(output_dir, f"{module_name}.xml")
#             tree.write(output_path)
#             logging.info(f"Generated IP-XACT file for {module_name} at {output_path}")
#     except Exception as e:
#         logging.error(f"Error generating IP-XACT files: {e}")

# def process_path(path, lib_file, extensions=(".sv", ".v", ".vh", ".svh", ".verilog"), generate_ipxact_flag=False):
#     start_time = time.time()
#     all_modules = []
#     files_to_process = []
#     syntax_trees = []
#     connections_by_module = {}
#     module_names = set()
#     detailed_output = []
#     macros = {}
#     parsed_instances = set()
#     lib_cells = {} if not lib_file else parse_lib_file(lib_file)
#     parsed_data = {
#         "system_usage": {},
#         "file_processing": {
#             "path": path,
#             "library_file": lib_file if lib_file else "None",
#             "files_found": 0
#         },
#         "macro_extraction": {
#             "total_macros": 0,
#             "macros": {}
#         },
#         "module_analysis": {
#             "total_modules_parsed": 0,
#             "module_names": []
#         },
#         "modules": [],
#         "hierarchy": {
#             "top_level_modules": [],
#             "structure": {}
#         },
#         "execution_summary": {
#             "execution_time": 0.0
#         }
#     }

#     if lib_cells:
#         logging.debug(f"Parsed library cells: {lib_cells}")

#     log_section("File Processing", [
#         f"Starting processing of path: {path}",
#         f"Library file: {lib_file}" if lib_file else "No library file provided",
#     ])
#     if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
#         files_to_process.append(lib_file)
#     if os.path.isfile(path) and path.endswith(extensions):
#         files_to_process.append(path)
#     elif os.path.isdir(path):
#         for root, _, files in os.walk(path):
#             for file in files:
#                 if file.endswith(extensions):
#                     files_to_process.append(os.path.join(root, file))
#     parsed_data["file_processing"]["files_found"] = len(files_to_process)
#     log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

#     log_section("Macro Extraction", [])
#     include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
#     for file_path in files_to_process:
#         if file_path.endswith(('.vh', '.svh')):
#             file_macros = extract_macros(file_path)
#             macros.update(file_macros)
#             parsed_data["macro_extraction"]["macros"].update(file_macros)
#             logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
#     parsed_data["macro_extraction"]["total_macros"] = len(macros)
#     logging.info(f"Total macros extracted: {len(macros)}")

#     log_section("Syntax Tree Parsing", [])
#     import pyslang
#     source_manager = pyslang.SourceManager()
#     for include_dir in include_dirs:
#         source_manager.addUserDirectories(include_dir)
#     for file_path in files_to_process:
#         if not file_path.endswith(('.sv', '.v', '.verilog')):
#             continue
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 source_text = f.read()
#             preprocessed_text = preprocess_verilog(file_path, source_text, macros)
#             source_buffer = source_manager.assignText(file_path, preprocessed_text)
#             syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
#             syntax_trees.append((file_path, syntax_tree, preprocessed_text))
#             for diag in syntax_tree.diagnostics:
#                 message = str(diag.message) if hasattr(diag, 'message') else str(diag)
#                 line = getattr(diag.location, 'lineNumber', 'Unknown')
#                 column = getattr(diag.location, 'columnNumber', 'Unknown')
#                 logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
#         except FileNotFoundError:
#             logging.error(f"File {file_path} not found")
#             continue
#         except Exception as e:
#             logging.error(f"Error parsing {file_path}: {e}")
#             continue

#     log_section("Module Analysis", [])
#     module_count_total = 0
#     for file_path, syntax_tree, _ in syntax_trees:
#         module_count = 0
#         for member in syntax_tree.root.members:
#             if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
#                 module_name = getattr(member.header, 'name', None)
#                 if module_name is None or not hasattr(module_name, 'valueText'):
#                     continue
#                 module_name = module_name.valueText
#                 ports, _ = parse_module_ports(member, macros)
#                 all_modules.append({"name": module_name, "ports": ports, "file": file_path})
#                 parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
#                 module_names.add(module_name)
#                 module_count += 1
#                 module_count_total += 1
#         logging.info(f"Parsed {module_count} modules in {file_path}")
#     parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
#     logging.info(f"Total modules parsed: {module_count_total}")

#     log_section("Module Processing", [])
#     for file_path, syntax_tree, source_text in syntax_trees:
#         module_data = process_file(
#             file_path=file_path,
#             source_text=source_text,
#             all_modules=all_modules,
#             syntax_tree=syntax_tree,
#             macros=macros,
#             parsed_instances=parsed_instances,
#             module_names=module_names,
#             detailed_output=detailed_output,
#             lib_cells=lib_cells
#         )
#         if module_data:
#             for module_name, connections, components in module_data:
#                 if file_path not in connections_by_module:
#                     connections_by_module[file_path] = []
#                 connections_by_module[file_path].append({
#                     "name": module_name,
#                     "connections": connections,
#                     "components": components
#                 })
#                 module_entry = {
#                     "name": module_name,
#                     "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
#                     "components": components,
#                     "connectivity_report": connections["wires"],
#                     "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items() if inst['module'] != 'unknown'],
#                     "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
#                 }
#                 parsed_data["modules"].append(module_entry)
#                 logging.info(f"Processed module {module_name} in {file_path}")

#     log_section("Module Hierarchy", [])
#     hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
#     if hierarchy_data is None:
#         logging.error("Failed to generate hierarchy data, setting defaults")
#         hierarchy_data = {"top_level_modules": [], "structure": {}}
#     parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
#     parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

#     parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

#     for line in detailed_output:
#         print(line)
#     print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

#     os.makedirs("generated_op_files", exist_ok=True)
#     output_json_path = os.path.join("generated_op_files", "output.json")
#     try:
#         with open(output_json_path, "w") as json_file:
#             json.dump(convert_sets_to_lists(parsed_data), json_file, indent=4)
#         logging.info(f"Exported parsed data to {output_json_path}")
#     except Exception as e:
#         logging.error(f"Error writing to {output_json_path}: {e}")

#     if generate_ipxact_flag:
#         generate_ipxact(parsed_data)

#     return parsed_data

# def main():
#     parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
#     parser.add_argument("path", help="Path to a Verilog file or directory")
#     parser.add_argument("-l", "--lib", help="Path to library file", default=None)
#     parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
#                         help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
#     parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
#     args = parser.parse_args()
#     setup_logging(args.verbosity)
#     logging.info("Starting main execution")
#     logging.debug("Debug test: main function started with path=%s, lib=%s, verbosity=%s",
#                   args.path, args.lib, args.verbosity)
#     process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)

# if __name__ == "__main__":
#     start_monitoring(interval=5)
#     main()




# after adding new commands


import os
import argparse
import time
import logging
import json
from .parser import parse_module_ports, parse_components, process_file, preprocess_verilog
from .utility import setup_logging, generate_hierarchy_dot, extract_macros, log_section
from .monitor import start_monitoring
from .lib_parser import parse_lib_file

def convert_sets_to_lists(data):
    if isinstance(data, dict):
        return {k: convert_sets_to_lists(v) for k, v in data.items()}
    elif isinstance(data, set):
        return list(data)
    elif isinstance(data, list):
        return [convert_sets_to_lists(item) for item in data]
    else:
        return data

def generate_ipxact(parsed_data, output_dir="ipxact_output"):
    try:
        import xml.etree.ElementTree as ET
        os.makedirs(output_dir, exist_ok=True)
        for module in parsed_data["modules"]:
            module_name = module["name"]
            root = ET.Element("spirit:component", xmlns_spirit="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
            ET.SubElement(root, "spirit:name").text = module_name
            ET.SubElement(root, "spirit:version").text = "1.0"
            ports_elem = ET.SubElement(root, "spirit:ports")
            for port in module.get("ports", []):
                port_elem = ET.SubElement(ports_elem, "spirit:port")
                parts = port.split(' ')
                direction = parts[0]
                data_type = parts[1]
                width = parts[2] if len(parts) > 2 else '1'
                port_name = parts[-1]
                ET.SubElement(port_elem, "spirit:name").text = port_name
                ET.SubElement(port_elem, "spirit:direction").text = direction
                wire_elem = ET.SubElement(port_elem, "spirit:wire")
                ET.SubElement(wire_elem, "spirit:vector").text = width
            tree = ET.ElementTree(root)
            output_path = os.path.join(output_dir, f"{module_name}.xml")
            tree.write(output_path)
            logging.info(f"Generated IP-XACT file for {module_name} at {output_path}")
    except Exception as e:
        logging.error(f"Error generating IP-XACT files: {e}")

def process_path(path, lib_file, extensions=(".sv", ".v", ".vh", ".svh", ".verilog"), generate_ipxact_flag=False):
    start_time = time.time()
    all_modules = []
    files_to_process = []
    syntax_trees = []
    connections_by_module = {}
    module_names = set()
    detailed_output = []
    macros = {}
    parsed_instances = set()
    lib_cells = {} if not lib_file else parse_lib_file(lib_file)
    parsed_data = {
        "system_usage": {},
        "file_processing": {
            "path": path,
            "library_file": lib_file if lib_file else "None",
            "files_found": 0
        },
        "macro_extraction": {
            "total_macros": 0,
            "macros": {}
        },
        "module_analysis": {
            "total_modules_parsed": 0,
            "module_names": []
        },
        "modules": [],
        "hierarchy": {
            "top_level_modules": [],
            "structure": {}
        },
        "execution_summary": {
            "execution_time": 0.0
        }
    }

    if lib_cells:
        logging.debug(f"Parsed library cells: {lib_cells}")

    log_section("File Processing", [
        f"Starting processing of path: {path}",
        f"Library file: {lib_file}" if lib_file else "No library file provided",
    ])
    if lib_file and os.path.isfile(lib_file) and lib_file.endswith(extensions):
        files_to_process.append(lib_file)
    if os.path.isfile(path) and path.endswith(extensions):
        files_to_process.append(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(extensions):
                    files_to_process.append(os.path.join(root, file))
    parsed_data["file_processing"]["files_found"] = len(files_to_process)
    log_section("File Processing", [f"Found {len(files_to_process)} files to process"])

    log_section("Macro Extraction", [])
    include_dirs = [os.path.abspath(os.path.dirname(path)) if os.path.isfile(path) else os.path.abspath(path)]
    for file_path in files_to_process:
        if file_path.endswith(('.vh', '.svh')):
            file_macros = extract_macros(file_path)
            macros.update(file_macros)
            parsed_data["macro_extraction"]["macros"].update(file_macros)
            logging.info(f"Extracted {len(file_macros)} macros from {file_path}")
    parsed_data["macro_extraction"]["total_macros"] = len(macros)
    logging.info(f"Total macros extracted: {len(macros)}")

    log_section("Syntax Tree Parsing", [])
    import pyslang
    source_manager = pyslang.SourceManager()
    for include_dir in include_dirs:
        source_manager.addUserDirectories(include_dir)
    for file_path in files_to_process:
        if not file_path.endswith(('.sv', '.v', '.verilog')):
            continue
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_text = f.read()
            preprocessed_text = preprocess_verilog(file_path, source_text, macros)
            source_buffer = source_manager.assignText(file_path, preprocessed_text)
            syntax_tree = pyslang.SyntaxTree.fromBuffer(source_buffer, source_manager)
            syntax_trees.append((file_path, syntax_tree, preprocessed_text))
            for diag in syntax_tree.diagnostics:
                message = str(diag.message) if hasattr(diag, 'message') else str(diag)
                line = getattr(diag.location, 'lineNumber', 'Unknown')
                column = getattr(diag.location, 'columnNumber', 'Unknown')
                logging.error(f"Diagnostic for {file_path} at line {line}:{column}: {message}")
        except FileNotFoundError:
            logging.error(f"File {file_path} not found")
            continue
        except Exception as e:
            logging.error(f"Error parsing {file_path}: {e}")
            continue

    log_section("Module Analysis", [])
    module_count_total = 0
    for file_path, syntax_tree, _ in syntax_trees:
        module_count = 0
        for member in syntax_tree.root.members:
            if member.kind == pyslang.SyntaxKind.ModuleDeclaration:
                module_name = getattr(member.header, 'name', None)
                if module_name is None or not hasattr(module_name, 'valueText'):
                    continue
                module_name = module_name.valueText
                ports, _ = parse_module_ports(member, macros)
                all_modules.append({"name": module_name, "ports": ports, "file": file_path})
                parsed_data["module_analysis"]["module_names"].append({"name": module_name, "file": file_path})
                module_names.add(module_name)
                module_count += 1
                module_count_total += 1
        logging.info(f"Parsed {module_count} modules in {file_path}")
    parsed_data["module_analysis"]["total_modules_parsed"] = module_count_total
    logging.info(f"Total modules parsed: {module_count_total}")

    log_section("Module Processing", [])
    for file_path, syntax_tree, source_text in syntax_trees:
        module_data = process_file(
            file_path=file_path,
            source_text=source_text,
            all_modules=all_modules,
            syntax_tree=syntax_tree,
            macros=macros,
            parsed_instances=parsed_instances,
            module_names=module_names,
            detailed_output=detailed_output,
            lib_cells=lib_cells
        )
        if module_data:
            for module_name, connections, components in module_data:
                if file_path not in connections_by_module:
                    connections_by_module[file_path] = []
                connections_by_module[file_path].append({
                    "name": module_name,
                    "connections": connections,
                    "components": components
                })
                module_entry = {
                    "name": module_name,
                    "ports": next(m["ports"] for m in all_modules if m["name"] == module_name),
                    "components": components,
                    "connectivity_report": connections["wires"],
                    "module_to_module_connectivity": [f"{module_name} -> {inst['module']} ({inst_name})" for inst_name, inst in connections["instances"].items() if inst['module'] != 'unknown'],
                    "connectivity_issues": [f"Unconnected wire: {w}" for w in connections["wires"] if not connections["wires"][w]["source"] and not connections["wires"][w]["sinks"]]
                }
                parsed_data["modules"].append(module_entry)
                logging.info(f"Processed module {module_name} in {file_path}")

    log_section("Module Hierarchy", [])
    hierarchy_data = generate_hierarchy_dot(all_modules, connections_by_module, detailed_output)
    if hierarchy_data is None:
        logging.error("Failed to generate hierarchy data, setting defaults")
        hierarchy_data = {"top_level_modules": [], "structure": {}}
    parsed_data["hierarchy"]["top_level_modules"] = hierarchy_data["top_level_modules"]
    parsed_data["hierarchy"]["structure"] = hierarchy_data["structure"]

    parsed_data["execution_summary"]["execution_time"] = time.time() - start_time

    for line in detailed_output:
        print(line)
    print(f"Total execution time: {parsed_data['execution_summary']['execution_time']:.2f} seconds")

    os.makedirs("generated_op_files", exist_ok=True)
    output_json_path = os.path.join("generated_op_files", "output.json")
    try:
        with open(output_json_path, "w") as json_file:
            json.dump(convert_sets_to_lists(parsed_data), json_file, indent=4)
        logging.info(f"Exported parsed data to {output_json_path}")
    except Exception as e:
        logging.error(f"Error writing to {output_json_path}: {e}")

    if generate_ipxact_flag:
        generate_ipxact(parsed_data)

    return parsed_data

def main():
    parser = argparse.ArgumentParser(description="Analyze Verilog/SystemVerilog files.")
    parser.add_argument("path", help="Path to a Verilog file or directory")
    parser.add_argument("-l", "--lib", help="Path to library file", default=None)
    parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2],
                        help="Verbosity level: 0=ERROR, 1=INFO, 2=DEBUG")
    parser.add_argument("--ipxact", action="store_true", help="Generate IP-XACT files")
    parser.add_argument("--max_lines", type=int, help="Limit log to N lines")
    parser.add_argument("--filter_level", choices=["DEBUG", "INFO", "ERROR"], help="Filter logs by level")
    args = parser.parse_args()
    setup_logging(args.verbosity, max_lines=args.max_lines, filter_level=args.filter_level)
    logging.info("Starting main execution")
    logging.debug("Debug test: main function started with path=%s, lib=%s, verbosity=%s",
                  args.path, args.lib, args.verbosity)
    process_path(os.path.abspath(args.path), args.lib, generate_ipxact_flag=args.ipxact)

if __name__ == "__main__":
    start_monitoring(interval=5)
    main()