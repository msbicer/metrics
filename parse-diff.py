import sys

project_name = sys.argv[1]

ofile  = open(project_name+'-modified.txt', "wb")
with open(project_name+"-diff.txt") as f:
    for line in f:
        if line.startswith('Files '):
            filename = line.split()[1]
            if (filename.endswith('.php') or filename.endswith('.js') or filename.endswith('.html') or filename.endswith('.css') or filename.endswith('.xml')) and (not "Tests" in filename):
                ofile.write(filename+'\n')
ofile.close()