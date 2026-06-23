#!/usr/bin/env python

import sys

from datetime import datetime
now = datetime.now()
now = now.strftime("%Y-%m-%d %H:%M:%S")

def get_data(settings):
    try:
        with open(settings["filename"], "r") as f:
            return f.readlines()
    except FileNotFoundError:
        print("File Not Found")
        return []


def get_argv(index, cast_type, default):
    try:
        return cast_type(sys.argv[index])
    except (ValueError, IndexError):
        return default

def get_parts(parts, index, cast_type, default):
    try:
        return cast_type(parts[index])
    except (ValueError, IndexError):
        return default
    
def parse_data(line):
    parts = line.split()

    log_type = get_parts(parts, 0, str, " ").lower()
    log_imp = get_parts(parts, 1, int, 0)
    log_msg = " ".join(parts[2: ])
    if log_msg == "":
        return None

    return log_type, log_imp, log_msg


def parse_log(settings):

    logs = {
        "info": [],
        "error": [],
        "skipped": []
        }

    rules = {
        "info": lambda log_imp: settings["info_limit"] > log_imp,
        "error": lambda log_imp: settings["error_minimum"] <= log_imp,
    }

    lines = get_data(settings)

    for line in lines:
        data = parse_data(line)
        if data is None:
            logs["skipped"].append(line)
            continue

        log_type, log_imp, log_msg = data

        if log_type.lower() in rules:
            if rules[log_type](log_imp):
                logs[log_type].append((log_type, log_imp, log_msg))
            else: logs["skipped"].append(line)
            
        else:
            logs["skipped"].append(line)

    return logs


def write_output(now, logs, settings):

    if settings["output"] in ["print", "both"]:
        data_writer(print, now, logs, settings)

    if settings["output"] in ["file", "both"]:
        with open(out_file, "w") as f:
            data_writer(lambda x: f.write(x + "\n"),now, logs, settings)


def data_writer(writer, now, logs, settings):

    #statistics to be added later

    display = {
        "info": "info",
        "error": "error",
    }

    limis = {
        "info": (f"<{settings['info_limit']}"),
        "error": (f"=>{settings['error_minimum']}")
    }

    writer(f"\n---{now}---\n")

    for log_type, entries in logs.items():
        if log_type in display:
            writer(f"\n{display[log_type]} {limis[log_type]}: {len(logs[log_type])}")
            for log_type, log_imp, log_msg in entries:
                writer(f"{log_type} --> {log_imp} --> {log_msg}")

        else:
            writer("\nskipped or invalid logs: ")
            for a in logs[log_type]:
                writer(f"{a.strip()}")

    writer("")


def main():

    if len(sys.argv) < 2:
        print("Incorrect argument passed")
        print("eg. python log.py <data.txt> <info_limit> <error_minimum> <print/file/both> <output_file.txt>")
        return None
        
    if len(sys.argv) < 4:
        print("not enough values provided, using default")
        print("eg. python log.py <data.txt> <info_limit> <error_minimum> <print/file/both> <output_file.txt>")
    
    settings = {
    "filename": sys.argv[1],
    "info_limit": get_argv(2, int, 1000),
    "error_minimum": get_argv(3, int, 100),
    "output": get_argv(4, str, "print").lower(),
    "out_file": get_argv(5, str, "info_error.txt").lower()
    }
    
    logs = parse_log(settings)

    write_output(now, logs, settings)
            
main()
