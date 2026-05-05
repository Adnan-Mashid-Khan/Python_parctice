#!/usr/bin/env python

def get_num():
    with open("data.txt", "r") as f:
        lines = f.readlines()
    num = []
    for line in lines:
        for t in line.split():
            num.append(int(t))
    return num

def check_num(t):
    if t > 25:
        return "HIGH"
    else:
        return "LOW"

def main():
    numbers = get_num()
    high_num = []
    low_num = []

    for t in numbers:
        status = check_num(t)

        if status == "HIGH":
            high_num.append(t)
        else:
            low_num.append(t)

    print(f"\nHigh Numbers: {high_num}")
    print(f"Low Numbers: {low_num}")

main()
