import sys
import csv
import wget
import html
import os

def getFilenameSameLine(line):
	flag = 0
	offsetStart = line.find('"') + 1
	while (flag==0):
		offsetEnd = offsetStart + 1
		while(line[offsetEnd]!= '"'):
			if(line[offsetEnd] == '/'):
				offsetStart = offsetEnd + 1
			offsetEnd+=1
		name = line[offsetStart : offsetEnd]
		z = name.find(".sol")
		if (z!=-1):
			flag = 1
		else:
			offsetStart = offsetEnd + 1
	return name

def getFilenameNewLine(line):
	offsetStart = line.find('"') + 1
	offsetEnd = offsetStart + 1
	while(line[offsetEnd]!= '"'):
		if(line[offsetEnd] == '/'):
			offsetStart = offsetEnd + 1
		offsetEnd+=1
	name = line[offsetStart : offsetEnd]
	return name

def cropFiles(dir):
	with open(dir + 'escaped.txt') as file:
		content = file.read()
		if '"content":' in content:
			multiFile = 1
		else:
			multiFile = 0
	file.close()
	f = open(dir + "escaped.txt","r")
	lines = f.read().splitlines()
	writemode = 0
	previousLine = "proxy"
	if (multiFile == 1) :
		for x in lines:
			if (writemode == 1):
				if ((x == '"') and (previousLine == '}')):
					ff.close()
					writemode = 0
				elif (len(x) > 1):
					if ((x[0] == '}') and (x[1]== '\"')):
						ff.write("}\n")
						ff.close()
						writemode = 0
					elif ((x[0] == '\"') and (x[1]== '}')):
						ff.close()
						t = x.find(".sol")
						if(t!=-1):
							filename = getFilenameSameLine(x[1:])
							ff = open(dir + filename,"a")
							offset = i + len('"content": "')
							restOfString = x[offset:]
							ff.write(restOfString + "\n")
						else:
							writemode = 0
					else :
						ff.write(x + "\n")
				else :
					ff.write(x + "\n")
			else:
				i = x.find('"content":')
				if (i!=-1):
					y = x.find(".sol")
					if(y!=-1):
						try:
							filename = getFilenameSameLine(x)
						except:
							print (x)
							return 0
					else:
						filename = getFilenameNewLine(previousLine)
					ff = open(dir + filename,"a")
					offset = i + len('"content": "')
					restOfString = x[offset:]
					ff.write(restOfString + "\n")
					writemode = 1
			previousLine = x
	else :
		for x in lines:
			if (writemode == 1):
				if ((x == '\"')  and (previousLine == '}')):
					ff.close()
					writemode = 0
				elif (len(x) > 1):
					if ((x[0] == '}') and (x[1]== '\"')):
						ff.write("}\n")
						ff.close()
						writemode = 0
					elif ((x[0]=='\"') and (previousLine == '}')):
						ff.close()
						writemode = 0
					else:
						ff.write(x + "\n")
				else:
					ff.write(x + "\n")
			else:
				i = x.find('"SourceCode":"')
				if (i!=-1):
					filename = dir + "standard.sol"
					ff = open(filename,"a")
					offset = i + len('"SourceCode":"')
					restOfString = x[offset:]
					ff.write(restOfString + "\n")
					writemode = 1
			previousLine = x
	return 0



contractNum = input("Choose the number of contracts to download:\n")
flag= 0
apiSwitch = True
exist = os.path.exists('contracts')
if (exist == False) :
	os.mkdir('contracts')
with open("export-verified-contractaddress-opensource-license3.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        dict = list(reader)
for row in dict :
	ContractName = row["ContractName"]
	ContractAddress = row["ContractAddress"]
	isExist = os.path.exists('contracts/' + ContractName)
	if (isExist == True) :
		print(ContractName)
		continue
	else :
		path = 'contracts/' + ContractName
		os.mkdir(path)
		try :
			if (apiSwitch == True):
				wget.download('https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + ContractAddress + '&apikey=134UIX3T11BZN1QNIRMK5S4VETWJ6QH1KN', path + '/raw.txt')
				apiSwitch = False
			elif (apiSwitch == False):
				wget.download('https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + ContractAddress + '&apikey=XN14FHPZYYVI3HDDHYZD96VCSBI3JW76QY', path + '/raw.txt')
				apiSwitch = True
		except:
			print("\n Download failed for :" + path +"\n")
			os.rmdir(path)
			continue
		f = open(path + '/raw.txt',"r")
		data = f.read()
		try:
			escaped1 = data.encode('utf-8').decode('unicode_escape')
			escaped2 = escaped1.encode('utf-8').decode('unicode_escape')
		except:
			print ('Escape error on: ' + path + '\n')
			os.remove(path + '/raw.txt')
			os.rmdir(path)
			continue
		ff = open(path + "/escaped.txt","w")
		ff.write(escaped2)
		ff.close()
		f.close()
		os.remove(path + '/raw.txt')
		cropFiles(path + '/')
		os.remove(path + '/escaped.txt')
		flag += 1
		if (flag == int(contractNum)) :
			break
