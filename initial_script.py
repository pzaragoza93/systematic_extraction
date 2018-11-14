import csv
from os import listdir
from os.path import isfile, join
import sys
from lxml import html
import requests
from lxml import etree
import re
from lxml.etree import tostring

# Constants
data_path = "init_data"
acm_html_data_path = "acm_html"
isi_html_data_path = "ISI_html"
microservice_keywords = ["micro-service" , "microservice" , "microservice-oriented" , "micro-service-oriented"]
keywords = ["monolith" , "monolithic" , "legacy" , "reverse" , "redevelopment" , "redeveloping" , "redevelop" , "refactor" , "refactoring",
"refactorization" , "refactorisation" , "reengineering" , "reengineer" , "restructure" , "restructuring" , "re-engineering" , "re-structuring",
"modernize" , "modernizing" , "modernization" , "migrating" , "migration" , "migrate" , "decomposing" , "decompose" , "transforming",
"transform" , "transformation" , "extraction" , "extracting" , "extract" , "identification" , "identifying" , "moving" , "move" ,
"re-architecture" , "re-architecturing", "rearchitecture" , "rearchitecturing" , "rewriting" , "re-writing" , "rewrite" , "re-write"]

################### Settings ###################
verbose			= False
# Scraping and saving references extracted from the initial filtered databases
FETCH_IEEE		= False
SAVE_IEEE		= False # /xpl/dwnldReferences is not disallowed on the robots.txt list therefore is may be used.
FETCH_ACM		= True
SAVE_ACM		= True # must be set to false because ACM does not allow scrapping: User-agent: * Disallow: /
FETCH_Springer	= False # User-agent: * Allow: /chapter/
SAVE_Springer	= True  
FETCH_ISI		= False
SAVE_ISI		= True # must be set to false because ACM does not allow scrapping: User-agent: * Disallow: /


# Functions
def verbosity_print(string):
	if verbose:
		print(string)

# Fetching all the csv files that contain the article informations
onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
verbosity_print(onlyfiles)

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
		if (str(filename) == "SPRINGERreferences.txt"):
			reader = csv.reader(csvfile, delimiter='|', quotechar='|')
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
					element.append(filename)
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
	verbosity_print(element[0])
print("Number of documents found: " + str(len(final_papers)))

##########################################################
###					Extracting references			   ###
##########################################################

##########  IEEE extraction  ##########
IEEE_links = []
for element in final_papers:
	if len(element)>15 and ("https://ieeexplore.ieee.org/stamp/stamp.jsp?" in element[15]) and FETCH_IEEE:
		# /xpl/dwnldReferences is not disallowed on the robots.txt list.
		url = "https://ieeexplore.ieee.org/xpl/dwnldReferences?arnumber=" + element[15].split('?arnumber=', -1)[1]
		print(url)
		page = requests.get(url)
		tree = html.fromstring(page.content)
		references = tree.xpath('//body/text()')
		references = references[0].encode('utf-8').replace("\t","").rstrip().split("\n\n\n\n")
		print(len(references))
		if(SAVE_IEEE):
			text_file = open("IEEEreferences.txt", 'w')
			for elmt in references:
				text_file.write(url)
				text_file.write(elmt.replace("\n ", "") + "\n")
			text_file.close()



##########  ACM extraction  ##########
ACM_links = []
text_file = open("./init_data/ACMreferences.txt", 'w')
for element in final_papers:
	if len(element)>2 and  ("ACM" in element[len(element)-1] and FETCH_ACM):
		url = "https://dl.acm.org/citation.cfm?id=" + str(element[1]) + "&preflayout=flat"
		#print(url)
		#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		#page = requests.get(url,  headers=headers)
		#tree = html.fromstring(page.content)
		#print page.text
		#references = tree.xpath('//html/body/div/div/div/table[1]/tbody/tr/td[3]')
		#print(references[0])
		#break
html_pages = [f for f in listdir(acm_html_data_path) if isfile(join(acm_html_data_path, f))]
for filename in html_pages:
	with open(acm_html_data_path+'/'+filename, 'rb') as html_file:
		page = html_file.read().split('<div class="abstract">\n1', 1)[-1].split('</table>',1)[0]	# cutting out everything but the table
		rfs = re.findall(r"<div>(.*?)</div>", page.replace('\n', ''))							 	# finding all the references
		if len(rfs):
			if(SAVE_ACM):
				for r in rfs:
					if "<a href" in r:
						text_file.write(r.split(">", 1)[-1] + "\n")	# cutting out the href link at the beginning of the reference
					else:
						text_file.write(r + "\n")
		#references = tree.xpath('/html/body/div/div/div/table/tr')
text_file.close()
			

##########  Springer extraction  ##########
Springer_link = []
text_file = ""
if(FETCH_Springer and SAVE_Springer):
	text_file = open("./init_data/SPRINGERreferences.txt", 'w')
for element in final_papers:
	if len(element)>10 and  (("link.springer.com" in element[8]) or ("link.springer.com" in element[10])) and FETCH_Springer:
		
		# finding position of url
		pos = 8
		if("link.springer.com" in element[10]):
			pos = 10
		url = element[pos].replace("http://","https://").replace('"',"")
		print url
		page = requests.get(url)
		tree = html.fromstring(page.content)
		references = tree.xpath('//body/div/main/div/div/article/div/section[@id="Bib1"]/div/ol/li/div[2]')
		if(SAVE_Springer):
			#text_file.write(url)
			for elmt in references:
				text_file.write(elmt.text.encode('utf-8') + "\n")
if(FETCH_Springer and SAVE_Springer):
	text_file.close()

##########  ISI Web of Knowledge extraction  ##########
ISI_web = []
text_file = open("./init_data/ISIWEBreferences.txt", 'w')
html_pages = [f for f in listdir(isi_html_data_path) if isfile(join(isi_html_data_path, f))]
for filename in html_pages:
	with open(isi_html_data_path+'/'+filename, 'rb') as html_file:
		page = html_file.read()	# cutting out everything but the table
		# rfs = re.findall(r"<div>(.*?)</div>", page.replace('\n', ''))	
		rfs = re.findall(r'<value lang_id="">(.*?)</value>', page.replace('\n', ''))	# finding all the references
		if len(rfs):
			if(SAVE_ISI):
				for r in rfs:
					text_file.write(r + "\n")
text_file.close()

#http://apps.webofknowledge.com/full_record.do?product=WOS&search_mode=GeneralSearch&qid=1&SID=D36wenRGCrOeiGyRS7Z&page=1&doc=1
#http://apps.webofknowledge.com/summary.do?product=WOS&parentProduct=WOS&search_mode=CitedRefList&parentQid=1&parentDoc=1&qid=2&SID=D36wenRGCrOeiGyRS7Z&colName=WOS&page=1

