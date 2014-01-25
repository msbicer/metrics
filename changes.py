from git import *
import csv
import time
import sys

project_name = sys.argv[1]
from_commit = sys.argv[2]
to_commit = sys.argv[3]
repo_path = sys.argv[4]

commit_cache = {}

def show(commit):
	global git
	filename = None
	skip = False
	if commit in commit_cache:
		return []
	else:
		commit_cache[commit] = 1
	try:
		output = git.show(commit)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		return []
	lines_added = 0
	lines_removed = 0
	result = []
	for line in output.split('\n'):
		#we reached new file in commit
		if line.startswith('---') or line.startswith('+++'):
			if line.startswith('---'):
				#reset skip flag
				if skip is False and filename is not None:
					modification = [filename, lines_added, lines_removed]
					result.append(modification)
				skip = False
				#reset counters
				lines_added = 0
				lines_removed = 0
			if '/dev/null' in line:
				#appropriately set skip flag
				skip = True
			else:
				if len(line.split())>1:
				    filename = line.split()[1]
				    filename = filename[filename.find('/')+1:]
		elif skip is False:
			if line.startswith('+'):
				lines_added+=1
			elif line.startswith('-'):
				lines_removed+=1
	return result

def log(fr, to):
    global git
    try:
    	output =  git.log('--date=raw','--pretty=medium',fr+'..'+to)
    except:
    	return
    commit = None
    mrg = None
    author = None
    date = None
    for line in output.split('\n'):
        if line.startswith('commit '):#entered commit detail body
            if commit is not None:
            	result = show(commit)
            	for modification in result:
            		writer.writerow([commit,date,author, modification[0], modification[1], modification[2]])
            commit = line.split()[1]
            mrg = None
        elif line.startswith('Merge:'):
            commit = None
            mrg = line.split()
            #print 'mrg : ',mrg[1],mrg[2],str(len(mrg))
            log(mrg[1],mrg[2])
        elif mrg is None:
        	if line.startswith('Author:'):
        		author = line.split()
        		author = author[len(author)-1]
        	elif line.startswith('Date:'):
        		date = line[5:].strip().split()[0]
        		print commit+" "+time.ctime(int(date))
        		#Date:   Tue Dec 3 15:52:22 2013 +0100

repo = Repo(repo_path)
git = repo.git

ofile  = open(project_name+'-changes.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

writer.writerow(['Id','Change_Date','Committer','File_Name','Lines_Added','Lines_Removed'])
#Id,Change_Date,Committer,File_Name,Lines_Added,Lines_Removed
#git log --pretty=medium 23c2be3d329d98a5750f5d5c50135a63858836cd..2e47d2edd45080c046bc32dd2ca5c64f31086366
#log('23c2be3d329d98a5750f5d5c50135a63858836cd','2e47d2edd45080c046bc32dd2ca5c64f31086366')
#log('c3ebdbf9cceddb82cd2089aaef8c7b992e536363','2e47d2edd45080c046bc32dd2ca5c64f31086366')
log(from_commit, to_commit)
