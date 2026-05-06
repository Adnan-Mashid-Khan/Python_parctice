#!/usr/bin/env python

import sys

def get_data(filename):
    try:
        with open(filename, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print("File Not Found")
    
def parse_data(line):
    parts = line.split()
    log_type = parts[0]
    log_imp = parts[1]
    log_msg = "".join(parts[2: ])

    return log_type, log_imp, log_msg

def main():

    if len(sys.argv) < 2:
        print("Incorrect argument passed")
        print("eg. python log.py <data.txt> <info_limit> <error_minimum> <print/file/both>")
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
    
    lines = get_data(filename)
    info = []
    error = []
    
    for line in lines:
        data = parse_data(line)
        log_type, log_imp, log_msg = data

        if "info" == log_type.lower() and  info_limit > int(log_imp):
            info.append((log_type, log_imp, log_msg))

        elif "error" == log_type.lower() and error_minimum < int(log_imp):
            error.append((log_type, log_imp, log_msg))

    if output in ["print", "both"]:
        print(f"\ninfo logs <{info_limit}:{len(info)}")#info output
        for log_type, log_imp, log_msg in info:
            print(f"{log_imp} --> {log_msg}")
        
        print(f"\nerror logs >{error_minimum}:{len(error)}")#error output
        for log_type, log_imp, log_msg in error:
            print(f"{log_imp} --> {log_msg}")

    if output in ["file", "both"]:
        with open("log_test_parsed.txt", "w") as f:
            f.write(f"info logs <{info_limit}: {len(info)}")
            for log_type, log_imp, log_msg in info:
                f.write(f"\n{log_imp} --> {log_msg}")

            f.write(f"\nerror logs >{error_minimum}:{len(error)}\n")#error output
            for log_type, log_imp, log_msg in error:
                f.write(f"{log_imp} --> {log_msg}\n")
main()
