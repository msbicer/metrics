#from xml.dom import minidom
import sys
import xml.etree.ElementTree as ET

def count_request_param_access(root):
	global ns_node,ns_subnode,ns_scalar
	total = 0

	params = ["_POST","_GET","_REQUEST"]

	query = './/{0}Expr_Variable/{1}name'.format(ns_node, ns_subnode)
	total += count_param_occurrence(root.findall(query), params)

	return total

def count_session_write(root):
	global ns_node,ns_subnode,ns_scalar
	total = 0

	query = './/{0}Expr_Assign/{1}var'.format(ns_node, ns_subnode)
	total += count_param_occurrence(root.findall(query),"_SESSION")

	query = './/{0}Stmt_Unset'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_PostInc'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_PostDec'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_PreInc'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_PreDec'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	return total

def count_session_read(root):
	global ns_node,ns_subnode,ns_scalar
	total = 0

	query = './/{0}Expr_Assign/{1}expr'.format(ns_node, ns_subnode)
	total += count_param_occurrence(root.findall(query),"_SESSION")

	query = './/{0}Stmt_Echo'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_Empty'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_Isset'.format(ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}Expr_FuncCall/{1}args//{1}value'.format(ns_node, ns_subnode)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}cond/{1}Expr_ArrayDimFetch'.format(ns_subnode, ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")	

	query = './/{0}cond//{0}left/{1}Expr_ArrayDimFetch'.format(ns_subnode, ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	query = './/{0}cond//{0}right/{1}Expr_ArrayDimFetch'.format(ns_subnode, ns_node)
	total += count_param_occurrence(root.findall(query), "_SESSION")

	return total

def count_param_occurrence(haystack, needle):

	total = 0
	for e in haystack:
		text = ET.tostring(e) 
		if (isinstance(needle, list)):
			if (any(x in text for x in needle)):
				print text
				total+=1
		else:
			if ((text and needle in text)):
				print text
				total+=1
	return total

def parse_php(input_file):
	try:
		doc = ET.ElementTree(file=input_file)
		return doc
	except ET.ParseError:
		print "PARSE ERROR : "+input_file
		return None
	

ns_node = "{http://nikic.github.com/PHPParser/XML/node}"
ns_scalar = "{http://nikic.github.com/PHPParser/XML/scalar}"
ns_subnode = "{http://nikic.github.com/PHPParser/XML/subNode}"

if __name__ == '__main__':
	input_file = sys.argv[1]

	doc = ET.ElementTree(file=input_file)
	#parent_map = dict((c, p) for p in doc.getiterator() for c in p)

	#num_write_session = count_session_write(doc)
	#num_read_session = count_session_read(doc)
	num_params = count_request_param_access(doc)

	#print "write : "+str(num_write_session)
	#print "read : "+str(num_read_session)
	print "params : "+str(num_params)
	
