import fnmatch
import os
import csv
import sys
import common
import eval_php

project_name = sys.argv[1]
parsed_dir = sys.argv[2]

sys.setrecursionlimit(10000)

ifile  = open(project_name+'-understand.csv', "rb")
reader = csv.reader(ifile)
ofile  = open(project_name+'-static.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

pwd = os.getcwd()
print pwd

for idx, row in enumerate(reader):
	if idx==0:
		row.append('Has_Session')
		row.append('Session_Reads')
		row.append('Session_Writes')

		row.append('Has_Param')
		row.append('Param_Reads')
		
		row.append('Defected')
		row.pop(0)
		writer.writerow(row)
	else:
		if row[0] == 'File' and common.check_path_valid(row[1]):
			
			path = row[1]
			parsed_path = parsed_dir+path[path.index("/", len(pwd)+1)+1:]
			print path+" "+parsed_path
			if (path.endswith(".php")):
				root = eval_php.parse_php(parsed_path)
				if (root is not None):
					reads = eval_php.count_session_read(root)
					writes = eval_php.count_session_write(root)
					params = eval_php.count_request_param_access(root)
				else:
					reads = 0
					writes = 0
					params = 0

				row.append(True if reads>0 or writes>0 else False)
				row.append(reads)
				row.append(writes)

				row.append(True if params>0 else False)
				row.append(params)
			else:
				row.append(False)
				row.append(0)
				row.append(0)

				row.append(False)
				row.append(0)

			row.append('no')
			row.pop(0)
			writer.writerow(row)

ifile.close()
ofile.close()