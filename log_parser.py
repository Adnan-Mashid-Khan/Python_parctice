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
        field = line.split()
        if result is None and len(field) < 3 :
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


def build_statistics(logs):

    stats = {
        "summary": {
            "total_processed": 0,
            "valid_logs": 0,
            "skip_or_invalid": 0,
        },
        "info": {
            "largest": None,
            "smallest": None,
            "count": 0,
        },
        "error": {
            "largest": None,
            "smallest": None,
            "count": 0,
        },
        "warning": {
            "largest": None,
            "smallest": None,
            "count": 0,
        },
    }

    
    for log_type, entries in logs.items():
        stats["summary"]["total_processed"] += len(entries)
        if log_type in ("skipped", "invalid"):
            stats["summary"]["skip_or_invalid"] += len(entries)
        else:
            stats["summary"]["valid_logs"] += len(entries)

            if log_type not in ("skipped", "invalid"):
                for type_log, data, msg in entries:

                    if log_type in stats:
                        stats[log_type]["count"] += 1

                    if stats[log_type]["largest"] is None:
                        stats[log_type]["largest"] = data
                    else:
                        if data > stats[log_type]["largest"]:
                            stats[log_type]["largest"] = data
            
                    if stats[log_type]["smallest"] is None:
                        stats[log_type]["smallest"] = data
                    else:
                        if data < stats[log_type]["smallest"]:
                            stats[log_type]["smallest"] = data

    return stats

def write_report(writer, lines, logs, stats, limit, elimit, now):

    display = {
        "info": f"<{limit}",
        "error": f">={elimit}",
        "warning": "<1000"
    }
    
    writer(f"\n---Parsed Logs---\n")
    writer(f"Run Time: {now.strftime("%Y-%m-%d %H:%M:%S")}\n")
            
    writer(f"Total Lines in main file = {len(lines)}")
    writer(f"Total Processed Lines = {stats["summary"]["total_processed"]}")
    writer(f"Total Valid Logs = {stats["summary"]["valid_logs"]}")
    writer(f"Total Skipped/Invalid Logs = {stats["summary"]["skip_or_invalid"]}\n")
    
    for log_type, data in stats.items():
        if log_type == "summary": continue
        writer(f"{log_type} Count = {data['count']}")
        writer(f"Smallest {log_type} Value = {data["smallest"]}")
        writer(f"Largest {log_type} Value = {data["largest"]}\n")

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
                

def write_output(output, lines, logs, stats, limit, elimit, now):
    if output in ["print", "both"]:
        write_report(print, lines, logs, stats, limit, elimit, now)
        
    if output in ["file", "both"]:
        with open("log_parsed.txt", "w") as f:
            write_report(lambda x: f.write(x + "\n"), logs, stats, limit, elimit, now)

        
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
    stats = build_statistics(logs)

    write_output(output, lines, logs, stats, limit, elimit, now)

main()

