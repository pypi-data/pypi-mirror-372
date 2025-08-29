# import re
# import logging

# def setup_logging(verbosity):
#     level = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}.get(verbosity, logging.INFO)
#     logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")
#     if verbosity == 2:
#         logging.debug("Logging setup completed")

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 if line.strip().startswith('`define'):
#                     parts = line.strip().split()
#                     if len(parts) >= 2:
#                         macro_name = parts[1]
#                         macro_value = ' '.join(parts[2:]) or '1'
#                         macros[macro_name] = macro_value
#                         logging.debug(f"Extracted macro from {file_path}: {macro_name} = {macro_value}")
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#     return macros

# # def extract_macros(file_path):
# #     macros = {}
# #     try:
# #         with open(file_path, 'r', encoding='utf-8') as f:
# #             content = f.read()
# #         macro_pattern = re.compile(r'`define\s+(\w+)\s+([\w\d]+)')
# #         for match in macro_pattern.finditer(content):
# #             macro_name, macro_value = match.groups()
# #             try:
# #                 macro_value = int(macro_value) if macro_value.isdigit() else macro_value
# #                 macros[macro_name] = macro_value
# #                 logging.debug(f"Extracted macro from {file_path}: {macro_name} = {macro_value}")
# #             except ValueError:
# #                 logging.warning(f"Non-integer macro value for {macro_name} in {file_path}: {macro_value}")
# #                 macros[macro_name] = macro_value
# #         return macros
# #     except Exception as e:
# #         logging.error(f"Error reading macros from {file_path}: {e}")
# #         return {}

# def detect_counter(name, source_text):
#     pattern = rf'\b{name}\s*<=\s*{name}\s*\+.*?\d+|{name}\s*-\s*\d+\b'
#     result = bool(re.search(pattern, source_text, re.MULTILINE))
#     if logging.getLogger().isEnabledFor(logging.DEBUG):
#         logging.debug(f"Counter detection for {name}: {'detected' if result else 'not detected'}")
#     return result

# def log_section(section_name, messages):
#     logging.info(f"=== {section_name} ===")
#     for msg in messages:
#         logging.info(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     dot_content = ["digraph G {", "  rankdir=BT;"]
#     hierarchy = {m["name"]: set() for m in all_modules}
#     instantiated_modules = set()
#     signal_connections = []

#     for file_path, module_data_list in connections_by_module.items():
#         for conn_data in module_data_list:
#             module_name = conn_data["name"]
#             for inst_name, inst_conn in conn_data["connections"]["instances"].items():
#                 sub_module = inst_conn["module"]
#                 if sub_module in [m["name"] for m in all_modules]:
#                     hierarchy[module_name].add(sub_module)
#                     instantiated_modules.add(sub_module)
#                 else:
#                     logging.warning(f"Submodule {sub_module} in {module_name} not found in module list")
#                 for port_name, signal in inst_conn["ports"].items():
#                     base_signal = signal.split('[')[0]
#                     signal_connections.append(f"{sub_module} instance ({inst_name}.{port_name}) -> {module_name} wire ({signal})")

#     for module_name, submodules in hierarchy.items():
#         for submodule in submodules:
#             dot_content.append(f'  "{submodule}" -> "{module_name}";')
#         dot_content.append(f'  "{module_name}" [shape=box];')
#     dot_content.append("}")

#     try:
#         with open("hierarchy2.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info(f"Generated hierarchy2.dot with {len(all_modules)} modules")
#     except Exception as e:
#         logging.error(f"Error writing hierarchy2.dot: {e}")

#     # Append hierarchy to detailed_output
#     detailed_output.append("\nModule Hierarchy:")
#     top_level = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]
#     if not top_level:
#         detailed_output.append("  (no top-level modules found)")
#         logging.info("No top-level modules found in hierarchy")
#     else:
#         detailed_output.append(f"Found {len(top_level)} top-level modules: {', '.join(top_level)}")
#         logging.info(f"Found {len(top_level)} top-level modules: {', '.join(top_level)}")

#         def print_hierarchy(module, indent=0, visited=None):
#             if visited is None:
#                 visited = set()
#             if module in visited:
#                 detailed_output.append("  " * indent + f"- {module} (recursive)")
#                 return
#             visited.add(module)
#             detailed_output.append("  " * indent + f"- {module}")
#             for submodule in sorted(hierarchy.get(module, [])):
#                 print_hierarchy(submodule, indent + 1, visited.copy())

#         for top_module in sorted(top_level):
#             print_hierarchy(top_module)




# #tested

# import re
# import logging

# def setup_logging(verbosity):
#     level = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}.get(verbosity, logging.INFO)
#     logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read()
#         macro_pattern = re.compile(r'`define\s+(\w+)\s+([\w\d\'hbx]+)')
#         for match in macro_pattern.finditer(content):
#             macro_name, macro_value = match.groups()
#             macros[macro_name] = macro_value
#             logging.debug(f"Extracted macro from {file_path}: {macro_name} = {macro_value}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return {}

