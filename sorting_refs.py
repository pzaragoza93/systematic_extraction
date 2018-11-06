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
verbose   = False
SAVE_IEEE = False
filename = "./init_data/IEEEreferences_title.txt"

# Functions
def verbosity_print(string):
	if verbose:
		print(string)

content = []
with open(filename) as f:
    content = f.readlines()

content = [x.strip() for x in content] 
inter_papers = []
final_papers = []

# checking that microservice keywords are present
for element in content:
	lower_ele = str.lower(element)
	for keyword in microservice_keywords:
		test = False
		if keyword in lower_ele:
			inter_papers.append(element)
			break

print(len(inter_papers))
# checking that migration keywords are present
count = 0
for element in inter_papers:
	verbosity_print("Checking for keywords in: " + element)
	lower_ele = str.lower(element)
	for keyword in keywords:
		test = False
		if keyword in lower_ele:
			final_papers.append(element)
			print("Adding : " + element)
			count = count + 1
			break

print("Total number of papers: " + str(len(final_papers)) + " out of " + str(len(content) ))