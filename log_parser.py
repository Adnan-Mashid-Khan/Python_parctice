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

    rule = {
        "info": lambda log_data: log_data < limit,
        "error": lambda log_data: log_data >= elimit,
        "warning": lambda log_data: log_data < 1000,
    }

    
    logs={
        "info": [],
        "error": [],
        "warning": [],
        "skipped": [],
        "invalid": [],
    }
    
    
    for line in lines:
        result = parse_data(line)
        lane = line.split()
        if result is None and len(lane) < 3 :
            logs["invalid"].append(line)
            continue
        elif result is None: 
            logs["skipped"].append(line)
            continue
        log_type, log_data, log_msg = result

        if log_type not in logs:
            logs["skipped"].append(line)
            continue

        
            
        if rule[log_type](log_data):
            logs[log_type].append((log_type, log_data, log_msg))
        else: logs["skipped"].append(line)

    return logs
    

def write_report(writer, logs, limit, elimit, now):

    display = {
        "info": f"<{limit}",
        "error": f">={elimit}",
        "warning": "<1000"
    }
    
    writer(f"---Parsed Logs---\n")
    
    writer(f"Run Time: {now.strftime("%Y-%m-%d %H:%M:%S")}\n")

    for log_type, entries in logs.items():
        if log_type in display:
            writer(f"\n{log_type} ({display[log_type]}): {len(logs[log_type])}")
        else:
            writer(f"\n{log_type}: {len(logs[log_type])}")
        for entry in entries:
            
            if log_type in ["skipped", "invalid"]:
                writer(entry.strip())
            else: 
                a, b, c = entry
                writer(f"{a} - {b} - {c}")


def write_output(output, logs, limit, elimit, now):
    if output in ["print", "both"]:
        write_report(print, logs, limit, elimit, now)
        
    if output in ["file", "both"]:
        with open("log_parsed.txt", "w") as f:
            write_report(lambda x: f.write(x + "\n"), logs, limit, elimit, now)

        
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

    logs = process_log(lines, limit, elimit)

    write_output(output, logs, limit, elimit, now)

main()

