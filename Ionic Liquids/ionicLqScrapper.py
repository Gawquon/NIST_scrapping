#NIST scrapper.
import time
import numpy as np
import pandas as pd
import molToMass as mTm
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

#End Imports-------------------------------------------------------

MASS_PERCENT = 'Mass fraction of 1-butyl-3-methylimidazolium bis(trifluoromethylsulfonyl)imide Liquid'
#End constant decleration------------------------------------------------------------------------------

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--disable-gpu')#windows only -- can delete otherwise
#This program requires that a chromedriver is installed and that the driver is in the PATH

#Structure to package data ---------------------------------------------------------
class prePandasContainer: #This struct was a terrible idea
	molecule = ""
	formula = ""
	data = None
	headings = None
#-------------------------------------------------------------------

#Begin functions ----------------------------------------------------------
"""This takes a string and returns it with all HTML tags (i.e </sub>) removed."""
def clean_str_HTML(html_string):
	h = html_string
	h=h.replace('/','')
	h=h.replace("<br>",'')
	h=h.replace("<sub>",'')
	h=h.replace("<sup>",'')
	return h

"""Returns the first string containing the substring if fetch = True. Otherwise it returns a bool that evalutes to true if the substring is present in any string in the list"""
def substr_in_list(sub,list,fetch=False):
	for s in list:
		if sub in s:
			if fetch:
				return s
			return True
	if fetch:
		return ''
	return False

"""Iteravely searches the NIST data avaiable at the set configuration and pulls only data that passed the filter

	desc """
def page_table_processing():
	tableList = driver.find_elements_by_class_name("dgrid-row")
	for table in tableList:
		table.click()
		time.sleep(1) #temporary fix could be optimized

		#currently set up for only binary mixtures
		formula1 = driver.find_element_by_xpath('//*[@id="dscomp_pane"]/table/tr[2]/td[3]')
		formula2 = driver.find_element_by_xpath('//*[@id="dscomp_pane"]/table/tr[3]/td[3]')

		f1 = clean_str_HTML(formula1.get_attribute('innerHTML'))
		f2 = clean_str_HTML(formula2.get_attribute('innerHTML')) 

		if (f1 in validSolvents or f2 in validSolvents)  and ((f1 == subjectSolute[0]) ^ (f2 == subjectSolute[0])):
			NIST_metadata.append(prePandasContainer())			
			if(f1 == subjectSolute[0]):
				NIST_metadata[-1].molecule = driver.find_element_by_xpath('//*[@id="dscomp_pane"]/table/tr[3]/td[2]').get_attribute('innerHTML')
				NIST_metadata[-1].formula = f2
			else:
				NIST_metadata[-1].molecule = driver.find_element_by_xpath('//*[@id="dscomp_pane"]/table/tr[2]/td[2]').get_attribute('innerHTML')
				NIST_metadata[-1].formula = f1
			NIST_metadata[-1].data = [[],[],[],[]] # hardcoded, may be okay
			NIST_metadata[-1].headings = []
		
			print(NIST_metadata[-1].molecule)

			#Grabs the headings for use in a pandas dataframe
			for col in dataTable.find_elements_by_css_selector('th'):
				NIST_metadata[-1].headings.append(col.get_attribute('innerHTML'))

			for i in range(0,4):	#currently brute forced should be more elegant
				NIST_metadata[-1].headings[i] = clean_str_HTML(NIST_metadata[-1].headings[i])

			for row in dataTable.find_elements_by_css_selector('tr'):
				i = 0
				for d in row.find_elements_by_css_selector('td'):
					NIST_metadata[-1].data[i].append(d.get_attribute('innerHTML'))
					i = (i + 1)

			NIST_metadata[-1].data = np.asarray(NIST_metadata[-1].data)
			NIST_metadata[-1].data = pd.DataFrame(NIST_metadata[-1].data)
			NIST_metadata[-1].data = NIST_metadata[-1].data.T
			NIST_metadata[-1].data.columns = NIST_metadata[-1].headings
	return
#function list end-------------------------------------------------------

#Temporary library of empirical formulas used in FIRST data
validSolvents = ['C2H3N', 'C4H7N', 'C6H8N2', 'CH4O', 'C2H6O', 'C4H10O', 'C8H18O', 'C3H8O3', 'CH4O', 'C2H4Cl2', 'C3H4O3', 'C4H6O3', 'C2H6OS', 'C3H7NO', 'C4H8O', 'C3H6O', 'C6H10O', 'C4H9NO']

