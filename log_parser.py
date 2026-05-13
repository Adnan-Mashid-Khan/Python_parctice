#!/usr/bin/env python

import sys
from datetime import datetime
now = datetime.now()

def get_data(filename):
    try:
        with open(filename, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"{filename} NOT FOUND")
        return []

def get_parts(parts, index, cast_type, default):
    try:
        return cast_type(parts[index])
    except (IndexError, ValueError):
        return default

def get_argv(index, cast_type, default):
    try:
        return cast_type(sys.argv[index])
    except (IndexError, ValueError):
        return default
        
def parse_data(line):
    parts = line.split()
    if len(parts) < 3:
        return None
        
    log_type = get_parts(parts, 0, str, "").lower()
    log_data = get_parts(parts, 1, int, 0)
    log_msg = " ".join(parts[2:])
    
    return log_type, log_data, log_msg

def process_log(lines, limit, elimit):

    comparison = {
        "info": limit,
        "error": elimit,
        }

    info = []
    error = []
    skipped = []
    
    for line in lines:
        result = parse_data(line)
        if result is None:
            skipped.append(line)
            continue
        log_type, log_data, log_msg = result

        

        if log_type not in comparison:
            skipped.append(line)
            continue

        limit = comparison[log_type]
            
        if log_type == "info" and log_data < limit:
            info.append((log_type, log_data, log_msg))
        elif log_type == "error" and log_data >= limit:
            error.append((log_type, log_data, log_msg))
        else: skipped.append(line)

    return info, error, skipped
    

def write_report(writer, info, error, skipped, limit, elimit, now):
    writer(f"---Parsed Logs---\n")
    
    writer(f"Run Time: {now.strftime("%Y-%m-%d %H:%M:%S")}\n")

    writer(f"INFO (<{limit}): {len(info)}")
    for info, i, msg in info:
        writer(f"{info} - {i} - {msg}")
        
    writer(f"\nERROR (>={elimit}): {len(error)}")
    for error, e, msg in error:
        writer(f"{error} - {e} - {msg}")

    writer(f"\nSkipped lines")
    for s in skipped:
        writer(f"{(s).strip()}")
        
def main():
    if len(sys.argv) < 2:
        print("USAGE: python log_parser.py <text_file.txt> <info_limit> <error_min> <output_type>")
        print("Example: python log_parser.py dtd.txt 1000 100 print/file/both")
        return
        
    elif len(sys.argv) < 4:
        print("values not provided, using default")
    
    limit = get_argv(2, int, 1000)
    elimit = get_argv(3, int, 100)
    output = get_argv(4, str, "print").lower()
        
    filename = sys.argv[1]
    lines = get_data(filename)

    info, error, skipped = process_log(lines, limit, elimit)
    
    if output in ["print", "both"]:
        write_report(print, info, error, skipped, limit, elimit, now)

    if output in ["file", "both"]:
        with open("log_parsed.txt", "w") as f:
            write_report(lambda x: f.write(x + "\n"), info, error, skipped, limit, elimit, now)

main()