# def detect_counter(name, source_text):
#     patterns = [
#         rf'\b{name}\s*<=\s*{name}\s*[\+-]\s*\d+',  # name <= name + 1
#         rf'\b{name}\s*<=\s*{name}\s*[\+-]\s*\w+',  # name <= name + var
#         rf'\b{name}\s*<=\s*\d+\s*[\+-]\s*{name}'   # name <= 1 + name
#     ]
#     for pattern in patterns:
#         if re.search(pattern, source_text, re.MULTILINE):
#             logging.debug(f"Counter detected for {name} with pattern {pattern}")
#             return True
#     logging.debug(f"Counter detection for {name}: not detected")
#     return False

# def log_section(section_name, messages):
#     logging.info(f"=== {section_name} ===")
#     for msg in messages:
#         logging.info(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     dot_content = ["digraph G {", "  rankdir=BT;"]
#     hierarchy = {"top_level_modules": [], "structure": {m["name"]: set() for m in all_modules}}
#     instantiated_modules = set()

#     for file_path, module_data_list in connections_by_module.items():
#         for conn_data in module_data_list:
#             module_name = conn_data["name"]
#             for inst_name, inst_conn in conn_data["connections"]["instances"].items():
#                 sub_module = inst_conn["module"]
#                 if sub_module in [m["name"] for m in all_modules]:
#                     hierarchy["structure"][module_name].add(sub_module)
#                     instantiated_modules.add(sub_module)

#     hierarchy["top_level_modules"] = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]

#     for module_name, submodules in hierarchy["structure"].items():
#         for submodule in submodules:
#             dot_content.append(f'  "{submodule}" -> "{module_name}";')
#         dot_content.append(f'  "{module_name}" [shape=box];')
#     dot_content.append("}")

#     try:
#         with open("hierarchy.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info(f"Generated hierarchy.dot with {len(all_modules)} modules")
#     except Exception as e:
#         logging.error(f"Error writing hierarchy.dot: {e}")

#     detailed_output.append("\nModule Hierarchy:")
#     detailed_output.append(f"Found {len(hierarchy['top_level_modules'])} top-level modules: {', '.join(hierarchy['top_level_modules'])}")

#     def print_hierarchy(module, indent=0, visited=None):
#         if visited is None:
#             visited = set()
#         if module in visited:
#             detailed_output.append("  " * indent + f"- {module} (recursive)")
#             return
#         visited.add(module)
#         detailed_output.append("  " * indent + f"- {module}")
#         for submodule in sorted(hierarchy["structure"].get(module, [])):
#             print_hierarchy(submodule, indent + 1, visited.copy())

#     for top_module in sorted(hierarchy["top_level_modules"]):
#         print_hierarchy(top_module)

#     return hierarchy







# #tested2
# import re
# import logging

# def setup_logging(verbosity):
#     level = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}.get(verbosity, logging.INFO)
#     logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read()
#         macro_pattern = re.compile(r'`define\s+(\w+)\s+([\w\d\'hbx]+)')
#         for match in macro_pattern.finditer(content):
#             macro_name, macro_value = match.groups()
#             macros[macro_name] = macro_value
#             logging.debug(f"Extracted macro from {file_path}: {macro_name} = {macro_value}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return {}

# def detect_counter(name, source_text):
#     patterns = [
#         rf'\b{name}\s*<=\s*{name}\s*[\+-]\s*\d+',  # name <= name + 1
#         rf'\b{name}\s*<=\s*{name}\s*[\+-]\s*\w+',  # name <= name + var
#         rf'\b{name}\s*<=\s*\d+\s*[\+-]\s*{name}'   # name <= 1 + name
#     ]
#     for pattern in patterns:
#         if re.search(pattern, source_text, re.MULTILINE):
#             logging.debug(f"Counter detected for {name} with pattern {pattern}")
#             return True
#     logging.debug(f"Counter detection for {name}: not detected")
#     return False

# def log_section(section_name, messages):
#     logging.info(f"=== {section_name} ===")
#     for msg in messages:
#         logging.info(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     dot_content = ["digraph G {", "  rankdir=BT;"]
#     hierarchy = {"top_level_modules": [], "structure": {m["name"]: set() for m in all_modules}}
#     instantiated_modules = set()

#     for file_path, module_data_list in connections_by_module.items():
#         for conn_data in module_data_list:
#             module_name = conn_data["name"]
#             for inst_name, inst_conn in conn_data["connections"]["instances"].items():
#                 sub_module = inst_conn["module"]
#                 if sub_module in [m["name"] for m in all_modules]:
#                     hierarchy["structure"][module_name].add(sub_module)
#                     instantiated_modules.add(sub_module)

#     hierarchy["top_level_modules"] = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]

#     for module_name, submodules in hierarchy["structure"].items():
#         for submodule in submodules:
#             dot_content.append(f'  "{submodule}" -> "{module_name}";')
#         dot_content.append(f'  "{module_name}" [shape=box];')
#     dot_content.append("}")

#     try:
#         with open("hierarchy.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info(f"Generated hierarchy.dot with {len(all_modules)} modules")
#     except Exception as e:
#         logging.error(f"Error writing hierarchy.dot: {e}")

