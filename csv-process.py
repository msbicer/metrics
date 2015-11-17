import csv
import sys
import common

project_name = sys.argv[1]
metric_type = sys.argv[2]
if len(sys.argv) > 3:
    parsed_dir = sys.argv[3]
else:
    parsed_dir = None

def check_map(name):
    name = name.replace('\\','/')
    global defected
    for key in defected:
        # print 'check_map ',key,' ==> ',name
        if key in name:
            return defected[key]
    return 0

defected = {}

with open(project_name+"-modified.txt") as f:
    for line in f:
        #print line.strip()
        #defected[line.strip()] = 1
        filename = line.strip()
        if filename in defected:
            defected[filename] += 1
        else:
            defected[filename] = 1

#print d

ifile  = open(project_name+'-'+metric_type+'.csv', "rb")
reader = csv.reader(ifile)
ofile  = open(project_name+'-'+metric_type+'-labeled.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

i = 0
for idx, row in enumerate(reader):
    # row is a list of strings
    file_path = row[0].replace('\'', '')
    #print 'row',row,' ==> ',file_path
    #print 'path : ',file_path
    if (idx==0 or common.check_path_valid(file_path)):
        found = check_map(file_path)
        class_idx = len(row)-1
        print str(i)+" "+str(len(row))+" "+file_path+" "+row[class_idx]+" "+str(found)+" "+str(file_path.__len__())
        i=i+1
        if (idx==0):
            row[class_idx-1] = 'Defect_Count'
            row[class_idx] = 'Defected'
        elif found>0:
            row[class_idx-1] = found/float(row[14])
            row[class_idx] = 'yes'
        else:
            row[class_idx-1] = 0
            row[class_idx] = 'no'
        writer.writerow(row)
ifile.close()
ofile.close()