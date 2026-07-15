#!usr/bin/env python

import random
import string



def struct():

    structure = {
        "known": {#k1
            "log_type": ["info", "error", "warn"],
            "importance": {
                "min": 100,
                "max": 800
                },
            "message": {#k1.1
                "info": [
                    "user_login",
                    "backup_complete",
                    "service_started"
                ],
                "error": [
                    "server_crash",
                    "database_failure"
                ],
                "warn": [
                    "storage_full",
                    "90% ram used in 3 mins",
                    "90% storage full",
                    "too many login attempts"
                ]
            },
            "optional_timestamp": True,
            "optional_spaces": True
        },
        
        "unknown": {
            "log_type": {
                "type": str,
                "length": {
                    "min": 4,
                    "max": 10
                }
            },
            "importance": {
                "min": 100,
                "max": 600,
            },
            "message": {
                "type": str,
                "words": {
                    "min": 1,
                    "max": 30
                    },
                "word_length": {
                    "min": 4,
                    "max": 12
                }
            },
            "optional_timestamp": True,
            "optional_spaces": True
        },
        
        "invalid": {
            "missing": {
                "missing_log_type": True,
                "missing_importance": True,
                "missing_message": True,
                },

            "garbage": {
                "text": {
                    "type": str,
                    "length": {
                        "min": 1,
                        "max": 5
                        }
                    },
                 "num": {
                    "type": int,
                    "value": {
                        "min": -999,
                        "max": 999
                        }
                    }
                },
            "empty_line": True,
            }
        }


    return structure


def configuration():

    config = {
        "number_of_logs": 1000,
        "known": 70,
        "unknown": 18,
        "invalid": 12,
        "seed": None,
        "output_mode": "file",
        "output_filename": "raw_logs.log"
    }

    return config


def generator(config, structure):

    total_logs = config["number_of_logs"]

    if config["seed"] is not None:
        random.seed(config["seed"])

    for log in range(total_logs):
        dice = random.randint(1, 100)

        if dice <= 70:
            log_type = random.choice(structure["known"]["log_type"])

            log_imp = random.randint(structure["known"]["importance"]["min"], structure["known"]["importance"]["max"])

            log_msg = random.choice(structure["known"]["message"][log_type])

            log_line = f"{log_type} {log_imp} {log_msg}"
            output_writer(log_line)


        elif dice <= 88:
            
            type_length = random.randint(structure["unknown"]["log_type"]["length"]["min"], structure["unknown"]["log_type"]["length"]["max"])

            msg_length = random.randint(structure["unknown"]["message"]["words"]["min"], structure["unknown"]["message"]["words"]["max"])

            abc = []
            words = []

            for loop in range(type_length):
                letter = random.choice(string.ascii_lowercase)
                abc.append(letter)

            log_type = "".join(abc)

            log_imp = random.randint(structure["unknown"]["importance"]["min"], structure["unknown"]["importance"]["max"])

            for loop in range(msg_length):

                xyz_length = random.randint(structure["unknown"]["message"]["word_length"]["min"], structure["unknown"]["message"]["word_length"]["max"])

                xyz = []
                
                for loop in range(xyz_length):
                    letter = random.choice(string.ascii_lowercase)
                    xyz.append(letter)
                
                words.append("".join(xyz))

            log_msg = " ".join(words)

            log_line = f"{log_type} {log_imp} {log_msg}"
            output_writer(log_line)
        #use unknown structure



        else:
            empty = structure["invalid"]["empty_line"]
            missing = structure["invalid"]["missing"]
            wrong = structure["invalid"]["garbage"]

            collection = [missing, wrong, empty]
            mis_wro = [missing, wrong]

            result = {
                "log_type": "",
                "imp": "",
                "msg": ""
            }

            if random.choice(collection) is not empty:

                for field in ["log_type", "imp", "msg"]:
                    choice = random.choice(mis_wro) 
                    if choice == missing:
                        result[field] = ""

                    else:
                        form_type = random.choice(list(wrong))
                        form = wrong[form_type]
                        if form_type == "num":
                            result[field] = random.randint(form["value"]["min"], form["value"]["max"])

                        else:
                            length = random.randint(form["length"]["min"], form["length"]["max"])
                            
                            cba = []
                            
                            for loop in range(length):
                                letter = random.choice(string.ascii_lowercase)
                                cba.append(letter)

                            result[field] = "".join(cba)

                log_line = f"{result['log_type']} {result['imp']} {result['msg']}"
                output_writer(log_line)

            else:
                log_line = "\n"
                output_writer(log_line)
                            
                            


            
        #use invalid structure



def output_writer(log_line):

    with open("raw_logs.log", "a") as f:
        f.write(log_line + "\n")



def main():

    config = configuration()
    structure = struct()
    generator(config, structure)

main()
