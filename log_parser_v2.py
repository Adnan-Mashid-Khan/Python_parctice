#!usr/bin/env python

import sys
from datetime import datetime
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")



def parser_state(filename, output):

    logs = {
        "config": { #1st nest
            "default": {
                "enabled": True,     # on/off,
                "structure": {
                    "log_type": str,
                    "log_imp": int,
                    "log_msg": str
                },  #part1- log_type, part2- importance, part3- message,
                "log_imp": None,     #minimum importance logs which should be shown
                "rules": {}   #how logs will be parsed
            },
            "known_log": {
                "info": {"log_imp": 100}, #basically same as default,
                "error": {"log_imp": 100},
                "warn": {"log_imp": 200}
            }
        }, #1st nest closed

        "runtime": { #2nd nest
            "parsed": {
                "info": [],
                "error": [],
                "warn": []
            },
            "rejected": {
                "invalid": [],
                "skipped": []
            },
            "new_log_type": {
                "unknown": []
            }
        }, #2nd nest closed

        "stats": {#3rd nest
            "summary": {
                "total_logs_processed": 0,
                "total_known_parsed": 0,
                "total_rejected_parsed": 0,
                "total_unknown_parsed": 0
            },
            "info": {"count": 0},
            "error": {"count": 0},
            "warn": {"count": 0},
            "skipped": {"count": 0},
            "invalid": {"count": 0},
            "unknown": {"count": 0}
        },#3rd nest closed

        "metadata": {#4th nest
            "status": "",#(success, fail, partial)
            "input_file": filename,
            "output_mode": output,
            "parser_ver": "1.0",
            "tot_read_line": 0,
            "start_time": "",
            "end_time": "",
            "execution_time": ""
        }#4th nest closed
    }

    return logs

def get_data(filename):
    #reads the input file and gives lines
    try: 
        with open(filename, "r") as file:
            lines = [line.strip() for line in file.readlines()]

        return lines
        
    except FileNotFoundError:
        print(f"{filename} not found")
        return []


def parse_logs(lines, logs):
    #takes the lines from get_data and loops them
    #then calls parse_line and apply_rule to decide
    #then stores it in parser_state dict
    for line in lines:
        parsed = parse_line(line)

        if parsed is None:
            logs["runtime"]["rejected"]["invalid"].append(line)
        else:
            log_type, imp, msg = parsed
            apply_rules(logs, log_type, imp, msg)


def parse_line(line):
    #it will take a line from parse_logs and break it into needed structure
    
    part = line.split()
    if len(part) < 3:
        return None

    try: 
        log_type = str(part[0]).lower()
    except IndexError:
        return None

    try:
        imp = int(part[1])
    except (ValueError, IndexError):
        return None
        
    msg = " ".join(part[2:])

    return log_type, imp, msg
    



def apply_rules(logs, log_type, imp, msg):
    #will decide what happens with the log through rules via calling parser_state() and rules inside it

    known_map= {
        "config": logs["config"]["default"].copy(),
        "destination": logs["runtime"]["parsed"],
        "key": log_type
    }

    unknown_map= {
        "config": logs["config"]["default"].copy(),
        "destination": logs["runtime"]["new_log_type"],
        "key": "unknown"
    }

    active = known_map if log_type in logs["config"]["known_log"] else unknown_map

    if log_type in logs["config"]["known_log"]:
        known_map["config"].update(logs["config"]["known_log"][log_type])

    if not isinstance(log_type, active["config"]["structure"]["log_type"]):
        logs["runtime"]["rejected"]["invalid"].append((log_type, imp, msg))
        return

    if not isinstance(imp, active["config"]["structure"]["log_imp"]):
        logs["runtime"]["rejected"]["invalid"].append((log_type, imp, msg))
        return
        
    if not isinstance(msg, active["config"]["structure"]["log_msg"]):
        logs["runtime"]["rejected"]["invalid"].append((log_type, imp, msg))
        return
        
    if active["config"]["enabled"]:
        if active["config"]["log_imp"] is None or imp >= active["config"]["log_imp"]:
            active["destination"][active["key"]].append((log_type, imp, msg))
        else:
            logs["runtime"]["rejected"]["skipped"].append((log_type, imp, msg))
    else:
        logs["runtime"]["rejected"]["skipped"].append((log_type, imp, msg))
            

def build_statistics(logs):
    
    for log_type in logs["runtime"]["parsed"]:

        p_count = len(logs["runtime"]["parsed"][log_type])

        logs["stats"]["summary"]["total_logs_processed"] += p_count

        logs["stats"]["summary"]["total_known_parsed"] += p_count

        logs["stats"][log_type]["count"] = p_count



    for log_type in logs["runtime"]["rejected"]:

        r_count = len(logs["runtime"]["rejected"][log_type])

        logs["stats"]["summary"]["total_logs_processed"] += r_count

        logs["stats"]["summary"]["total_rejected_parsed"] += r_count

        logs["stats"][log_type]["count"] = r_count

       

    for log_type in logs["runtime"]["new_log_type"]:
        new_count = len(logs["runtime"]["new_log_type"][log_type])
                            
        logs["stats"]["summary"]["total_logs_processed"] += new_count

        logs["stats"]["summary"]["total_unknown_parsed"] += new_count

        logs["stats"][log_type]["count"] += new_count

    #will show a simplified map of what happend to the data


