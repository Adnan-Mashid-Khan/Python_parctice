#!/usr/bin/env python

import sys
from datetime import datetime

def get_data(filename):
    try:
        with open(filename, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"{filename} NOT FOUND")
        return []
    
def parse_data(line):
    parts = line.split()
    if len(parts) < 2:
        return None
        
    try:
        log_type = parts[0].lower()
    except IndexError:
        return None
    
    try:
        log_data = int(parts[1])
    except ValueError:
        return None
        
    log_msg = " ".join(parts[2:])
    
    return log_type, log_data, log_msg

def write_report(writer, info, error, limit, elimit, now):
    writer(f"---Parsed Logs---\n")
    
    writer(f"Run Time: {now.strftime("%Y-%m-%d %H:%M:%S")}\n")
    
    writer(f"INFO (<{limit}): {len(info)}")
    for i, msg in info:
        writer(f"{i} - {msg}\n")
        
    writer(f"ERROR (>={elimit}): {len(error)}")
    for e, msg in error:
        writer(f"{e} - {msg}\n")
        
def main():
    if len(sys.argv) < 5:
        print("USAGE: python log_parser.py <text_file.txt> <info_limit> <error_min> <output_type>")
        return
    
    try:
        limit = int(sys.argv[2])
    except ValueError:
        print("Invalid input given, using default value 300")
        limit = 300
    try:
        elimit = int(sys.argv[3])
    except ValueError:
        print("Invalid input given, using default value 400")
        elimit = 400

    output = sys.argv[4].lower()
    if output not in ["file", "print", "both"]:
        print("Invalid iput, using default 'file'")
        output = "file"
        
    filename = sys.argv[1]
    data1 = get_data(filename)

    info = []
    error = []
    now = datetime.now()

    for line in data1:
        result = parse_data(line)
        if result is None:
            continue
        log_type, log_data, log_msg = result
        
        if log_type == "info" and log_data < limit:
            info.append((log_data, log_msg))
        elif log_type == "error" and log_data >= elimit:
            error.append((log_data, log_msg))

    if output in ["print", "both"]:
        write_report(print, info, error, limit, elimit, now)

    if output in ["file", "both"]:
        with open("log_parsed.txt", "w") as f:
            write_report(lambda x: f.write(x + "\n"), info, error, limit, elimit, now)

main()

