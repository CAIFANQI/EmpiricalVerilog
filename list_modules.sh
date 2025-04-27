#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Error: No input provided."
  echo "Usage: bash foo.sh <input>"
  exit 1
fi

# Store the input argument in a variable
directory=$1

# Check for debug flag
debug_mode=false
if [ "$2" == "--debug" ]; then
  debug_mode=true
fi

# Set repo_name and output files based on debug mode
if [ "$debug_mode" = true ]; then
  repo_name=$(basename "$directory")
  output_file="$(pwd)/data/$repo_name/module_list.csv"
  testbench_output_file="$(pwd)/data/$repo_name/testbench_list.csv"
else
  repo_name=$(echo "$directory" | awk -F'/' '{print $(NF-2)"/"$(NF-1)"/"$NF}')
  output_file="$HOME/verilog_testing/data/$repo_name/module_list.csv"
  testbench_output_file="$HOME/verilog_testing/data/$repo_name/testbench_list.csv"
fi

# Ensure output files exist
if [ ! -z "$output_file" ]; then
    mkdir -p "$(dirname "$output_file")" && touch "$output_file"
fi
> "$output_file"
if [ ! -z "$testbench_output_file" ]; then
    mkdir -p "$(dirname "$testbench_output_file")" && touch "$testbench_output_file"
fi
> "$testbench_output_file"

# Loop through all .v and .sv files in the directory
find -H "$directory" -type f \( -name "*.v" -o -name "*.sv" \) | while read -r file; do
    # echo "File: $file"

    # Skip .sv files that are not testbenches
    if [[ "$file" == *.sv ]] && ! grep -qiE '^\s*module\s+([^[:space:](]*(test|testbench|tb|_tb)[^[:space:](]*)' "$file"; then
        continue
    fi

    # Count the number of times `module` appears
    module_count=$(grep -E -o "\bmodule\b" "$file" | wc -l)
    # echo "Number of 'module' occurrences: $module_count"
    
    # Extract and print words that appear after `module`, excluding commented lines
    # echo "Words after 'module':"
    modules=$(grep -v '^\s*//' "$file" | grep -oP 'module\s+\K\w+' | tr '\n' ',')
    # echo "$modules"
    rel_file=$(realpath --relative-to="$directory" "$file")
    if [ ! -z "${modules%,}" ]; then
        echo "$rel_file,${modules%,}" >> "$output_file"
    fi
    # echo "Testbenches:"
    testbenches=$(tr [:upper:] [:lower:] < "$file" | grep -E '^\s*module\s+([^[:space:](]*(test|testbench|tb|_tb)[^[:space:](]*)' "$file" | sed -E 's/^\s*module\s+//g; s/\s*\(.*//g' | tr -d ';')
    # handles case where multiple testbench modules are found in one file
    testbenches="${testbenches//$'\n'/,}"
    # echo "$testbenches"
    if [ ! -z "$testbenches" ]; then
        # echo "$rel_file,${testbenches%,}" 
        echo "$rel_file,${testbenches%,}" >> "$testbench_output_file" 
    fi
    # echo "----------------------------------------"
done