import csv
from os import listdir
from os.path import isfile, join
import sys
from lxml import html
import requests
from lxml import etree
import re

# Constants
data_path = "init_data"
microservice_keywords = ["micro-service" , "microservice" , "microservice-oriented" , "micro-service-oriented"]
keywords = ["monolith" , "monolithic" , "legacy" , "reverse" , "redevelopment" , "redeveloping" , "redevelop" , "refactor" , "refactoring",
"refactorization" , "refactorisation" , "reengineering" , "reengineer" , "restructure" , "restructuring" , "re-engineering" , "re-structuring",
"modernize" , "modernizing" , "modernization" , "migrating" , "migration" , "migrate" , "decomposing" , "decompose" , "transforming",
"transform" , "transformation" , "extraction" , "extracting" , "extract" , "identification" , "identifying" , "moving" , "move" ,
"re-architecture" , "re-architecturing", "rearchitecture" , "rearchitecturing" , "rewriting" , "re-writing" , "rewrite" , "re-write"]

# Settings
verbose = False

# Functions
def verbosity_print(string):
	if verbose:
		print(string)

# Fetching all the csv files that contain the article informations
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
print(onlyfiles)

# Fetching the papers, filtering and extracted.
print("Opening CSV files.")
final_papers = []
for filename in onlyfiles:
	with open(data_path+'/'+filename, 'rb') as csvfile:
		print("---------------------------")
		print("Analysing "+ filename)
		count = 0
		init_papers = []
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		for row in reader:
			#print(row[0])
			init_papers.append(row)
		
		inter_papers = []
		# checking that microservice keywords are present
		for element in init_papers:
			lower_ele = str.lower(element[0])
			for keyword in microservice_keywords:
				test = False
				if keyword in lower_ele:
					inter_papers.append(element)
					break

		# checking that migration keywords are present
		for element in inter_papers:
			verbosity_print("Checking for keywords in: " + element[0])
			lower_ele = str.lower(element[0])
			for keyword in keywords:
				test = False
				if keyword in lower_ele:
					final_papers.append(element)
					verbosity_print("adding : " + element[0])
					count = count + 1
					break
		print("Total number of papers: " + str(count))
print("----------------------------")

# Writing down the extracted documents
myfile = open("./final_data/final_cut.csv", 'wb')
wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
for element in final_papers:
	wr.writerow(element)

# Summary: Paper names and total count of papers extracted.
print("Final cut")
for element in final_papers:
	print(element[0])
print("Number of documents found: " + str(len(final_papers)))

# element[15]
# https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8354415
# https://ieeexplore.ieee.org/xpl/dwnldReferences?arnumber=8354415

IEEE_links = []
for element in final_papers:
	if len(element)>15 and ("https://ieeexplore.ieee.org/stamp/stamp.jsp?" in element[15]):
		#print("ieeexplore article number: "+ element[15].split('?arnumber=', -1)[1])
		url = "https://ieeexplore.ieee.org/xpl/dwnldReferences?arnumber=" + element[15].split('?arnumber=', -1)[1]
		print(url)
		page = requests.get(url)
		#page.text = page.text.replace("</br>","</fk>")
		#print(page.text)
		tree = html.fromstring(page.content)
		#print(etree.tostring(tree, pretty_print=True))
		references = tree.xpath('//body/text()')
		references = references[0].encode('utf-8').replace("\t","").rstrip().split("\n\n\n\n")
		print(len(references))
		text_file = open("IEEEreferences.txt", "a")
		for elmt in references:
			print(re.match("\"(.*?)\"",elmt.replace("\n ", ""),0))
			text_file.write(url)
			text_file.write(elmt.replace("\n ", "") + "\n")
			#text_file.write("##############################################################################################################")
		text_file.close()
		

#//body/text()[following-sibling::br]
#.split('\n\n\n')[0]