#Empirical formula first, then name used ny NIST database
subjectSolute = ['C10H15F6N3O4S2', '1-butyl-3-methylimidazolium bis(trifluoromethylsulfonyl)imide']

#driver = webdriver.Chrome(r'D:\TT-RPG\Code\PythonScripts\NPCgen\chromedriver_win32\chromedriver.exe',chrome_options=options)# windows
driver = webdriver.Chrome('/mnt/d/TT-RPG/Code/PythonScripts/NPCgen/chromedriver_win32/chromedriver.exe',chrome_options=options) #linux
driver.get('https://ilthermo.boulder.nist.gov/')

try:
	driver.find_element_by_id("sbutton").click()

	#
	#
	#------------------------ configuration ------------------------
	## This should be the only place changes are needed for different data sets
	mol_property = "density" #Molecular property to search

	driver.find_element_by_id("cmp").send_keys("C10H15F6N3O4S2")#Desired Compound
	driver.find_element_by_id('ncmp').send_keys("2")#This is # of compounds in mix
	#"a" for any, "1" for pure compound, "2" for binary mixture and "3" for ternary

	#The next three terms are merely additional options to narrow your search
	driver.find_element_by_id("auth").send_keys("")#Author's last name
	driver.find_element_by_id("keyw").send_keys("")#Key words(i.e. viscosity)
	driver.find_element_by_id("year").send_keys("")#Year of publication

	time_to_timeout = 10 #in sec, can be increased for large queries if nessecary
	#------------------------- configuration -------------------------
	#
	#

	driver.find_element_by_id("prp").send_keys(mol_property)#Property measured in data
	driver.find_element_by_id("submbutt").click()#Submits search query

	#side note: This currently lacks error cathing for improper search entries in the year, author and keyword fields
	pageArrow = driver.find_element_by_xpath("//*[@id='dsgrid']/div[4]/div/div[2]/span[3]")

	#wait for search to complete - broken
	i = 0
	while i < time_to_timeout:
		time.sleep(1)
		i += 1
		if int(pageArrow.get_attribute("tabindex")) == -1:
			break
	else:
		print("Finished waiting for search")

	dataTable = driver.find_element_by_xpath('//*[@id="dsdata_pane"]/table[2]')
	
	NIST_metadata = []

	while int(pageArrow.get_attribute("tabindex")) != -1:
		page_table_processing()#brings data from NIST into a pandas dataframe
		time.sleep(3)
		pageArrow.click()#turns page

	page_table_processing()#needed to process last page
	driver.quit()

except Exception as e:
	print(e)
	driver.quit()
	
#after this the data munging gets UGLY note to future self - put ALL data into pandas DO NOT USE STRUCTS

for dataset in NIST_metadata:
	frac = substr_in_list("fraction",dataset.headings,fetch=True)
	prp = substr_in_list(mol_property[1:],dataset.headings,fetch=True)
	temp = substr_in_list('emperature',dataset.headings,fetch=True)
	pres = substr_in_list('ressure',dataset.headings,fetch=True)

	if not substr_in_list(subjectSolute[1],dataset.headings):
		dataset.data[frac] = 1 - dataset.data[frac].astype(float)
			
	if substr_in_list("Mol",dataset.headings):
		mTm.execute(dataset.data,subjectSolute[0],dataset.formula,frac)

	dataset.data = dataset.data[[frac,prp,temp,pres]]
	dataset.data.columns=[MASS_PERCENT,mol_property,"K","kPa"]

uniquemols = []
allmols = []
for dataset in NIST_metadata:
	allmols.append(dataset.molecule)
	if dataset.molecule not in uniquemols:
		uniquemols.append(dataset.molecule)

allmols = np.array(allmols)
sharedInd = []
for u in uniquemols:
	sharedInd.append(np.where(allmols == u)[0])

exportDf = []

for ii in sharedInd:
	tempDf = []
	for i in ii:
		tempDf.append(NIST_metadata[i].data)
	exportDf.append(pd.concat(tempDf))

for count in range(0, len(exportDf)):
	df = exportDf[count]
	df[MASS_PERCENT] = df[MASS_PERCENT].astype(float)
	df = df.sort_values(by=[MASS_PERCENT])
	df[mol_property] = df[mol_property].str.split(' ').str[0]
	df.to_csv(uniquemols[count] + ".csv")

#manually prune any undesired data sets that passed through the filter due to matching empirical formulas
#when done move to plotter.py