def update_status(logs):
    if logs["stats"]["summary"]["total_logs_processed"] == 0:
        logs["metadata"]["status"] = "FAILED"
        
    elif logs["stats"]["summary"]["total_rejected_parsed"] == 0:
        logs["metadata"]["status"] = "SUCCESS"
        
    else:
        logs["metadata"]["status"] = "PARTIAL"


        

def build_report(writer, logs):
    writer("\nParser Report")
    writer("======================")
    writer(f"\nSTATUS: {logs['metadata']['status']}")
    writer(f"Parser Version: {logs['metadata']['parser_ver']}")
    writer(f"\nInput File: {logs['metadata']['input_file']}")
    writer(f"\nOutput Mode: {logs['metadata']['output_mode']}")
    writer(f"\nTotal Lines Read: {logs['metadata']['tot_read_line']}")
    writer(f"\nExecution Time: {logs['metadata']['execution_time']}")
    writer("----------------------")
    writer(f"\nSUMMARY\n")
    writer(f"Total Processes Logs: {logs['stats']['summary']['total_logs_processed']}")
    writer(f"Total Known Logs: {logs['stats']['summary']['total_known_parsed']}")
    writer(f"Total Rejected Logs: {logs['stats']['summary']['total_rejected_parsed']}")
    writer(f"Total Unknown Logs: {logs['stats']['summary']['total_unknown_parsed']}")
    writer(f"\n----------------------\n")
    writer(f"Known Log Count\n")
    for log_type in logs["runtime"]["parsed"]:
        writer(f"{(log_type).upper()} Count: {logs['stats'][log_type]['count']}")
    writer(f"\n----------------------\n")
    writer(f"Rejected Log Count\n")
    for log_type in logs["runtime"]["rejected"]:
        writer(f"{(log_type).upper()} Count: {logs['stats'][log_type]['count']}")
    writer(f"\n----------------------\n")
    writer(f"Unknown Log Count\n")
    writer(f"Unknown Count: {logs['stats']['unknown']['count']}")

    writer(f"\n----------------------\n")
    writer("Known Log Print")
    for log_type, entries in logs["runtime"]["parsed"].items():
        writer(f"\n{log_type.upper()}:")
        if len(entries) == 0:
            writer("No Logs For This Type")
        else:
            for _, imp, msg in entries:
                writer(f"{imp} --- {msg}")

    writer(f"\n----------------------\n")
    writer("Rejected Log Print")
    for log_type, entries in logs["runtime"]["rejected"].items():
        writer(f"\n{log_type.upper()}:")
        if len(entries) == 0:
            writer("No Logs For This Type")
        else:
            for entry in entries:
                if isinstance(entry, str):
                    writer(entry)
                elif isinstance(entry, tuple) and len(entry) == 3:
                    log_name, imp, msg = entry
                    writer(f"{log_name} --- {imp} --- {msg}")
                else:
                    writer(entry)


    writer(f"\n----------------------\n")
    writer("UnKnown Log Print")
    writer("\nUNKNOWN") #instead of log_type did this
    if len(logs["runtime"]["new_log_type"]["unknown"]) == 0:
        writer("No Logs For This Type")
    else:
        for log_type, imp, msg in logs["runtime"]["new_log_type"]["unknown"]:
            writer(f"{log_type} --- {imp} --- {msg}")
    
    
    #will decide the structure of how the data will be shown


def write_output(output, logs):
    if output in ("print", "both"):
        build_report(print, logs)
    if output in ("file", "both"):
        with open("log_parsed.txt", "w") as f:
            build_report(lambda x: f.write(x + "\n"), logs)
    
    
    #will give output

def main():

    if len(sys.argv) < 2:
        print("not enough data, using default")

    script_name = sys.argv[0]

    try:
        filename = sys.argv[1]
    except:
        print("raw logs file not given")
        filename = "messy_logs.txt"

    try:
        output = sys.argv[2]
    except:
        output = "print"
        
    logs = parser_state(filename, output)
    start_time = datetime.now()

    lines = get_data(filename)
    logs["metadata"]["tot_read_line"] = len(lines)

    parse_logs(lines, logs)
    build_statistics(logs)
    update_status(logs)

    end_time = datetime.now()
    execution_time = end_time - start_time

    logs["metadata"]["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
    logs["metadata"]["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
    logs["metadata"]["execution_time"] = str(execution_time)

    write_output(output, logs)
    

main()
    

    #oversees and call all function as necesarry
