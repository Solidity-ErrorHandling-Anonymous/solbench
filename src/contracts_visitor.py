import os
import matplotlib.pyplot as plt
import numpy as np
import json
import re

contracts = []
contracts_list=[]
contracts={
    'contract':contracts_list
}
def findWord(dire, word1, word2, word3, word4):
    version=0
    for filename in os.listdir(dire):
      f = os.path.join(dire, filename)
      if os.path.isfile(f):
        print(f)
        infile = open(f,"r")
        total_asse=0
        ext_calls=0
        total_req=0
        total_try=0
        data = infile.read()
        req=data.count(word1)
        total_req+=req
#        print("require appear ", req)
        asse=data.count(word2)
        total_asse+=asse
#        print("assert appear ", asse)
        trr=data.count(word3)
        total_try+=trr
#        print("try-catch appear ", trr)
#        print("-----------------------")
#        print("--------0-------0---------")
        infile = open(f,"r")
        count=0
        func_count=0
        funcs_list=[]
        mod_list=[]
        const_list=[]
        Lines = infile.readlines()
        contract={}
        funcs={}
        contract={
            'name':f,
            'functions':funcs_list,
            'modifiers':mod_list,
            'constructors':const_list,
            'compiler versions':version
#            'lines':2
        }
        contracts_list.append(contract)
#        external_list=[]
        external_list=0
#        contracts['contract_name']=contract
#        print("Lines is"+str(Lines))
        for line in Lines:
#              print("file"+f+"having"+count+"lines")
            count += 1
            if "pragma" in line and "//" not in line and "ABIEncoderV2" not in line:
                line_list=line.split(" ")
                print(line_list)
                print(len(line_list))
                if len(line_list)==2:
                    version = line_list[1]
                else:
                    version = line_list[2]
                    print("Version is:", version)
            if re.findall('\\bfunction\\b', line):
                require_list=[]
                assert_list=[]
                revert_list=[]
                ext_calls=0
#                try_list=[]
                line_list=line.split(" ")
                print(line_list)
#                fun_name=line_list[2]
                fun =0
                fun_arguments = re.split(r'\(|\)',line)
