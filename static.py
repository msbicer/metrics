import fnmatch
import os
import subprocess
import json
import csv
import sys
import common
import eval_php
import html

project_name = sys.argv[1]
parsed_dir = sys.argv[2]

sys.setrecursionlimit(10000)

# print "Loading complexity data..."
# stats_file = project_name+'-metrics.json'
# with open(stats_file) as stats_file:    
#     data = json.load(stats_file)
# complexity = {}
# for row in data:
# 	complexity[row['filename']] = row
# print "Data loaded"

ifile  = open(project_name+'-understand.csv', "rb")
reader = csv.reader(ifile)
ofile  = open(project_name+'-static.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

pwd = os.getcwd()
print pwd

ignore = []

for idx, row in enumerate(reader):
	html_loc = 0
	if idx==0:
		for i,x in enumerate(row):
			if x.endswith('_Html') or x.endswith('_Php') or x.endswith('_Javascript'):
				ignore.append(i)

		# row.append('bugs')
		# row.append('difficulty')
		# row.append('effort')
		# row.append('length')
		# row.append('MI')
		# row.append('MIwC')
		# row.append('operators')
		# row.append('time')
		# row.append('vocabulary')
		# row.append('volume')

		row.append('Has_Session')
		row.append('Session_Reads')
		row.append('Session_Writes')
		row.append('Cookies')
		row.append('Header_Access')

		row.append('Has_Param')
		row.append('Param_Reads')

		row.append('Context_Switches')

		row.append('DB_Query')
		row.append('DB_Query_Binary')

		row.append('Has_HTML')

		row.extend(html.header())
		
		row.append('Defect_Count')
		row.append('Defected')

		for x in reversed(ignore):
			row.pop(x)
		row.pop(0)
		writer.writerow(row)
	else:
		skip = False

		if row[0] == 'File' and common.check_path_valid(row[1]):
			
			path = row[1]
			parsed_path = parsed_dir+path[path.index("/", len(pwd)+1)+1:]
			print path+" "+parsed_path
			if (path.endswith(".php") or path.endswith(".module") or path.endswith(".inc") or path.endswith(".install")):
				# phpmetrics = complexity[path]
				# row.append(phpmetrics['bugs'])
				# row.append(phpmetrics['difficulty'])
				# row.append(phpmetrics['effort'])
				# row.append(phpmetrics['length'])
				# row.append(phpmetrics['maintainabilityIndex'])
				# row.append(phpmetrics['maintainabilityIndexWithoutComment'])
				# row.append(phpmetrics['operators'])
				# row.append(phpmetrics['time'])
				# row.append(phpmetrics['vocabulary'])
				# row.append(phpmetrics['volume'])

				root = eval_php.parse_php(parsed_path)
				if (root is not None):
					reads = eval_php.count_session_read(root)
					writes = eval_php.count_session_write(root)
					params = eval_php.count_request_param_access(root)
				else:
					reads = 0
					writes = 0
					params = 0
					continue;

				row.append(True if reads>0 or writes>0 else False)
				row.append(reads)
				row.append(writes)
				row.append(eval_php.count_cookie_access(root))
				row.append(eval_php.count_request_header_access(root))

				row.append(True if params>0 else False)
				row.append(params)

				row.append(eval_php.count_context_switch(root))

				db_query = eval_php.count_db_query(root)
				row.append(db_query)
				row.append(True if db_query>0 else False)

				content,parser = html.parse(root)

				# print "content : "+content

				if len(content)==0:
					row.append(False)
					#skip = True
				else:
					row.append(True)

				html_loc = html_loc + len(content.splitlines())
				row.extend(parser.data())
			else:
				#skip = True
				row.append(False)
				row.append(0)
				row.append(0)
				row.append(0)
				row.append(0)

				row.append(False)
				row.append(0)

				row.append(0)

				row.append(0)
				row.append(False)
				row.append(False)

				row.extend(html.empty())

			row.append(0)
			row.append('no')
			for x in reversed(ignore):
				row.pop(x)
			row.pop(0)
			if skip == False:
				# print '[%s]' % ', '.join(map(str, row))
				writer.writerow(row)
				print "HTML LOC "+str(html_loc)

ifile.close()
ofile.close()