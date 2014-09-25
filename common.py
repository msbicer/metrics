def check_path_valid(path):
	file_path = path.lower()
	if (('tests/' not in file_path and 'test/' not in file_path and 'testsuite/' not in file_path and 'documentation/' not in file_path and 'demos/' not in file_path) and (file_path.endswith('.php') #or file_path.endswith('.js') or file_path.endswith('.html') or file_path.endswith('.css') or file_path.endswith('.xml') or file_path.endswith('.java')
		)):
		return True
	else:
		return False