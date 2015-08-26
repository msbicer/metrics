import csv
import sys
import common
import os
import subprocess
import json
import eval_php
import html

project_name = sys.argv[1]
parsed_dir1 = sys.argv[2]
parsed_dir2 = sys.argv[3]

pwd = os.getcwd()
print pwd

with open(project_name+"-modified.txt") as f:
    for line in f:
    	parsed_path1 = pwd+"/"+parsed_dir1+line
    	parsed_path2 = pwd+"/"+parsed_dir2+line
    	print parsed_path1+" "+parsed_path2

    	if os.path.isfile(parsed_path1) and os.path.isfile(parsed_path2):
    		root1 = eval_php.parse_php(parsed_path1)
    		content1,parser1 = html.parse(root1)

    		root2 = eval_php.parse_php(parsed_path2)
    		content2,parser2 = html.parse(root2)

	    	if content1 == content2:
	    		print "===> "+line
	    	else:
	    		print "HTML : "+content1