#     detailed_output.append("\nModule Hierarchy:")
#     detailed_output.append(f"Found {len(hierarchy['top_level_modules'])} top-level modules: {', '.join(hierarchy['top_level_modules'])}")

#     def print_hierarchy(module, indent=0, visited=None):
#         if visited is None:
#             visited = set()
#         if module in visited:
#             detailed_output.append("  " * indent + f"- {module} (recursive)")
#             return
#         visited.add(module)
#         detailed_output.append("  " * indent + f"- {module}")
#         for submodule in sorted(hierarchy["structure"].get(module, [])):
#             print_hierarchy(submodule, indent + 1, visited.copy())

#     for top_module in sorted(hierarchy["top_level_modules"]):
#         print_hierarchy(top_module)

#     return hierarchy






# import re
# import logging

# def setup_logging(verbosity):
#     level = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}.get(verbosity, logging.INFO)
#     logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s", force=True)

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             content = f.read()
#         macro_pattern = re.compile(r'`define\s+(\w+)\s+([\w\d\'hbx]+)')
#         for match in macro_pattern.finditer(content):
#             macro_name, macro_value = match.groups()
#             macros[macro_name] = macro_value
#             logging.debug(f"Extracted macro from {file_path}: {macro_name} = {macro_value}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return {}

# def detect_counter(name, source_text):
#     patterns = [
#         rf'\b{name}\s*<=\s*{name}\s*[\+-]\s*\d+',  # name <= name + 1
#         rf'\b{name}\s*<=\s*{name}\s*[\+-]\s*\w+',  # name <= name + var
#         rf'\b{name}\s*<=\s*\d+\s*[\+-]\s*{name}'   # name <= 1 + name
#     ]
#     for pattern in patterns:
#         if re.search(pattern, source_text, re.MULTILINE):
#             logging.debug(f"Counter detected for {name} with pattern {pattern}")
#             return True
#     logging.debug(f"Counter detection for {name}: not detected")
#     return False

# def log_section(section_name, messages):
#     logging.info(f"=== {section_name} ===")
#     for msg in messages:
#         logging.info(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     dot_content = ["digraph G {", "  rankdir=BT;"]
#     hierarchy = {"top_level_modules": [], "structure": {m["name"]: set() for m in all_modules}}
#     instantiated_modules = set()

#     for file_path, module_data_list in connections_by_module.items():
#         for conn_data in module_data_list:
#             module_name = conn_data["name"]
#             for inst_name, inst_conn in conn_data["connections"]["instances"].items():
#                 sub_module = inst_conn["module"]
#                 if sub_module in [m["name"] for m in all_modules]:
#                     hierarchy["structure"][module_name].add(sub_module)
#                     instantiated_modules.add(sub_module)

#     hierarchy["top_level_modules"] = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]

#     for module_name, submodules in hierarchy["structure"].items():
#         for submodule in submodules:
#             dot_content.append(f'  "{submodule}" -> "{module_name}";')
#         dot_content.append(f'  "{module_name}" [shape=box];')
#     dot_content.append("}")

#     try:
#         with open("hierarchy.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info(f"Generated hierarchy.dot with {len(all_modules)} modules")
#     except Exception as e:
#         logging.error(f"Error writing hierarchy.dot: {e}")

#     detailed_output.append("\nModule Hierarchy:")
#     detailed_output.append(f"Found {len(hierarchy['top_level_modules'])} top-level modules: {', '.join(hierarchy['top_level_modules'])}")

#     def print_hierarchy(module, indent=0, visited=None):
#         if visited is None:
#             visited = set()
#         if module in visited:
#             detailed_output.append("  " * indent + f"- {module} (recursive)")
#             return
#         visited.add(module)
#         detailed_output.append("  " * indent + f"- {module}")
#         for submodule in sorted(hierarchy["structure"].get(module, [])):
#             print_hierarchy(submodule, indent + 1, visited.copy())

#     for top_module in sorted(hierarchy["top_level_modules"]):
#         print_hierarchy(top_module)

#     return hierarchy





































# tested3







# import logging
# import re
# import os

# def setup_logging(verbosity):
#     levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
#     logging.basicConfig(
#         level=levels.get(verbosity, logging.INFO),
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler('debug.log'),
#             logging.StreamHandler()
#         ]
#     )

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if line.startswith('`define'):
#                     match = re.match(r'`define\s+(\w+)\s+(.+)', line)
#                     if match:
#                         macro_name, macro_value = match.groups()
#                         macros[macro_name] = macro_value.strip()
#                         logging.debug(f"Extracted macro: `{macro_name}` = {macro_value}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return macros

# def detect_counter(text):
#     return bool(re.search(r'\w+\s*\+=\s*1|\w+\s*=\s*\w+\s*\+\s*1', text))

# def log_section(title, messages, detailed_output=None):
#     logging.info(f"\n=== {title} ===")
#     if detailed_output is not None:
#         detailed_output.append(f"\n=== {title} ===")
#     for msg in messages:
#         logging.info(msg)
#         if detailed_output is not None:
#             detailed_output.append(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     try:
#         instantiated_modules = set()
#         for file_path, modules in connections_by_module.items():
#             for module in modules:
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     instantiated_modules.add(inst["module"])
#                     logging.debug(f"Detected instantiated module: {inst['module']} in {module['name']}")
#         top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]
        
