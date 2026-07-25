#!/usr/bin/env python

import sys


class Config:
    def __init__(self):
        self.min_imp = {
            "info": 100,
            "error": 100,
            "warn": 50,
            "unknown": None
        }

    def get_min_imp(self, log_type):
        
        if log_type in self.min_imp:
            return self.min_imp[log_type]
        else: 
            return None
        


class Log:
    def __init__(self, log_type, imp, msg):
        self.log_type = log_type
        self.imp = imp
        self.msg = msg

    def display(self):
        return f"{self.log_type} -- {self.imp} -- {self.msg}"

    def validate(self):
        try:
            int(self.imp)
        except (ValueError, TypeError):
            return False
        try:
            if (
                isinstance(self.log_type, str)
                and isinstance(self.msg, str)
            ) and not (
                self.log_type == ""
                or self.msg == ""
            ): 
                return True
            else: return False
        except (ValueError, IndexError):
            return False


class FileReader:
    def __init__(self, filename):
        self.filename = filename

    def get_file(self):
        try:
            with open(self.filename, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                return lines
        except FileNotFoundError:
            print(f"{self.filename} file not found")
            return []
    


class Storage:
    def __init__(self):
        self.parsed = {
            "info": [],
            "error": [],
            "warn": [],
            "unknown": []
        }
        self.skipped = []
        self.invalid = []

    def add_parsed(self, log):
        log_type = (log.log_type).lower()
        if log_type in self.parsed:
            self.parsed[log_type].append(log)
        else:
            self.parsed["unknown"].append(log)

    def add_skipped(self, log):
        self.skipped.append(log)

    def add_invalid(self, log):
        self.invalid.append(log)
                

class Parser:
    def __init__(self, config):
        self.config = config


    def build_logs(self, lines, storage):
        for line in lines:
            log = self.parse_line(line)

            if log == None:
                continue
            
            elif not log.validate():
                storage.add_invalid(log)

            elif self.passes_importance(log):
                storage.add_parsed(log)

            else:
                storage.add_skipped(log)
                
            
    def parse_line(self, line):
        
        parts = line.split()
        if not parts:
            return
            
        if len(parts) > 0:
            

            try:
                log_type = parts[0]
            except (ValueError, IndexError):
                log_type = ""

            try:
                imp = parts[1]
            except (ValueError, IndexError):
                imp = ""
                
            try:
                msg = " ".join(parts[2: ])
            except (ValueError, IndexError):
                msg = ""
                
            log = Log(log_type, imp, msg)

            return log

            

    def passes_importance(self, log):
        imp = int(log.imp)
        log_type = log.log_type.lower()
        min_imp = self.config.get_min_imp(log_type)

        if min_imp is None:
            return True
        elif imp >= min_imp:
            return True
        else:
            return False


class Statistics:
    def total_lines(self, lines):
        total_lines = len(lines)

        return total_lines

    def total_logs(self, storage):

        parsed_count = 0
        count= {
            "info": 0,
            "error": 0,
            "warn": 0,
            "unknown": 0
        }

        for log_type in storage.parsed:
            parsed_count += len(storage.parsed[log_type])
            count[log_type] += len(storage.parsed[log_type])

        skipped_count = len(storage.skipped)
        invalid_count = len(storage.invalid)

        total_logs = parsed_count + skipped_count + invalid_count

        total = total_logs, parsed_count, skipped_count, invalid_count, count
        
        return total
    

class MetaData:
    def meta(self, filename, output, config):
        data = {
            "Parser version": "2.2",
            "Raw File": filename,
            "Output Method": output,
            "Configuration": "default"
        }

        min_imp = config.min_imp

        data_min_imp = data, min_imp
        return data_min_imp


class Report:

    def stats_organizer(self, total_lines, total):

        total_logs, parsed_count, skipped_count, invalid_count, count = total
        
        stats_lines = []
        
        stats_lines.append("\nStatistics\n---------")
        stats_lines.append(f"Total Lines in raw File: {total_lines}")
        stats_lines.append(f"Total Logs Parsed: {total_logs}")
        stats_lines.append(f"Total Parsed Count: {parsed_count}")
        stats_lines.append(f"Total Skipped Count: {skipped_count}")
        stats_lines.append(f"Total Invalid Count: {invalid_count}")
        stats_lines.append("\nParsed Breakdown\n---------")
        for log_type in count:
            stats_lines.append(f"{log_type.upper()} Count: {count[log_type]}")

        return "\n".join(stats_lines)


    def meta_organizer(self, data_min_imp):
        data, min_imp = data_min_imp
        meta_lines = []

        meta_lines.append("\nMETADATA\n----------")
        for name in data:
            meta_lines.append(f"{name.upper()}: {data[name]}")

        meta_lines.append("\nMinimum Importance\n----------")
        for min in min_imp:
            meta_lines.append(f"{min.upper()}: {min_imp[min]}")

        return "\n".join(meta_lines)

    def logs_organizer(self, storage):
        logs_lines = []
        logs_lines.append("\nparsed logs \n------------")

        for log_type in storage.parsed:
            logs_lines.append(f"{log_type} logs:")
            if len(storage.parsed[log_type]) == 0:
                logs_lines.append("No Logs of this type")
            for log in storage.parsed[log_type]:
                logs_lines.append(log.display())
                
            logs_lines.append("\n----")
                
        logs_lines.append("\nSkipped Log \n------------")
        for log in storage.skipped:
            logs_lines.append(log.display())
            
        logs_lines.append("\ninvalid logs \n------------")
        for log in storage.invalid:
            logs_lines.append(log.display())

        return "\n".join(logs_lines)

class Writer:
    def output(self, report, total_lines, total, data_min_imp, storage, output):

        stats_lines = report.stats_organizer(total_lines, total)
        meta_lines = report.meta_organizer(data_min_imp)
        logs_lines = report.logs_organizer(storage)

        print(stats_lines)
        print(meta_lines)

        if output in ("print", "both"):
            print(logs_lines)

        if output in ("file", "both"):
            with open("write_logs.txt", "w") as f:
                f.write(stats_lines)
                f.write(meta_lines)
                f.write(logs_lines)


def main():
    if len(sys.argv) < 2:
        print(f"not enough information \npython class_parser.py <raw.log> <print/file/both")
    
    filename = sys.argv[1]

    try:
        output = sys.argv[2]
    except IndexError:
        output = "file"
        print("not enough values, using default")

    config = Config()

    filereader = FileReader(filename)
    lines = filereader.get_file()

    storage = Storage()
    
    parser = Parser(config)
    parser.build_logs(lines, storage)

    stats = Statistics()
    total_lines = stats.total_lines(lines)
    total = stats.total_logs(storage)

    metadata = MetaData()
    data_min_imp = metadata.meta(filename, output, config)
    
    report = Report()

    writer = Writer()
    writer.output(report, total_lines, total, data_min_imp, storage, output)

    
main()
