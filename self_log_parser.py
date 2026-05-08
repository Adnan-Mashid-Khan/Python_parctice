#!/usr/bin/env python

import sys
from datetime import datetime

def get_data(filename):
    try:
        with open(filename, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print("File Not Found")
        return []
    
def parse_data(line):
    parts = line.split()

    try:
        log_type = parts[0]
    except (IndexError, ValueError):
        return None
        
    try:
        log_imp = int(parts[1])
    except (IndexError, ValueError):
        return None
        
    try:
        log_msg = " ".join(parts[2: ])
    except IndexError:
        return None

    return log_type, log_imp, log_msg

def data_writer(writer, now, info, error, skipped, info_limit, error_minimum):

    writer(f"\ninfo logs <{info_limit}:{len(info)}")#info output
    writer(f"{now}\n")
    for log_type, log_imp, log_msg in info:
        writer(f"{log_imp} --> {log_msg}")
        
    writer(f"\nerror logs >{error_minimum}:{len(error)}")#error output
    writer(f"{now}\n")
    for log_type, log_imp, log_msg in error:
        writer(f"{log_imp} --> {log_msg}")

    writer(f"\nskipped logs (all skipped logs):{len(skipped)}")
    writer(f"{now}\n")
    for a in skipped:
        writer(a.strip())

    return

def main():

    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")

    if len(sys.argv) < 2:
        print("Incorrect argument passed")
        print("eg. python log.py <data.txt> <info_limit> <error_minimum> <print/file/both> <output_file.txt")
        return None
    
    filename = sys.argv[1]

    try:
        info_limit = int(sys.argv[2])
    except IndexError:
        print("info limit not provided, using default 1000")
        info_limit = 1000
        

    try:
        error_minimum = int(sys.argv[3])
    except IndexError:
        print("minimum error not provided, using default 100")
        error_minimum = 100

    try:
        output = sys.argv[4]
    except IndexError:
        print("output type not provided, using default type print")
        output = "print"

    try:
        out_file = sys.argv[5]
    except IndexError:
        print("output file name not given, using defaut file info_error.txt")
        out_file = "info_error.txt"
    
    lines = get_data(filename)
    info = []
    error = []
    skipped = []
    
    for line in lines:
        data = parse_data(line)
        if data is None:
            skipped.append(line)
            continue
            
        log_type, log_imp, log_msg = data

        if "info" == log_type.lower() and  info_limit > log_imp:
            info.append((log_type, log_imp, log_msg))

        elif "error" == log_type.lower() and error_minimum < log_imp:
            error.append((log_type, log_imp, log_msg))
    
    if output in ["print", "both"]:
        data_writer(print, now, info, error, skipped, info_limit, error_minimum)

    if output in ["file", "both"]:
        with open(out_file, "w") as f:
            data_writer(lambda x: f.write(x + "\n"), now, info, error, skipped, info_limit, error_minimum)
            
main()