#         dot_content = ["digraph G {", '  rankdir=LR;']
#         structure = {}
#         for file_path, modules in connections_by_module.items():
#             structure[file_path] = []
#             for module in modules:
#                 module_name = module["name"]
#                 structure[file_path].append(module_name)
#                 dot_content.append(f'  "{module_name}";')
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
        
#         dot_content.append("}")
#         with open("hierarchy.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info("Generated hierarchy.dot")
#         log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
#         if not instantiated_modules:
#             logging.warning("No instantiated modules detected, hierarchy may be incomplete.")
        
#         return {
#             "top_level_modules": top_level_modules,
#             "structure": structure
#         }
#     except Exception as e:
#         logging.error(f"Error generating hierarchy: {e}")
#         return {"top_level_modules": [], "structure": {}}

















# import logging
# import re
# import os

# def setup_logging(verbosity):
#     levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
#     # logging.basicConfig(
#     #     level=levels.get(verbosity, logging.INFO),
#     #     format='%(asctime)s - %(levelname)s - %(message)s',
#     #     handlers=[
#     #         logging.FileHandler('debug.log'),
#     #         logging.StreamHandler()
#     #     ]
#     # )

#     logging.basicConfig(
#         level=levels.get(verbosity, logging.INFO),
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.FileHandler('debug.log'),
#             logging.StreamHandler()
#         ]
#     )

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if line.startswith('`define'):
#                     match = re.match(r'`define\s+(\w+)\s+(.+)', line)
#                     if match:
#                         macro_name, macro_value = match.groups()
#                         macros[macro_name] = macro_value.strip()
#                         logging.debug(f"Extracted macro: `{macro_name}` = {macro_value}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return macros

# def detect_counter(text):
#     return bool(re.search(r'\w+\s*\+=\s*1|\w+\s*=\s*\w+\s*\+\s*1', text))

# def log_section(title, messages, detailed_output=None):
#     logging.info(f"\n=== {title} ===")
#     if detailed_output is not None:
#         detailed_output.append(f"\n=== {title} ===")
#     for msg in messages:
#         logging.info(msg)
#         if detailed_output is not None:
#             detailed_output.append(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     try:
#         instantiated_modules = set()
#         for file_path, modules in connections_by_module.items():
#             for module in modules:
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if module["name"] != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:  # Filter self-loops and invalid
#                         instantiated_modules.add(inst["module"])
#                     else:
#                         logging.debug(f"Filtered invalid edge: {module['name']} -> {inst['module']} [label=\"{inst_name}\"]")
#         top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]
        
#         dot_content = ["digraph G {", '  rankdir=LR;']
#         structure = {}
#         for file_path, modules in connections_by_module.items():
#             structure[file_path] = []
#             for module in modules:
#                 module_name = module["name"]
#                 structure[file_path].append(module_name)
#                 dot_content.append(f'  "{module_name}";')
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if module_name != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                         dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
#         dot_content.append("}")
#         with open("hierarchy.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info("Generated hierarchy.dot")
#         log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
#         if not instantiated_modules:
#             logging.warning("No instantiated modules detected, hierarchy may be incomplete.")
        
#         return {
#             "top_level_modules": top_level_modules,
#             "structure": structure
#         }
#     except Exception as e:
#         logging.error(f"Error generating hierarchy: {e}")
#         return {"top_level_modules": [], "structure": {}}







# import logging
# import re
# import os

# def setup_logging(verbosity):
#     try:
#         levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
#         log_level = levels.get(verbosity, logging.INFO)
        
#         # Ensure outputs directory exists
#         os.makedirs('outputs', exist_ok=True)
#         logging.debug(f"Created outputs directory: outputs")
        
#         # Create a formatter
#         formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
#         # Create file handler
#         file_handler = logging.FileHandler('outputs/debug.log', mode='w')  # Overwrite mode
#         file_handler.setFormatter(formatter)
#         file_handler.setLevel(log_level)
        
#         # Create console handler
#         console_handler = logging.StreamHandler()
#         console_handler.setFormatter(formatter)
#         console_handler.setLevel(log_level)
        
#         # Configure root logger
#         logging.getLogger('').setLevel(log_level)
#         logging.getLogger('').handlers = []  # Clear existing handlers
#         logging.getLogger('').addHandler(file_handler)
#         logging.getLogger('').addHandler(console_handler)
        
#         # Test logging
#         logging.debug("Logging initialized with DEBUG level")
#         logging.info("Logging initialized with INFO level")
#         logging.error("Logging initialized with ERROR level")
        
#         # Force flush to ensure logs are written
#         file_handler.flush()
#     except Exception as e:
#         print(f"Error setting up logging: {e}")
#         raise

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if line.startswith('`define'):
#                     match = re.match(r'`define\s+(\w+)\s+(.+)', line)
#                     if match:
#                         macro_name, macro_value = match.groups()
#                         macros[macro_name] = macro_value.strip()
#                         logging.debug(f"Extracted macro: `{macro_name}` = {macro_value}")
#         logging.debug(f"Extracted {len(macros)} macros from {file_path}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return macros

