#!/usr/bin/env bash
# arcas_parser - Bash wrapper for Arcas Parser

# Paths
BASE_DIR="$(pwd)"                 # Use current directory
LOG_FILE="$BASE_DIR/generated_op_files/debug.log"  # Log file path

# Show help message
help() {
    echo "Usage: ./arcas.sh <command> [options]"
    echo "Commands:"
    echo "  help                Show this help"
    echo "  check <path>        Check environment (Graphviz for visualize) and path"
    echo "  parse <path> [-v 0|1|2] [-l lib_file]  Run analyzer"
    echo "  visualize           Generate hierarchy.png from hierarchy.dot"
    echo "  ipxact <path> [-v 0|1|2] [-l lib_file]  Run analyzer and generate IP-XACT files"
    echo "  parse_limited <path> [-v 0|1|2] [-l lib_file] [-m lines]  Run analyzer, limit logs to specified lines"
    echo "  parse_debug <path> [-v 0|1|2] [-l lib_file]  Run analyzer, show only DEBUG logs"
    echo "  parse_error <path> [-v 0|1|2] [-l lib_file]  Run analyzer, show only ERROR logs"
    echo "  parse_info <path> [-v 0|1|2] [-l lib_file]  Run analyzer, show only INFO logs"
    echo "Options for parse, ipxact, parse_limited, parse_debug, parse_error, parse_info:"
    echo "  -v 0|1|2           Verbosity (0=errors, 1=info, 2=debug, default=1)"
    echo "  -l <lib_file>      Library file path"
    echo "  -m <lines>         Max lines for parse_limited (positive integer)"
    echo "Examples:"
    echo "  ./arcas.sh help"
    echo "  ./arcas.sh check /mnt/d/workspace/ARCAS/SDK_Design"
    echo "  ./arcas.sh parse /mnt/d/workspace/ARCAS/SDK_Design -v 2 -l /mnt/d/workspace/ARCAS/SDK_Design/SDK_Tech_cells.lib"
    echo "  ./arcas.sh visualize"
    echo "  ./arcas.sh ipxact /mnt/d/workspace/ARCAS/SDK_Design -v 2 -l /mnt/d/workspace/ARCAS/SDK_Design/SDK_Tech_cells.lib"
    echo "  ./arcas.sh parse_limited /mnt/d/workspace/ARCAS/SDK_Design -v 2 -l /mnt/d/workspace/ARCAS/SDK_Design/SDK_Tech_cells.lib -m 50"
    echo "  ./arcas.sh parse_debug /mnt/d/workspace/ARCAS/SDK_Design -v 2 -l /mnt/d/workspace/ARCAS/SDK_Design/SDK_Tech_cells.lib"
    echo "  ./arcas.sh parse_error /mnt/d/workspace/ARCAS/SDK_Design -v 2 -l /mnt/d/workspace/ARCAS/SDK_Design/SDK_Tech_cells.lib"
    echo "  ./arcas.sh parse_info /mnt/d/workspace/ARCAS/SDK_Design -v 2 -l /mnt/d/workspace/ARCAS/SDK_Design/SDK_Tech_cells.lib"
    exit 0
}

check() {
    local path="$1"
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    command -v python3 >/dev/null || { echo "Error: Python3 not found. Install Python3."; exit 1; }
    python3 -c "import pyslang" 2>/dev/null || { echo "Error: pyslang not installed. Run: pip install pyslang"; exit 1; }
    python3 -c "import psutil" 2>/dev/null || { echo "Error: psutil not installed. Run: pip install psutil"; exit 1; }
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh check <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    if command -v dot >/dev/null; then
        echo "Graphviz (dot) is installed (required for visualize command)"
    else
        echo "Warning: Graphviz (dot) not installed. Install it for visualize command with: sudo apt-get install graphviz (Ubuntu) or brew install graphviz (macOS)"
    fi
    echo "Check passed: Arcas package, Python, pyslang, psutil, and path $path are ready"
}

# # Check environment and path
# check() {
#     local path="$1"
#     command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
#     command -v python3 >/dev/null || { echo "Error: Python3 not found. Install Python3."; exit 1; }
#     python3 -c "import pyslang" 2>/dev/null || { echo "Error: pyslang not installed. Run: pip install pyslang"; exit 1; }
#     python3 -c "import psutil" 2>/dev/null || { echo "Error: psutil not installed. Run: pip install psutil"; exit 1; }
#     [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh check <path>"; exit 1; }
#     [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
#     if command -v dot >/dev/null; then
#         echo "Graphviz (dot) is installed (required for visualize command)"
#     else
#         echo "Warning: Graphviz (dot) not installed. Install it for visualize command with: sudo apt-get install graphviz (Ubuntu) or brew install graphviz (macOS)"
#     fi
#     echo "Check passed: Arcas package, Python, pyslang, psutil, and path $path are ready"
# }

