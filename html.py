import eval_php
import os
from sets import Set
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    total_tags = 0
    tags = Set()

    forms = 0
    inputs = 0
    anchors = 0
    frames = 0

    scripts = 0
    external_scripts = 0
    in_page_scripts = 0

    css_included = 0
    style_tags = 0
    inline_css = 0
    inline_css_lines = 0
    
    total_attrs = 0
    avg_attrs = 0
    attrs = Set()
    
    max_depth = 0
    total_depth = 0
    avg_depth = 0

    total_comment = 0
    total_text = 0

    depth = 0

    def tag_opened(self, tag, attrs):
        self.depth+=1
        self.total_depth += self.depth
        if self.depth>self.max_depth:
            self.max_depth = self.depth

        self.tags.add(tag)
        self.total_tags += 1

        self.total_attrs += len(attrs)

        if tag == "input":
            self.inputs += 1
        elif tag == "form":
            self.forms += 1
        elif tag == "iframe" or tag == "frame":
            self.frames += 1
        elif tag == "a":
            self.anchors += 1
        elif tag == "script":
            self.scripts += 1
        elif tag == "style":
            self.style_tags += 1


        for a in attrs:
            # print "attr : ",a
            name = a[0].lower()
            if name == "<" or name == ">":
                pass
                
            value = "" if a[1] == None else a[1].lower()
            self.attrs.add(name)
            if name == "style" and len(value)>0:
                self.inline_css += 1
                self.inline_css_lines += len(value.split(";"))
            elif tag == "link" and name == "rel" and value == "stylesheet":
                self.css_included += 1
            elif tag == "script":
                if name == "src":
                    self.external_scripts += 1
                else:
                    self.in_page_scripts += 1 


    def handle_starttag(self, tag, attrs):
        self.tag_opened(tag.lower(), attrs)
        #print "Encountered a start tag:", tag, attrs
    def handle_startendtag(self, tag, attrs):
        self.tag_opened(tag.lower(), attrs)
        # self.depth=max(0,self.depth-1)
        self.depth-=1
        #print "Encountered a startend tag:", tag, attrs
    def handle_comment(self, data):
        self.total_comment += 1
    def handle_endtag(self, tag):
        # self.depth=max(0,self.depth-1)
        self.depth-=1
        #print "Encountered an end tag :", tag
    def handle_data(self, data):
        self.total_text+=1
        # print "Encountered data :", data
        pass
    def finalize(self):
        self.avg_attrs = 0 if self.total_attrs==0 else self.total_tags / float(self.total_attrs)
        self.avg_depth = 0 if self.total_depth==0 else self.total_tags / float(self.total_depth)
    def data(self):
        return (self.total_tags,len(self.tags),self.total_attrs,len(self.attrs)
            ,self.avg_attrs,self.max_depth,self.total_depth,self.avg_depth,self.total_comment,self.total_text
            ,self.forms, self.inputs, self.anchors, self.frames, self.scripts, self.in_page_scripts, self.external_scripts
            ,self.css_included, self.style_tags, self.inline_css, self.inline_css_lines)


# def read_file(file_path):
# 	with open (file_path, "r") as myfile:
# 	    data=myfile.read().replace('\n', '')
# 	# data = removeComments(data)
# 	return data

def header():
    return ('total_tags','unique_tags','total_attrs','unique_attrs'
            ,'avg_attrs','max_depth','total_depth','avg_depth','total_comment','total_text'
            ,'forms','inputs','anchors','frames','scripts','in_page_scripts','external_scripts'
            ,'css_included','style_tags','inline_css','inline_css_lines')

def empty():
    return [0] * len(header())

def parse(root):
    content = eval_php.get_html(root)
    parser = MyHTMLParser()
    parser.feed(content)
    parser.finalize()

    return content,parser

# parser = MyHTMLParser()

# in_file = '/Users/sbicer/Desktop/akademik/phpmyadmin/phpmyadmin-git/db_structure.php' #sys.argv[1]
# pwd = os.getcwd()
# parsed_dir = '/Users/sbicer/Desktop/akademik/phpmyadmin/php-ast/'
# parsed_path = parsed_dir+in_file[in_file.index("/", len(pwd)+1)+1:]
# #content = read_file(in_file)

# root = eval_php.parse_php(parsed_path)
# content = eval_php.get_html(root)
# parser.feed(content)

# parser.finalize()

# print header()
# print parser.data()

def test():
    php_from = []
    php_to = []
    in_string = False
    in_php = False
    in_comment = False
    string_begin_ch = None
    escaping = False
    idx = 0
    while idx < len(content):
        ch = content[idx]
        if ch == "\\":
            escaping = not escaping
        if escaping:
            idx+=1
            pass
        if ch == "\"" or ch == "'" and in_comment == False:
            if in_string == False:
                in_string = True
                string_begin_ch = ch
            elif in_string == True and string_begin_ch == ch:
                in_string = False
                string_begin_ch = None
        elif not in_php or in_string == False:
            if ch == "/":
                if content[idx+1] == "/":
                    ln = content.find("\n",idx)
                    if ln != -1:
                        content = content[:idx] + content[ln+1:]
                elif content[idx+1] == "*":
                    in_comment = True
                    idx+=1
                elif content[idx-1] == "*" and in_comment == True:
                    in_comment = False
            elif not in_comment:
                if ch == "<" or ch == "?":
                    print str(idx)+" "+str(in_string)+" "+content[idx-5:idx+5]+"\n"

                if ch == "<" and content[idx+1] == "?":
                    if content[idx+2].isspace() or content[idx+2:idx+5] == "php":
                        in_php = True
                        php_from.append(idx)
                elif ch == "?" and content[idx+1] == ">" and in_php:
                    in_php = False
                    php_to.append(idx+1)
        idx+=1

    i = len(php_from)-1
    while i >= 0:
        print str(i)+" "+str(len(content))+" "+str(php_from[i])+" "+str(php_to[i])
        content = content[0:php_from[i]] + content[php_to[i]:]
        i-=1
    print content