#                print(fun_name)
                print(len(line_list))
                print(f)
                if "function" in line_list[0]:
                    func_count+=1
                    print('KOUKOUROYS')
                    if "function" in line_list:
                        funcs={
                            'function name': re.split(r'[(]', line_list[1])[0],
                            'function arguments': fun_arguments[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        funcs_list.append(funcs)
                        external_list=0
                        fun=1
                elif "function" in line_list[1] and ('*' not in line_list[0] and '//' not in line_list[0]):
                    func_count+=1
                    print('KOUKOUROYS')
                    if "function" in line_list:
                        funcs={
                            'function name': re.split(r'[(]', line_list[1])[0],
                            'function arguments': fun_arguments[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        funcs_list.append(funcs)
                        external_list=0
                        fun=1
                elif fun==0 and "function" in line_list[2] and "//" not in line_list[1] and "*" not in line_list[1] and "//" not in line_list[0] and "*" not in line_list[0] and "@" not in line_list[0] and "@" not in line_list[1] and "///" not in line_list[0] and "///" not in line_list[1]:
                    func_count+=1
                    if "function" in line_list:
                        funcs={
                            'function name': re.split(r'[(]', line_list[3])[0],
                            'function arguments': fun_arguments[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        funcs_list.append(funcs)
                        external_list=0
                        fun=1
                elif len(line_list)>3:
                    if fun==0 and "function" in line_list[3] and "//" not in line_list[2] and "*" not in line_list[2] and "//" not in line_list[1] and "*" not in line_list[1] and "//" not in line_list[0] and "*" not in line_list[0]:
                        fun_name=line_list[3]
                        func_count+=1
                        if "function" in line_list:
                            funcs={
                                'function name': re.split(r'[(]', line_list[4])[0],
                                'function arguments': fun_arguments[1],
                                'require':require_list,
                                'assert': assert_list,
                                'revert': revert_list,
                                'external calls':external_list,
                                'line': count
                            }
                            funcs_list.append(funcs)
                            external_list=0
                            fun=1
                elif len(line_list)>4:
                    if ("function" in line_list[4]) and ('*' not in line_list[3] and line_list[3] != "//") and ('*' not in line_list[2] and "//" not in line_list[2]) and ('*' not in line_list[1] and "//" not in line_list[1])  and ('*' not in line_list[0] and "//" not in line_list[0]) :
                        fun_name=line_list[4]
                        func_count+=1
                        if "function" in line_list:
                            funcs={
                               'function name': re.split(r'[(]', line_list[5])[0],
                               'function arguments': fun_arguments[1],
                               'require':require_list,
                               'assert': assert_list,
                               'revert': revert_list,
                               'external calls':external_list,
                               'line': count
                            }
                            funcs_list.append(funcs)
                            external_list=0
                else:
                    print(len(line_list))
                    if len(line_list)>5:
                        if "function" in line_list[5] and ('*' not in line_list[4] and "//" not in line_list[4])  and ('*' not in line_list[3] and "//" not in line_list[3])  and ('*' not in line_list[2] and "//" not in line_list[2])  and ('*' not in line_list[1] and "//" not in line_list[1])  and ('*' not in line_list[0] and "//" not in line_list[0]) :
                            fun_name=line_list[5]
                            func_count+=1
                            print("SOOSOSOOSOOSOSOOSOOSO")
                            if "function" in line_list:
                                funcs={
                                    'function name': re.split(r'[(]', line_list[6])[0],
                                    'function arguments': fun_arguments[1],
                                    'require':require_list,
                                    'assert': assert_list,
                                    'revert': revert_list,
                                    'external calls':external_list,
                                    'line': count
                                }
                                funcs_list.append(funcs)
                                external_list=0
                if len(line_list) > 6:
                    if line_list[5] == '*' or line_list[5] == '/':
                        print("Nothing / is note")
            if re.findall('\\bmodifier\\b', line):
                require_list=[]
                assert_list=[]
                revert_list=[]
#                try_list=[]
                line_list=line.split(" ")
                mod_arguments = re.split(r'\(|\)|\{',line)
                print(line_list)
                print(len(line_list))
                print(mod_arguments)
#                mod_name=line_list[2]
#                print(fun_name)
#                print("RE TI THA GINEI")
                if "modifier" in line_list[0] and "\\t" not in line_list:
                    func_count+=1
#                    print("tha boume???????")
                    if "modifier" in line_list[0]:
                        print("KAI OMWS")
                        mods={
                            'modifier name': re.split(r'[(]', line_list[1])[0],
                            'modifier arguments': line_list[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        mod_list.append(mods)
                        external_list=0
#                        print("OLA KALA")
                elif "modifier" in line_list[1]:
                    func_count+=1
                    if "modifier" in line_list[1] and "//" not in line_list[0] and "*" not in line_list[0]:
                        mods={
                            'modifier name': re.split(r'[(]', line_list[2])[0],
                            'modifier arguments': mod_arguments[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        mod_list.append(mods)
                        external_list=0
                elif "modifier" in line_list[2] and "//" not in line_list[1] and "//" and "//" not in line_list[0] and "*" not in line_list[0] and "*" not in line_list[0]:
                    func_count+=1
                    if "modifier" in line_list[2]:
                        mods={
                            'modifier name': re.split(r'[(]', line_list[3])[0],
                            'modifier arguments': line_list[3],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        external_list=0
                elif "modifier" in line_list[3] and "//" not in line_list[2] and "//" and "//" not in line_list[1] and "//" not in line_list[0] and r'(?i)\b[a-z]\b' in line_list[0] and "*" not in line_list[2] and "*" not in line_list[1] and "*" not in line_list[0] :
                    func_count+=1
                    if "modifier" in line_list[3]:
                        mods={
                            'modifier name': re.split(r'[(]', line_list[4])[0],
                            'modifier arguments': mod_arguments[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        mod_list.append(mods)
                        external_list=0
                elif line_list[4] == "modifier" and "//" not in line_list[3] and "//" not in line_list[2] and "//" not in line_list[1] and "//" not in line_list[0] and "*" not in line_list[2] and "*" not in line_list[1] and "*" not in line_list[0]:
                    func_count+=1
#                    print(mod_arguments)
                    if len(mod_arguments) == 1:
                        mods={
                            'modifier name': re.split(r'[(]', line_list[5])[0],
                            'modifier arguments': "-",
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        mod_list.append(mods)
                        external_list=0
                    else:
                        mods={
                            'modifier name': re.split(r'[(]', line_list[5])[0],
                            'modifier arguments': mod_arguments[1],
                            'require':require_list,
                            'assert': assert_list,
                            'revert': revert_list,
                            'external calls':external_list,
                            'line': count
                        }
                        mod_list.append(mods)
                        external_list=0
                else:
                    print("Nothing / is note")
            if re.findall('\\bconstructor\\b', line) and "type" not in line:
                require_list=[]
                assert_list=[]
                revert_list=[]
                const=0
#                try_list=[]
                line_list=line.split(" ")
                const_arguments = re.split(r'\(|\)',line)
#                print(line_list)
#                mod_name=line_list[2]
#                print(fun_name)
                print(line_list)
                if "constructor" in line_list[0]:
                     func_count+=1
                     print(f)
                     print("OELLELLE")
#                    print(const_arguments[1])
#                    print("prin boume")
                     if "constructor" in line_list[0]:
#                        print("bikameeeeeeee")
                         consts={
#                            'modifier name': re.split(r'[(]', line_list[3])[0],
                             'constructor arguments': const_arguments[1],
                             'require':require_list,
                             'assert': assert_list,
                             'revert': revert_list,
                             'external calls':external_list,
                             'line': count
                         }
                         const_list.append(consts)
                         external_list=0
                         const=1
                if len(line_list)>1:
                    if "constructor" in line_list[1] and "//" not in line_list[1] and "//" not in line_list[0]:
                        func_count+=1
                        print("OELLELLE")
#                    print(const_arguments[1])
#                    print("prin boume")
                        if "constructor" in line_list[1]:
#                        print("bikameeeeeeee")
                            consts={
#                            'modifier name': re.split(r'[(]', line_list[3])[0],
                                'constructor arguments': const_arguments[1],
                                'require':require_list,
                                'assert': assert_list,
                                'revert': revert_list,
                                'external calls':external_list,
                                'line': count
                            }
                            const_list.append(consts)
                            external_list=0
                            const=1
                if len(line_list)>2:
                    if "constructor" in line_list[2] and "*" not in line_list:
                        func_count+=1
                        print("OELLELLE")
#                    print(const_arguments[1])
#                    print("prin boume")
                        if "constructor" in line_list[2] and "*" not in line_list:
#                        print("bikameeeeeeee")
                            consts={
#                            'modifier name': re.split(r'[(]', line_list[3])[0],
                                'constructor arguments': const_arguments[1],
                                'require':require_list,
                                'assert': assert_list,
                                'revert': revert_list,
                                'external calls':external_list,
                                'line': count
                            }
                            const_list.append(consts)
                            external_list=0
                            const=1
                if len(line_list)>3:
                    if "constructor" in line_list[3] and "*" not in line_list:
                        func_count+=1
                        print(f)
                        print("OELLELLE")
#                    print(const_arguments[1])
#                    print("prin boume")
                        if "constructor" in line_list[3] and "*" not in line_list and "///" not in line_list and "//" not in line_list:
#                        print("bikameeeeeeee")
                            consts={
#                            'modifier name': re.split(r'[(]', line_list[3])[0],
                                'constructor arguments': const_arguments[1],
                                'require':require_list,
                                'assert': assert_list,
                                'revert': revert_list,
                                'external calls':external_list,
                                'line': count
                            }
                            const_list.append(consts)
                            external_list=0
                if len(line_list)>4:
                    if "constructor" in line_list[4] and "*" not in line_list:
                        func_count+=1
                        print(f)
                        print("OELLELLE")
#                    print(const_arguments[1])
#                    print("prin boume")
                        if "constructor" in line_list[4] and "*" not in line_list and "//" not in line_list:
#                        print("bikameeeeeeee")
                            consts={
#                            'modifier name': re.split(r'[(]', line_list[3])[0],
                                'constructor arguments': const_arguments[1],
                                'require':require_list,
                                'assert': assert_list,
                                'revert': revert_list,
                                'external calls':external_list,
                                'line': count
                            }
                            const_list.append(consts)
                            external_list=0
#                if "constructor" in line_list[5]:
#                    func_count+=1
##                    print(const_arguments[1])
##                    print("prin boume")
#                    if "constructor" in line_list[5]:
##                        print("bikameeeeeeee")
#                        consts={
##                            'modifier name': re.split(r'[(]', line_list[3])[0],
#                            'constructor arguments': const_arguments[1],
#                            'require':require_list,
#                            'assert': assert_list,
#                            'revert': revert_list,
#                            'line': count
#                        }
#                        const_list.append(consts)
#                if line_list[3] == "modifier":
#                    mod_name=line_list[3]
#                    func_count+=1
#                    if "function" in line_list:
#                        mods={
#                            'mod_name': re.split(r'[(]', line_list[3])[0],
#                            'require':require_list,
#                            'assert': assert_list,
#                            'line': count
#                        }
#                        mod_list.append(mods)
#                if line_list[4] == "modifier":
#                    mod_name=line_list[4]
#                    func_count+=1
#                    if "function" in line_list:
#                        mods={
#                            'mod_name': re.split(r'[(]', line_list[3])[0],
#                            'require':require_list,
#                            'assert': assert_list,
#                            'line': count
#                        }
#                        mod_list.append(modss)
#                if line_list[4] == '*' or line_list[4] == '/':
#                    print("Nothing / is note")
            if re.findall('\\.\\b',line):
                if '//' not in line:
                    external_list+=1
                    print('KOAIUSUUSISIISIISI',line)
#                    extc={
#                        'external calls': ext_calls
#                    }
#                    external_list.append(extc)
            if re.findall('\\brequire\\b', line):
                if "//" not in line:
                    if "(" in line:
                        args_list = re.split(r'\,|\(|\)', line)
                        print("EIMASTE EDDW")
                        print(args_list[0],args_list[1])
                        kou = 1
#                print(args_list)
#                if line_list[4]:
                        le=1
                        if len(args_list) > 2:
                            requ={
                                'require argument 1':args_list[1],
                                'require argument 2':args_list[2]
                            }
                            require_list.append(requ)
            if re.findall('\\brevert\\b', line):
                if "//" not in line and "*" not in line:
                    args_list = re.split(r'\,|\(|\)', line)
                    print("LINE IS:", line)
                    if len(args_list)>=2:
                        print("LINE IS:", line)
                        print("LELA")
                        print("LALLA",args_list[0],args_list[1])
                        kou = 1
#                print(args_list)
#                if line_list[4]:
                        le=1
                        if len(args_list) > 2:
                            revert={
                                'revert argument 1':args_list[1],
                                'revert argument 2':args_list[2]
                            }
                            revert_list.append(revert)
            if re.findall('\\bassert\\b', line):
                if "//" not in line:
                    print(line)
                    if "(" in line:
                        args_list2 = re.split(r'\,|\(|\)', line)
                        kou = 1
                        print("SKOUS")
                        print(args_list2)
#                        if line_list[5]:
                        le=1
                        print(len(args_list2))
                        if len(args_list2)>= 3:
                            print('bikame' + str(args_list2))
                            asse={
                                'assert argument 1':args_list2[1],
                                'assert argument 2':args_list2[2]
                            }
                            assert_list.append(asse)
        contracts['contract']=contracts_list
#        contracts['contract_name']['functions']=funcs_list
        with open('mydata3.json', 'w') as f:
            json.dump(contracts, f)

if __name__ == '__main__':
    findWord('../dataset/sample', 'require', 'assert', 'try {', 'revert')
#    findfunctions('./10condataset')
