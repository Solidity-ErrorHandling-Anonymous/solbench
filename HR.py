from pathlib import Path 
import re

file = Path('~/solbench/data/sample/0xfd1d97f0d8b100a9df095b40a13520af13df7ec1.sol')
with file.open() as open_file:
    for line in open_file:
        if ('enum' in line): # enum type
            enumtype = line.split(" ")[1]
            print(enumtype)
            file = Path('0xfd1d97f0d8b100a9df095b40a13520af13df7ec1.sol')
            with file.open() as open_file:
                for line in open_file:
                    if (enumtype in line):
                        print(line)
#        print(line, end="")
        if(re.findall(r"\.\b", line) and ('*' not in line)): #external Calls
            print(line)
        if(re.search(r'\bfunction\b',line)):
            print(line)
        if(re.findall(r'\([^()]*\)', line)) and ((re.search(r'\bfunction\b',line))):  # function arguments
            print(line)
        if((re.search(r'\btry new\b',line))): #external contract
            print(line)
        if((re.search(r'revert?\W+(\w+)(\(\w+\))?(, (\w+)(\(\w+\))?)*',line))): #revert statement- function
            print(line)
        if((re.search(r'\w+\*\.*',line))):
            print(line)
        if(re.findall(r"\[\b", line)): #arrays
            print(line)
        if(re.findall('[/]', line)) and ("/*" not in line) and ("*" not in line) and ("//" not in line): #div1
            print(line)
        if(re.findall(r'\bdiv\b', line)) and ("/*" not in line) and ("*" not in line) and ("//" not in line): #div2
            print(line)
        if(re.findall('[*+\/-]+|[A-Za-z]+', line)) and ("*/" not in line) and ("//" not in line) and ("@" not in line): #overflows
            print(line)
        if((re.search(r'\bassert\b',line))): #program logic
            print(line)
#print(re.findall("(\.\s+[a-zA-Z]+)", file))