# Run the analyzer
parse() {
    local path="$1"
    shift
    local verbosity=1
    local lib_file=""
    while getopts "v:l:" opt; do
        case $opt in
            v) verbosity="$OPTARG"
               [[ "$verbosity" =~ ^[0-2]$ ]] || { echo "Error: Verbosity must be 0, 1, or 2"; exit 1; }
               ;;
            l) lib_file="$OPTARG"
               [ ! -f "$lib_file" ] && { echo "Error: Library file $lib_file not found"; exit 1; }
               ;;
            *) echo "Error: Invalid option. Use: ./arcas.sh parse <path> [-v 0|1|2] [-l lib_file]"; exit 1 ;;
        esac
    done
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh parse <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    cmd="arcas \"$path\" -v $verbosity"
    [ -n "$lib_file" ] && cmd="$cmd -l \"$lib_file\""
    echo "Running: $cmd"
    eval $cmd || { echo "Error: Analysis failed. See $LOG_FILE"; exit 1; }
    echo "Done! Output in $LOG_FILE, hierarchy in generated_op_files/hierarchy.dot, generated_op_files/output.json"
}

# Visualize hierarchy.dot as PNG
visualize() {
    if ! command -v dot &> /dev/null; then
        echo "Error: Graphviz (dot) not installed. Install it with: sudo apt-get install graphviz (Ubuntu) or brew install graphviz (macOS)."
        exit 1
    fi
    if [ ! -f "generated_op_files/hierarchy.dot" ]; then
        echo "Error: generated_op_files/hierarchy.dot not found. Run parse command first."
        exit 1
    fi
    dot -Tpng generated_op_files/hierarchy.dot -o generated_op_files/hierarchy.png || { echo "Error: Failed to generate hierarchy.png"; exit 1; }
    echo "Generated hierarchy.png in generated_op_files/"
}

# Run the analyzer and generate IP-XACT files
ipxact() {
    local path="$1"
    shift
    local verbosity=1
    local lib_file=""
    while getopts "v:l:" opt; do
        case $opt in
            v) verbosity="$OPTARG"
               [[ "$verbosity" =~ ^[0-2]$ ]] || { echo "Error: Verbosity must be 0, 1, or 2"; exit 1; }
               ;;
            l) lib_file="$OPTARG"
               [ ! -f "$lib_file" ] && { echo "Error: Library file $lib_file not found"; exit 1; }
               ;;
            *) echo "Error: Invalid option. Use: ./arcas.sh ipxact <path> [-v 0|1|2] [-l lib_file]"; exit 1 ;;
        esac
    done
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh ipxact <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    cmd="arcas \"$path\" -v $verbosity --ipxact"
    [ -n "$lib_file" ] && cmd="$cmd -l \"$lib_file\""
    echo "Running: $cmd"
    eval $cmd || { echo "Error: Analysis failed. See $LOG_FILE"; exit 1; }
    echo "Done! Output in $LOG_FILE, hierarchy in generated_op_files/hierarchy.dot, IP-XACT files in ipxact_output/"
}

# Run the analyzer, limit logs to specified lines
parse_limited() {
    local path="$1"
    shift
    local verbosity=1
    local lib_file=""
    local max_lines=30  # Default to 30 lines
    while getopts "v:l:m:" opt; do
        case $opt in
            v) verbosity="$OPTARG"
               [[ "$verbosity" =~ ^[0-2]$ ]] || { echo "Error: Verbosity must be 0, 1, or 2"; exit 1; }
               ;;
            l) lib_file="$OPTARG"
               [ ! -f "$lib_file" ] && { echo "Error: Library file $lib_file not found"; exit 1; }
               ;;
            m) max_lines="$OPTARG"
               [[ "$max_lines" =~ ^[1-9][0-9]*$ ]] || { echo "Error: Max lines must be a positive integer"; exit 1; }
               ;;
            *) echo "Error: Invalid option. Use: ./arcas.sh parse_limited <path> [-v 0|1|2] [-l lib_file] [-m lines]"; exit 1 ;;
        esac
    done
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh parse_limited <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    cmd="arcas \"$path\" -v $verbosity --max_lines $max_lines"
    [ -n "$lib_file" ] && cmd="$cmd -l \"$lib_file\""
    echo "Running: $cmd"
    eval $cmd || { echo "Error: Analysis failed. See $LOG_FILE"; exit 1; }
    echo "Done! Output in $LOG_FILE (limited to $max_lines lines), hierarchy in generated_op_files/hierarchy.dot, generated_op_files/output.json"
}