# def detect_counter(text):
#     try:
#         return bool(re.search(r'\w+\s*\+=\s*\d+|\w+\s*=\s*\w+\s*\+\s*\d+', text))
#     except Exception as e:
#         logging.error(f"Error detecting counter: {e}")
#         return False

# def log_section(title, messages, detailed_output=None):
#     try:
#         logging.info(f"\n=== {title} ===")
#         if detailed_output is not None:
#             detailed_output.append(f"\n=== {title} ===")
#         for msg in messages:
#             logging.info(msg)
#             if detailed_output is not None:
#                 detailed_output.append(msg)
#         # Flush logs
#         for handler in logging.getLogger('').handlers:
#             handler.flush()
#     except Exception as e:
#         logging.error(f"Error in log_section: {e}")

# def build_tree_string(top_level_modules, connections_by_module, module_names):
#     """
#     Build a tree-like string representation of the module hierarchy.
#     Returns a string formatted with ASCII characters (├──, │, etc.).
#     """
#     try:
#         def build_subtree(module, prefix="", is_last=True, visited=None):
#             if visited is None:
#                 visited = set()
#             lines = []
#             if module in visited:
#                 lines.append(f"{prefix}{'└──' if is_last else '├──'} {module} (cyclic)")
#                 return lines
#             visited.add(module)
#             lines.append(f"{prefix}{'└──' if is_last else '├──'} {module}")
            
#             # Find children (modules instantiated by this module)
#             children = []
#             for file_path, modules in connections_by_module.items():
#                 for mod in modules:
#                     if mod["name"] == module:
#                         for inst_name, inst in mod["connections"]["instances"].items():
#                             if inst["module"] in module_names and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                                 children.append((inst["module"], inst_name))
            
#             # Sort children for consistent output
#             children.sort(key=lambda x: x[0] + x[1])  # Sort by module name and instance name
            
#             for i, (child, inst_name) in enumerate(children):
#                 is_last_child = i == len(children) - 1
#                 child_prefix = prefix + ("    " if is_last else "│   ")
#                 lines.extend(build_subtree(child, child_prefix, is_last_child, visited.copy()))
            
#             return lines

#         tree_lines = []
#         for module in sorted(top_level_modules):
#             tree_lines.extend(build_subtree(module, visited=set()))
#         return "\n".join(tree_lines)
#     except Exception as e:
#         logging.error(f"Error building tree string: {e}")
#         return ""

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     try:
#         # Identify instantiated modules
#         instantiated_modules = set()
#         for file_path, modules in connections_by_module.items():
#             for module in modules:
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if inst["module"] in {m["name"] for m in all_modules} and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                         instantiated_modules.add(inst["module"])
#                         logging.debug(f"Found instantiated module: {inst['module']} by {module['name']} [label=\"{inst_name}\"]")
        
#         # Top-level modules are those not instantiated by any other module
#         top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]
#         logging.debug(f"Top-level modules: {top_level_modules}")
        
#         dot_content = ["digraph G {", '  rankdir=LR;']
#         structure = {}
#         for file_path, modules in connections_by_module.items():
#             structure[file_path] = []
#             for module in modules:
#                 module_name = module["name"]
#                 structure[file_path].append(module_name)
#                 dot_content.append(f'  "{module_name}";')
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if inst["module"] in {m["name"] for m in all_modules} and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                         dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
#                         logging.debug(f"Added edge: {module_name} -> {inst['module']} [label=\"{inst_name}\"]")
        
#         dot_content.append("}")
        
#         # Log DOT content
#         logging.debug("Hierarchy DOT content:\n%s", "\n".join(dot_content))
        
#         # Generate and log tree-like hierarchy
#         module_names = {m["name"] for m in all_modules}
#         tree_string = build_tree_string(top_level_modules, connections_by_module, module_names)
#         logging.info("Module Hierarchy Tree:\n%s", tree_string)
        
#         with open("outputs/hierarchy.dot", "w") as f:
#             f.write("\n".join(dot_content))
#         logging.info("Generated hierarchy.dot")
#         log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
#         if not instantiated_modules:
#             logging.warning("No instantiated modules detected, hierarchy may be incomplete.")
        
#         # Flush logs
#         for handler in logging.getLogger('').handlers:
#             handler.flush()
        
#         return {
#             "top_level_modules": top_level_modules,
#             "structure": structure
#         }
#     except Exception as e:
#         logging.error(f"Error generating hierarchy: {e}")
#         return {"top_level_modules": [], "structure": {}}








# # updated1
# # identifies counters, registers, muxes, and gates in both .v files (Verilog/SystemVerilog files) and .lib files (library files)


# import logging
# import re
# import os


