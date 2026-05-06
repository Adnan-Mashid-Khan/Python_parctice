#!/usr/bin/env python

def get_data():
    with open("data.txt", "r") as f:
        return f.readlines()

def parse_data(line):
    parts = line.split()
    log_type = parts[0]
    log_imp = parts[1]
    log_msg = "".join(parts[2: ])

    return log_type, log_imp, log_msg

def main():
    lines = get_data()
    info = []
    error = []
    
    for line in lines:
        data = parse_data(line)
        log_type, log_imp, log_msg = data

        if "info" == log_type.lower():
            info.append((log_type, log_imp, log_msg))
        elif "error" == log_type.lower():
            error.append((log_type, log_imp, log_msg))

    print(f"info logs:{len(info)}\n")
    print(f"{info}")
    print(f"error logs:{len(error)}\n")
    print(f"{error}")

main()