# Run the analyzer, show only DEBUG logs
parse_debug() {
    local path="$1"
    shift
    local verbosity=1
    local lib_file=""
    while getopts "v:l:" opt; do
        case $opt in
            v) verbosity="$OPTARG"
               [[ "$verbosity" =~ ^[0-2]$ ]] || { echo "Error: Verbosity must be 0, 1, or 2"; exit 1; }
               ;;
            l) lib_file="$OPTARG"
               [ ! -f "$lib_file" ] && { echo "Error: Library file $lib_file not found"; exit 1; }
               ;;
            *) echo "Error: Invalid option. Use: ./arcas.sh parse_debug <path> [-v 0|1|2] [-l lib_file]"; exit 1 ;;
        esac
    done
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh parse_debug <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    cmd="arcas \"$path\" -v $verbosity --filter_level DEBUG"
    [ -n "$lib_file" ] && cmd="$cmd -l \"$lib_file\""
    echo "Running: $cmd"
    eval $cmd || { echo "Error: Analysis failed. See $LOG_FILE"; exit 1; }
    echo "Done! Output in $LOG_FILE (DEBUG only), hierarchy in generated_op_files/hierarchy.dot, generated_op_files/output.json"
}

# Run the analyzer, show only ERROR logs
parse_error() {
    local path="$1"
    shift
    local verbosity=1
    local lib_file=""
    while getopts "v:l:" opt; do
        case $opt in
            v) verbosity="$OPTARG"
               [[ "$verbosity" =~ ^[0-2]$ ]] || { echo "Error: Verbosity must be 0, 1, or 2"; exit 1; }
               ;;
            l) lib_file="$OPTARG"
               [ ! -f "$lib_file" ] && { echo "Error: Library file $lib_file not found"; exit 1; }
               ;;
            *) echo "Error: Invalid option. Use: ./arcas.sh parse_error <path> [-v 0|1|2] [-l lib_file]"; exit 1 ;;
        esac
    done
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh parse_error <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    cmd="arcas \"$path\" -v $verbosity --filter_level ERROR"
    [ -n "$lib_file" ] && cmd="$cmd -l \"$lib_file\""
    echo "Running: $cmd"
    eval $cmd || { echo "Error: Analysis failed. See $LOG_FILE"; exit 1; }
    echo "Done! Output in $LOG_FILE (ERROR only), hierarchy in generated_op_files/hierarchy.dot, generated_op_files/output.json"
}

# Run the analyzer, show only INFO logs
parse_info() {
    local path="$1"
    shift
    local verbosity=1
    local lib_file=""
    while getopts "v:l:" opt; do
        case $opt in
            v) verbosity="$OPTARG"
               [[ "$verbosity" =~ ^[0-2]$ ]] || { echo "Error: Verbosity must be 0, 1, or 2"; exit 1; }
               ;;
            l) lib_file="$OPTARG"
               [ ! -f "$lib_file" ] && { echo "Error: Library file $lib_file not found"; exit 1; }
               ;;
            *) echo "Error: Invalid option. Use: ./arcas.sh parse_info <path> [-v 0|1|2] [-l lib_file]"; exit 1 ;;
        esac
    done
    [ -z "$path" ] && { echo "Error: No path provided. Use: ./arcas.sh parse_info <path>"; exit 1; }
    [ ! -e "$path" ] && { echo "Error: Path $path does not exist"; exit 1; }
    command -v arcas >/dev/null || { echo "Error: Arcas package not installed. Install it with: pip install arcas-1.0.0-py3-none-any.whl"; exit 1; }
    cmd="arcas \"$path\" -v $verbosity --filter_level INFO"
    [ -n "$lib_file" ] && cmd="$cmd -l \"$lib_file\""
    echo "Running: $cmd"
    eval $cmd || { echo "Error: Analysis failed. See $LOG_FILE"; exit 1; }
    echo "Done! Output in $LOG_FILE (INFO only), hierarchy in generated_op_files/hierarchy.dot, generated_op_files/output.json"
}

# Handle commands
case "$1" in
    help) help ;;
    check) shift; check "$1" ;;
    parse) shift; parse "$@" ;;
    visualize) visualize ;;
    ipxact) shift; ipxact "$@" ;;
    parse_limited) shift; parse_limited "$@" ;;
    parse_debug) shift; parse_debug "$@" ;;
    parse_error) shift; parse_error "$@" ;;
    parse_info) shift; parse_info "$@" ;;
    *) echo "Error: Unknown command: $1. Use: ./arcas.sh help"; exit 1 ;;
esac