import fnmatch
import os
import csv
import sys

project_name = sys.argv[1]
base_dir = sys.argv[2]

def check_path_valid(file_path):
	if (('Tests/' not in file_path) and (file_path.endswith('.php') or file_path.endswith('.js') or file_path.endswith('.html') or file_path.endswith('.css') or file_path.endswith('.xml'))):
		return True
	else:
		return False

def extract_metrics(matrix):

	nrCommits = 0
	nrCommitters = 0
	nrLinesAdd = 0
	nrLinesRemove = 0
	nrCommitsLast = 0
	nrCommittersLast = 0
	nrLinesAddLast = 0
	nrLinesRemoveLast = 0
	giniCoeff = 0
	topCommitterPercent = 0

	nrCommits = len(matrix)
	localCommitters = {}
	lastCommitters = {}
	top = 0
	for row in matrix:
		date = int(row[1])
		author = row[2]
		file_path = base_dir+row[3]

		lines_added = int(row[4])
		lines_removed = int(row[5])

		nrLinesAdd += lines_added
		nrLinesRemove += lines_removed

		if author in localCommitters:
			localCommitters[author] = localCommitters[author]+1
		else:
			localCommitters[author] = 1

		
		for idx, item in enumerate(topCommitters):
			if (idx<=len(topCommitters)/10):
				if item[0] == author:
					top+=1
					break
			else:
				break

		if (date>=lastCommitTime-MONTH):
			if author in lastCommitters:
				lastCommitters[author] = lastCommitters[author]+1
			else:
				lastCommitters[author] = 1
			nrCommitsLast+=1
			nrLinesAddLast+=lines_added
			nrLinesRemoveLast+=lines_removed

	nrCommittersLast = len(lastCommitters)
	nrCommitters = len(localCommitters)
	giniCoeff = float(delta)/((nrCommits/nrCommitters)*(totalCommits*totalCommits))
	topCommitterPercent = float(top)/nrCommitters
	return [nrCommits,nrCommitters,nrLinesAdd,nrLinesRemove,nrCommitsLast,nrCommittersLast,nrLinesAddLast,nrLinesRemoveLast,giniCoeff,topCommitterPercent]


files = []
for root, dirnames, filenames in os.walk(base_dir):
	for file_path in filenames:
		full_path = os.path.join(root, file_path)
		if check_path_valid(full_path):
			files.append(full_path)

changes = {}
committers = {}

totalCommits = 0
delta = 0
topCommitters = []

sequence = 0
lastCommitTime = 0

MONTH = 60*60*24*30

ifile  = open(project_name+'-changes.csv', "rb")
reader = csv.reader(ifile)
ofile  = open(project_name+'-churn.csv', "wb")
writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

#Id,Change_Date,Committer,File_Name,Lines_Added,Lines_Removed
for idx, row in enumerate(reader):
	if idx>0:
		date = int(row[1])
		author = row[2]
		file_path = base_dir+row[3]
		#print 'enumerate ',file_path
		lines_added = int(row[4])
		lines_removed = int(row[5])
		lastCommitTime = max(lastCommitTime, date)
		if author in committers:
			committers[author] = committers[author]+1
		else:
			committers[author] = 1
		if check_path_valid(file_path):
			totalCommits+=1
			matrix = []
			if file_path in changes:
				matrix = changes[file_path]
			matrix.append(row)
			changes[file_path] = matrix
avgCommit = float(totalCommits) / len(committers)
topCommitters = sorted(committers.items(), key=lambda x: x[1])
for item in topCommitters:
	count = item[1]
	delta += abs(count - avgCommit)

writer.writerow(['File_Name','Commit_Count','Committer_Count','Lines_Added','Lines_Removed','Last_Commit_Count','Last_Commiter_Count','Last_Lines_Added','Last_Lines_Removed','Gini_Coefficient','Top_Committer_Percent','Defected'])
for name in files:
	if name in changes:
		#print name+" "+str(changes[name])
		metrics = extract_metrics(changes[name])
		metrics.insert(0, name)
		metrics.append('No')
		writer.writerow(metrics)
ifile.close()
ofile.close()