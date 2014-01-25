import csv
import sys

project_name = sys.argv[1]

def check_map(name):
    name = name.replace('\\','/')
    global defected
    for key in defected:
        if key in name:
            return True
    return False

defected = {}

with open(project_name+"-modified.txt") as f:
    for line in f:
       print line.strip()
       defected[line.strip()] = 1

#print d

ifile  = open(project_name+'-churn.csv', "rb")
reader = csv.reader(ifile)
ofile  = open(project_name+'-churn-labeled.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

i = 0
for idx, row in enumerate(reader):
    # row is a list of strings
    file_path = row[0].replace('\'', '')
    #print 'path : ',file_path
    if (idx==0 or ('Tests/' not in file_path and (file_path.endswith('.php') or file_path.endswith('.js') or file_path.endswith('.html') or file_path.endswith('.css') or file_path.endswith('.xml')))):
        found = check_map(file_path)
        class_idx = len(row)-1
        print str(i)+" "+str(len(row))+" "+file_path+" "+row[class_idx]+" "+str(found)+" "+str(file_path.__len__())
        i=i+1
        if found:
            row[class_idx] = 'yes'
        else:
            row[class_idx] = 'no'
        writer.writerow(row)
ifile.close()
ofile.close()