# def setup_logging(verbosity):
#     levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
#     try:
#         os.makedirs("generated_op_files", exist_ok=True)
#         # Clear any existing handlers to avoid conflicts
#         logging.getLogger('').handlers = []
#         # Configure logging
#         logger = logging.getLogger('')
#         logger.setLevel(levels.get(verbosity, logging.INFO))
#         # File handler
#         file_handler = logging.FileHandler(os.path.join("generated_op_files", "debug.log"), mode='w')
#         file_handler.setLevel(levels.get(verbosity, logging.INFO))
#         file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#         logger.addHandler(file_handler)
#         # Stream handler
#         stream_handler = logging.StreamHandler()
#         stream_handler.setLevel(levels.get(verbosity, logging.INFO))
#         stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#         logger.addHandler(stream_handler)
#         # Test log to verify setup
#         logging.debug("Logging initialized for verbosity level %s", verbosity)
#     except Exception as e:
#             print(f"Error setting up logging: {e}")
#             raise

# # def setup_logging(verbosity):
# #     levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
# #     # # Create generated_op_files folder if not exists
# #     os.makedirs("generated_op_files", exist_ok=True)
# #     logging.basicConfig(
# #         level=levels.get(verbosity, logging.INFO),
# #         format='%(asctime)s - %(levelname)s - %(message)s',
# #         handlers=[
# #             logging.FileHandler(os.path.join("generated_op_files", "debug.log")),
# #             # logging.FileHandler('debug.log'),
# #             logging.StreamHandler()
# #         ]
# #     )

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if line.startswith('`define'):
#                     match = re.match(r'`define\s+(\w+)\s+(.+)', line)
#                     if match:
#                         macro_name, macro_value = match.groups()
#                         macros[macro_name] = macro_value.strip()
#                         logging.debug(f"Extracted macro: `{macro_name}` = {macro_value}")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return macros

# def detect_counter(text):
#     return bool(re.search(r'\w+\s*\+=\s*\d+|\w+\s*=\s*\w+\s*\+\s*\d+', text))

# def log_section(title, messages, detailed_output=None):
#     logging.info(f"\n=== {title} ===")
#     if detailed_output is not None:
#         detailed_output.append(f"\n=== {title} ===")
#     for msg in messages:
#         logging.info(msg)
#         if detailed_output is not None:
#             detailed_output.append(msg)

# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     try:
#         instantiated_modules = set()
#         for file_path, modules in connections_by_module.items():
#             for module in modules:
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if module["name"] != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                         instantiated_modules.add(inst["module"])
#                     else:
#                         logging.debug(f"Filtered invalid edge: {module['name']} -> {inst['module']} [label=\"{inst_name}\"]")
#         top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]
        
#         dot_content = ["digraph G {", '  rankdir=LR;']
#         structure = {}
#         for file_path, modules in connections_by_module.items():
#             structure[file_path] = []
#             for module in modules:
#                 module_name = module["name"]
#                 structure[file_path].append(module_name)
#                 dot_content.append(f'  "{module_name}";')
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if module_name != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                         dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
#         dot_content.append("}")
#         os.makedirs("generated_op_files", exist_ok=True)
#         with open(os.path.join("generated_op_files", "hierarchy.dot"), "w") as f:
#             f.write("\n".join(dot_content))
#         # with open("hierarchy.dot", "w") as f:
#         #     f.write("\n".join(dot_content))
#         logging.debug("Hierarchy DOT content:\n%s", "\n".join(dot_content))  # Log DOT content
#         logging.info("Generated hierarchy.dot")
#         log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
#         if not instantiated_modules:
#             logging.warning("No instantiated modules detected, hierarchy may be incomplete.")
        
#         return {
#             "top_level_modules": top_level_modules,
#             "structure": structure
#         }
#     except Exception as e:
#         logging.error(f"Error generating hierarchy: {e}")
#         return {"top_level_modules": [], "structure": {}}









# updated2

# before adding new commands


# utility.py
# import logging
# import re
# import os

# def setup_logging(verbosity):
#     levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
#     try:
#         os.makedirs("generated_op_files", exist_ok=True)
#         logging.getLogger('').handlers = []
#         logger = logging.getLogger('')
#         logger.setLevel(levels.get(verbosity, logging.INFO))
#         file_handler = logging.FileHandler(os.path.join("generated_op_files", "debug.log"), mode='w')
#         file_handler.setLevel(levels.get(verbosity, logging.INFO))
#         file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
#         logger.addHandler(file_handler)
#         if verbosity > 0:  # Only add stream handler for INFO or DEBUG
#             stream_handler = logging.StreamHandler()
#             stream_handler.setLevel(levels.get(verbosity, logging.INFO))
#             stream_handler.setFormatter(logging.Formatter('%(message)s'))  # Simplified console output
#             logger.addHandler(stream_handler)
#         logging.debug("Logging initialized for verbosity level %s", verbosity)
#     except Exception as e:
#         print(f"Error setting up logging: {e}")
#         raise

# def extract_macros(file_path):
#     macros = {}
#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if line.startswith('`define'):
#                     match = re.match(r'`define\s+(\w+)\s+(.+)', line)
#                     if match:
#                         macro_name, macro_value = match.groups()
#                         macros[macro_name] = macro_value.strip()
#                         logging.debug(f"Extracted macro: `{macro_name}` = {macro_value}")
#         return macros
#     except FileNotFoundError:
#         logging.error(f"File {file_path} not found")
#         return macros
#     except Exception as e:
#         logging.error(f"Error extracting macros from {file_path}: {e}")
#         return macros

