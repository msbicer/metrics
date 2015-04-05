import re
import sys
import os
import subprocess
import json
import hashlib
import csv
import pdb
import cssselect
from sets import Set

def build_files_set(rootdir):
    root_to_subtract = re.compile(r'^.*?' + rootdir + r'[\\/]{0,1}')

    files_set = {}
    for (dirpath, dirnames, filenames) in os.walk(rootdir):
        for filename in filenames + dirnames:
            full_path = os.path.join(dirpath, filename)
            relative_path = root_to_subtract.sub('', full_path, count=1)
            files_set[relative_path] = full_path

    return files_set

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
    escaping = False
    in_string = False
    for idx, c in enumerate(data):
        #print c+" "+str(escaping)+" "+str(in_string)
        if c == "\\":
            escaping = not escaping
        
        if escaping:
            continue

        if c == "\"":
            in_string = not in_string
            
        if in_string:
            continue

        if c == "{":
            #pdb.set_trace()
            # print "push"
            stack.append({
                'index':idx,
                'name':selector(idx,data,stack,last_block)
            })
            last_block = idx
        elif c == "}":
            #pdb.set_trace()
            # print "pop"
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

def get_metrics(rule):
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

    remove = ["imports","comments","commentsLength","duplicatedSelectors","emptyRules","base64Length"]
    for key in remove:
        metrics.pop(key, None)

    selectors = rule[:rule.find("{")]
    css = cssselect.parse(selectors)
    i = 0
    specificity = 0
    while i<len(css):
        tmp = css[i].specificity()
        val = tmp[2] + tmp[1]*10 + tmp[0]*100
        if val>specificity:
            specificity = val
        i+=1

    metrics["specificity"] = specificity
    if specificity>=100:
        metrics["specificity_category"] = 'high'
    elif specificity>=10:
        metrics["specificity_category"] = 'medium'
    else:
        metrics["specificity_category"] = 'low'

    return metrics

def compare_files(css_file1, css_file2):
    global writer
    global row_index

    data1 = read_css(css_file1)
    data2 = read_css(css_file2)
    # pdb.set_trace()
    rules = get_rules(data1)
    compare_rules = get_rules(data2)
    table = Set()
    for r in compare_rules:
        h = hashlib.sha256(removeComments(r)).hexdigest()
        table.add(h)

    for rule in rules:
        #print rule
        try:
            metrics = get_metrics(rule)

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
        except Exception, e:
            #print "can't parse selector : "+rule
            pass
        

#if __name__ == '__main__':

row_index = 0

project_name = sys.argv[1]
file1 = sys.argv[2]
file2 = sys.argv[3]

ofile  = open(project_name+"-css.csv", "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

#pdb.set_trace()
if (file1.endswith("/") and file2.endswith("/")):
    files_set1 = build_files_set(file1)
    files_set2 = build_files_set(file1)
    for relative_path in files_set1:
        if (relative_path in files_set2) and ("tests/" not in relative_path) and (relative_path.endswith(".css") or (".css." in relative_path)):
            print "inspecting : "+relative_path
            compare_files(files_set1[relative_path], files_set2[relative_path])
else:
    compare_files(file1, file2)
ofile.close()

# rootDir = '.'
# for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
#     print('Found directory: %s' % dirName)
#     for fname in fileList:
#       if fname
#         print('\t%s' % fname)