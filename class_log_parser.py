#!/usr/bin/env python

import sys

class Log:
    def __init__(self, log_type, imp, msg):
        self.log_type = log_type
        self.imp = imp
        self.msg = msg

    def display(self):
        print(f"{self.log_type} -- {self.imp} -- {self.msg}")

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
        

class Parser:
    def __init__(self, filename):
        self.filename = filename
        self.parsed = []
        self.skipped = []
        self.invalid = []
        self.min_imp = 100


    def get_file(self):
        try:
            with open(self.filename, "r") as f:
                lines = [line.strip() for line in f.readlines()]
                return lines
        except FileNotFoundError:
            print(f"{self.filename} file not found")
            return []

    def build_logs(self, lines):
        for line in lines:
            log = self.parse_line(line)

            if not log.validate():
                self.invalid.append(log)

            elif self.passes_importance(log):
                self.parsed.append(log)     

            else:
                self.skipped.append(log)
            
    def parse_line(self, line):
        
        parts = line.split()
        if len(parts) > 0:
            

            try:
                log_type = parts[0]
            except (ValueError, IndexError):
                log_type = ""

            try:
                imp = parts[1]
            except (ValueError, IndexError):
                imp = None
                
            try:
                msg = " ".join(parts[2: ])
            except (ValueError, IndexError):
                msg = ""
                
            log = Log(log_type, imp, msg)

            return log

    def passes_importance(self, log):
        imp = int(log.imp)
        try:
            if imp >= self.min_imp:
                return True
            else: 
                return False
        except TypeError:
            return False

    def output(self):
        print("parsed logs \n------------")
        for log in self.parsed:
            log.display()
        print("\nSkipped Log \n------------")
        for log in self.skipped:
            log.display()
        print("\ninvalid logs \n------------")
        for log in self.invalid:
            log.display()
        



def main():
    if len(sys.argv) < 2:
        print(f"not enough information \npython class_parser.py <raw.log>")
    
    filename = sys.argv[1]

    parser = Parser(filename)
    lines = parser.get_file()
    parser.build_logs(lines)
    parser.output()
main()






#log1 = Log("error",500, "Disk full")

#if log1.validate() is True:
    #log1.display()
#else: print("log not valid")
