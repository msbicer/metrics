import re
import sys
import os
import subprocess
import json
import hashlib
import csv
import pdb
from sets import Set

css_file1 = sys.argv[1]
css_file2 = sys.argv[2]
out_path =  css_file1[0:css_file1.index('.')]+".csv"

ofile  = open(out_path, "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

def removeComments(string):
    string = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,string)
    return string

def read_css(file_path):
	with open (file_path, "r") as myfile:
	    data=myfile.read().replace('\n', '')
	data = removeComments(data)
	return data

def selector(index,data,stack,last_block):
	selectors = []
	for obj in stack:
		selectors.append(obj['name']+"{")
	selectors.append(data[last_block+1:index].strip())

	return ' '.join(selectors)

def get_rules(data):
	stack = []
	last_block = -1
	rules = []
	for idx, c in enumerate(data):
		if c == "{":
			# pdb.set_trace()
			stack.append({
				'index':idx,
				'name':selector(idx,data,stack,last_block)
			})
			last_block = idx
		elif c == "}":
			obj = stack.pop()
			if obj['index'] == last_block:
				text = obj['name']+" {"+data[obj['index']+1:idx]
				for obj in stack:
						text+="}"
				text+="}"

				# replaced = re.sub('\s{2,}',' ',text)
				replaced = re.sub('([:;,{}])\s+',r'\1',text)
				# pdb.set_trace()
				rules.append(replaced)
			last_block = idx
		elif c == ";":
			if len(stack)==0:
				last_block = idx
	return rules

data1 = read_css(css_file1)
data2 = read_css(css_file2)
# pdb.set_trace()
rules = get_rules(data1)
compare_rules = get_rules(data2)
table = Set()
for r in compare_rules:
	h = hashlib.sha256(removeComments(r)).hexdigest()
	table.add(h)

row_index = 0
for rule in rules:
	# print rule
	proc = subprocess.Popen(['echo "'+rule+'" | analyze-css -'],stdout=subprocess.PIPE, shell=True)
	(o, err) = proc.communicate()
	result = json.loads(o)
	metrics = result["metrics"]
	if ("rules" not in metrics):
		metrics["rules"] = 0
	if ("declarations" not in metrics):
		metrics["declarations"] = 0
	if ("selectors" not in metrics):
		metrics["selectors"] = 0

	# print metrics

	row = []
	header = []

	# header.append("Hash")

	h = hashlib.sha256(removeComments(rule)).hexdigest()
	# row.append(h)

	for k in metrics:
		if (row_index == 0):
			header.append(k)
		row.append(metrics[k])

	header.append("Defected")
	if h in table:
		row.append(False)
	else:
		row.append(True)
		print "defected : "+rule

	if (row_index == 0):
		writer.writerow(header)
	row_index+=1

	writer.writerow(row)

ofile.close()
