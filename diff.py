from git import *
import time
import sys

project_name = sys.argv[1]
from_commit = sys.argv[2]
to_commit = sys.argv[3]
repo_path = sys.argv[4]

commit_cache = {}
log_cache = {}
changed_files = {}

def is_bugfix(commit, comment):
	if commit is None:
		return False
	comment = comment.lower()
	if ('bug' in comment) or ('error' in comment) or ('fix' in comment) or ('fail' in comment) or ('minor' in comment):
		return True
	else:
		return False

def show(commit):
	filename = None
	skip = False
	if commit in commit_cache:
		return
	else:
		commit_cache[commit] = 1

	try:
		output = git.show(commit)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		return
	
	comments = []
	in_diff_section = False
	in_comment_section = False
	for line in output.split('\n'):
		#we reached new file in commit
		if line.startswith('---') or line.startswith('+++'):
			if line.startswith('---'):
				#reset skip flag
				if skip is False and filename is not None:
					if is_bugfix(commit, comment_string):
						changed_files[filename] = 1
						print comment_string+" "+filename
				skip = False
				#reset counters
				
			if line.startswith('+++') and '/dev/null' in line:
				#appropriately set skip flag
				skip = True
			else:
				if len(line.split())>1:
				    filename = line.split()[1]
				    filename = filename[filename.find('/')+1:]
		elif not in_diff_section:
			if line.startswith('diff'):
				in_diff_section = True
				comment_string = ' '.join(comments)
			elif line.startswith('Date:'):
				in_comment_section = True
			elif in_comment_section:
				comments.append(line)

def log(fr, to):
    key = fr+'..'+to
    if key in log_cache:
        print 'log : '+key
        return
    else:
        log_cache[key] = 1

    try:
    	output =  git.log('--date=raw','--pretty=medium',fr+'..'+to)
    except:
    	return
    commit = None
    mrg = None
    for line in output.split('\n'):
        if line.startswith('commit '):#entered commit detail body
            if commit is not None:
            	show(commit)
            commit = line.split()[1]
            mrg = None
        elif line.startswith('Merge:'):
            commit = None
            mrg = line.split()
            #print 'mrg : ',mrg[1],mrg[2],str(len(mrg))
            log(mrg[1],mrg[2])

repo = Repo(repo_path)
git = repo.git

#Id,Change_Date,Committer,File_Name,Lines_Added,Lines_Removed
#git log --pretty=medium 23c2be3d329d98a5750f5d5c50135a63858836cd..2e47d2edd45080c046bc32dd2ca5c64f31086366
#log('23c2be3d329d98a5750f5d5c50135a63858836cd','2e47d2edd45080c046bc32dd2ca5c64f31086366')
#log('c3ebdbf9cceddb82cd2089aaef8c7b992e536363','2e47d2edd45080c046bc32dd2ca5c64f31086366')
log(from_commit, to_commit)

modified_file  = open(project_name+'-modified.txt', "wb")
for filename in changed_files:
	modified_file.write(filename+'\n')
modified_file.close()