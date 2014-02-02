import fnmatch
import os
import csv
import sys
import common

project_name = sys.argv[1]

ifile  = open(project_name+'-understand.csv', "rb")
reader = csv.reader(ifile)
ofile  = open(project_name+'-static.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

for idx, row in enumerate(reader):
	if idx==0:
		row.append('Defected')
		row.pop(0)
		writer.writerow(row)
	else:
		if row[0] == 'File' and common.check_path_valid(row[1]):
			row.append('no')
			row.pop(0)
			writer.writerow(row)

ifile.close()
ofile.close()