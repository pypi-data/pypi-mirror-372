import os
import argparse
import time
import logging
import json
from .parser import parse_module_ports,process_file, preprocess_verilog
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