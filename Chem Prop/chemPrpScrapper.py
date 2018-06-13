import time
import warnings
import matplotlib as ml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
#from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import pandas as pd

### Function declarations
def clean_str_HTML(html_string):
	"""This takes a string and returns it with all HTML tags (i.e </sub>) removed."""
	h = html_string
	h=h.replace("<br>",'')	
	h=h.replace("<sub>",'')
	h=h.replace("<sup>",'')
	h=h.replace("</br>",'')
	h=h.replace("</sub>",'')
	h=h.replace("</sup>",'')
	return h

def substr_in_list(sub,list,fetch=False):
	"""Returns the first string containing the substring if fetch = True. Otherwise it returns a bool that evalutes to true if the substring is present in any string in the list"""
	for s in list:
		if sub in s:
			if fetch:
				return s
			return True
	if fetch:
		return ''
	return False

def scrapeplot_isot(compound,temperature=298,pressure_min=0.05,pressure_max=0.2,y_property='Pressure',x_property='Volume',saveto=''):
	"""Plots two properties against each other at an isothermal condition for a comp contained in the NIST chemistry webbook. T in Kelvin, pressure in MPa."""

	### NOTE: Config settings
	# This program requires that a chromedriver is installed and that the driver is in the PATH
	comp = compound #compound of intrest as it appears in the NIST menu
	T = temperature #T in Kelvin you want to look at
	p_min = pressure_min #MPa minimum pressure to look at
	p_max = pressure_max #MPa maximum pressure to look at
	x_prp = x_property #property wanted on the x-axis as listed in NIST
	y_prp = y_property #property wanted on the y-axis as listed in NIST
	driver_path = '.../chromedriver.exe'
	###

	try:
		### Driver setup
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		options.add_argument('--disable-gpu') #windows only -- can delete otherwise
		#This program requires that a chromedriver is installed and that the driver is in the PATH

		driver = webdriver.Chrome(driver_path,chrome_options=options) #linux
		driver.get('https://webbook.nist.gov/chemistry/fluid/')
		###

		### First Page
		driver.find_element_by_xpath('//*[@id="ID"]').send_keys(comp) #Molecule selector ID
		driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[5]/input[1]').click()
		###
		time.sleep(3) # Should eventualy be replaced with a proper wait method
		### Second Page
		driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[1]/input').send_keys(str(T)) # T input
		driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[2]/table/tbody/tr[1]/td[1]/input').send_keys(str(p_min)) # PLow input
		driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[2]/table/tbody/tr[2]/td[1]/input').send_keys(str(p_max)) # PHigh input
		driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[3]/input').click() # checkbox
		driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[5]/input[1]').click()
		###
		time.sleep(3)
		### Third Page
		table = driver.find_element_by_xpath('//*[@id="main"]/table[1]/tbody') # table
		###
		### 

		# Loads the headers into an array and finds the index in array of selected properties
		# while taking into account inexact matches between the NIST term and supplied string
		headers = []
		for col in table.find_elements_by_css_selector('th'):
			headers.append(clean_str_HTML(col.get_attribute('innerHTML')))

		x_index = headers.index(substr_in_list(x_prp[1:],headers,fetch=True))
		y_index = headers.index(substr_in_list(y_prp[1:],headers,fetch=True))

		# Prepares and populates a 2d python array to be filled with as many data points as available
		# this is for ease of data entry in a structure that can also be easiy cast to a pandas df
		df_scaffold = []
		df_scaffold.append([])
		df_scaffold.append([])

		for row in table.find_elements_by_css_selector('tr'):
			d = row.find_elements_by_css_selector('td')
			if(d != []):
				df_scaffold[0].append(clean_str_HTML(d[x_index].get_attribute('innerHTML')))
				df_scaffold[1].append(clean_str_HTML(d[y_index].get_attribute('innerHTML')))

		driver.quit()

	except Exception as e:
		print(e)
		driver.quit()

	# Builds and prepares pandas df for plotting
	df = pd.DataFrame(df_scaffold).T
	df.columns = [headers[x_index], headers[y_index]]
	df = df.convert_objects(convert_numeric=True,)

	# Plots figure and saves as pdf to current directory or specified location 
	ml.use("Agg")
	df.plot.scatter(x=headers[x_index],y=headers[y_index],title=comp + " at " + str(T) + "K",s=15)
	if saveto != '':
		saveto += '/'
	ml.pyplot.savefig(saveto + comp.lower()+ '.pdf')
	###