# def detect_counter(text):
#     return bool(re.search(r'\w+\s*\+=\s*\d+|\w+\s*=\s*\w+\s*\+\s*\d+', text))

# def log_section(title, messages, detailed_output=None):
#     logging.info(f"\n=== {title} ===")
#     if detailed_output is not None:
#         detailed_output.append(f"\n=== {title} ===")
#     for msg in messages:
#         logging.info(msg)
#         if detailed_output is not None:
#             detailed_output.append(msg)

# # def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
# #     try:
# #         instantiated_modules = set()
# #         for file_path, modules in connections_by_module.items():
# #             for module in modules:
# #                 for inst_name, inst in module["connections"]["instances"].items():
# #                     if module["name"] != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
# #                         instantiated_modules.add(inst["module"])
        
# #         top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]
        
# #         dot_content = ["digraph G {", '  rankdir=LR;']
# #         structure = {}
# #         for file_path, modules in connections_by_module.items():
# #             structure[file_path] = []
# #             for module in modules:
# #                 module_name = module["name"]
# #                 structure[file_path].append(module_name)
# #                 dot_content.append(f'  "{module_name}";')
# #                 for inst_name, inst in module["connections"]["instances"].items():
# #                     if module_name != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
# #                         dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
# #         dot_content.append("}")
        
# #         os.makedirs("generated_op_files", exist_ok=True)
# #         output_dot_path = os.path.join("generated_op_files", "hierarchy.dot")
# #         try:
# #             with open(output_dot_path, "w") as f:
# #                 f.write("\n".join(dot_content))
# #             logging.info(f"Generated {output_dot_path}")
# #         except Exception as e:
# #             logging.error(f"Error writing to {output_dot_path}: {e}")
        
# #         log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
# #         if not instantiated_modules:
# #             logging.warning("No instantiated modules detected, hierarchy may be incomplete.")
        
# #         return {
# #             "top_level_modules": top_level_modules,
# #             "structure": structure
# #         }
# #     except Exception as e:
# #         logging.error(f"Error generating hierarchy: {e}")
# #         return {"top_level_modules": [], "structure": {}}




# def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
#     try:
#         # Step 1: Collect all instantiated modules
#         instantiated_modules = set()
#         for file_path, modules in connections_by_module.items():
#             for module in modules:
#                 for inst_name, inst in module["connections"]["instances"].items():
#                     if module["name"] != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                         instantiated_modules.add(inst["module"])

#         # Step 2: Identify top-level modules
#         top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]

#         # Step 3: DOT graph setup
#         dot_content = ["digraph G {", '  rankdir=LR;']


#         def build_hierarchy(module_name, connections_by_module, visited=None):
#             if visited is None:
#                 visited = set()
#             if module_name in visited:
#                 # Prevent infinite recursion
#                 return {}

#             visited.add(module_name)
#             hierarchy = {}

#             # Find the module object from connections_by_module
#             for file_path, modules in connections_by_module.items():
#                 for module in modules:
#                     if module["name"] == module_name:
#                         for inst_name, inst in module["connections"]["instances"].items():
#                             if inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
#                                 # Add DOT edge
#                                 dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
#                                 # Recursively build child hierarchy
#                                 hierarchy[inst_name] = {
#                                     "module": inst["module"],
#                                     "instances": build_hierarchy(inst["module"], connections_by_module, visited.copy())
#                                 }
#                         return hierarchy
#             return {}


#         # Step 4: Build nested structure starting from top modules
#         structure = {}
#         for top in top_level_modules:
#             dot_content.append(f'  "{top}";')
#             structure[top] = {
#                 "module": top,
#                 "instances": build_hierarchy(top, connections_by_module)
#             }

#         dot_content.append("}")

#         # Step 5: Save DOT file
#         os.makedirs("generated_op_files", exist_ok=True)
#         output_dot_path = os.path.join("generated_op_files", "hierarchy.dot")
#         try:
#             with open(output_dot_path, "w") as f:
#                 f.write("\n".join(dot_content))
#             logging.info(f"Generated {output_dot_path}")
#         except Exception as e:
#             logging.error(f"Error writing to {output_dot_path}: {e}")

#         # Step 6: Log and return
#         log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
#         if not instantiated_modules:
#             logging.warning("No instantiated modules detected, hierarchy may be incomplete.")

#         return {
#             "top_level_modules": top_level_modules,
#             "structure": structure  # Now nested
#         }

#     except Exception as e:
#         logging.error(f"Error generating hierarchy: {e}")
#         return {"top_level_modules": [], "structure": {}}




# after adding new commands



import logging
import re
import os

class LimitedLinesHandler(logging.FileHandler):
    def __init__(self, filename, max_lines):
        super().__init__(filename, mode='w')
        self.max_lines = max_lines
        self.line_count = 0

    def emit(self, record):
        if self.line_count < self.max_lines:
            super().emit(record)
            self.line_count += 1
        else:
            self.close()

def setup_logging(verbosity, max_lines=None, filter_level=None):
    levels = {0: logging.ERROR, 1: logging.INFO, 2: logging.DEBUG}
    try:
        os.makedirs("generated_op_files", exist_ok=True)
        logging.getLogger('').handlers = []
        logger = logging.getLogger('')
        logger.setLevel(levels.get(verbosity, logging.INFO))
        
        # Use LimitedLinesHandler if max_lines is specified
        if max_lines:
            file_handler = LimitedLinesHandler(os.path.join("generated_op_files", "debug.log"), max_lines)
        else:
            file_handler = logging.FileHandler(os.path.join("generated_op_files", "debug.log"), mode='w')
        
        file_handler.setLevel(levels.get(verbosity, logging.INFO))
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Apply level filter if specified
        if filter_level:
            file_handler.addFilter(lambda record: record.levelname == filter_level)
        
        logger.addHandler(file_handler)
        
        # Add stream handler for console output if verbosity > 0
        if verbosity > 0:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(levels.get(verbosity, logging.INFO))
            stream_handler.setFormatter(logging.Formatter('%(message)s'))
            if filter_level:
                stream_handler.addFilter(lambda record: record.levelname == filter_level)
            logger.addHandler(stream_handler)
        
        logging.debug("Logging initialized for verbosity level %s", verbosity)
    except Exception as e:
        print(f"Error setting up logging: {e}")
        raise

def extract_macros(file_path):
    macros = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('`define'):
                    match = re.match(r'`define\s+(\w+)\s+(.+)', line)
                    if match:
                        macro_name, macro_value = match.groups()
                        macros[macro_name] = macro_value.strip()
                        logging.debug(f"Extracted macro: `{macro_name}` = {macro_value}")
        return macros
    except FileNotFoundError:
        logging.error(f"File {file_path} not found")
        return macros
    except Exception as e:
        logging.error(f"Error extracting macros from {file_path}: {e}")
        return macros

def detect_counter(text):
    return bool(re.search(r'\w+\s*\+=\s*\d+|\w+\s*=\s*\w+\s*\+\s*\d+', text))

def log_section(title, messages, detailed_output=None):
    logging.info(f"\n=== {title} ===")
    if detailed_output is not None:
        detailed_output.append(f"\n=== {title} ===")
    for msg in messages:
        logging.info(msg)
        if detailed_output is not None:
            detailed_output.append(msg)

def generate_hierarchy_dot(all_modules, connections_by_module, detailed_output):
    try:
        # Step 1: Collect all instantiated modules
        instantiated_modules = set()
        for file_path, modules in connections_by_module.items():
            for module in modules:
                for inst_name, inst in module["connections"]["instances"].items():
                    if module["name"] != inst["module"] and inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
                        instantiated_modules.add(inst["module"])

        # Step 2: Identify top-level modules
        top_level_modules = [m["name"] for m in all_modules if m["name"] not in instantiated_modules]

        # Step 3: DOT graph setup
        dot_content = ["digraph G {", '  rankdir=LR;']

        def build_hierarchy(module_name, connections_by_module, visited=None):
            if visited is None:
                visited = set()
            if module_name in visited:
                # Prevent infinite recursion
                return {}

            visited.add(module_name)
            hierarchy = {}

            # Find the module object from connections_by_module
            for file_path, modules in connections_by_module.items():
                for module in modules:
                    if module["name"] == module_name:
                        for inst_name, inst in module["connections"]["instances"].items():
                            if inst["module"] not in {'unknown', 'module', 'begin', 'generate', 'case', 'if'}:
                                # Add DOT edge
                                dot_content.append(f'  "{module_name}" -> "{inst["module"]}" [label="{inst_name}"];')
                                # Recursively build child hierarchy
                                hierarchy[inst_name] = {
                                    "module": inst["module"],
                                    "instances": build_hierarchy(inst["module"], connections_by_module, visited.copy())
                                }
                        return hierarchy
            return {}

        # Step 4: Build nested structure starting from top modules
        structure = {}
        for top in top_level_modules:
            dot_content.append(f'  "{top}";')
            structure[top] = {
                "module": top,
                "instances": build_hierarchy(top, connections_by_module)
            }

        dot_content.append("}")

        # Step 5: Save DOT file
        os.makedirs("generated_op_files", exist_ok=True)
        output_dot_path = os.path.join("generated_op_files", "hierarchy.dot")
        try:
            with open(output_dot_path, "w") as f:
                f.write("\n".join(dot_content))
            logging.info(f"Generated {output_dot_path}")
        except Exception as e:
            logging.error(f"Error writing to {output_dot_path}: {e}")

        # Step 6: Log and return
        log_section("Hierarchy Output", [f"Top-level modules: {', '.join(top_level_modules)}"], detailed_output)
        if not instantiated_modules:
            logging.warning("No instantiated modules detected, hierarchy may be incomplete.")

        return {
            "top_level_modules": top_level_modules,
            "structure": structure  # Now nested
        }

    except Exception as e:
        logging.error(f"Error generating hierarchy: {e}")
        return {"top_level_modules": [], "structure": {}}