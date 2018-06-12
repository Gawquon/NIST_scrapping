import time
import numpy as np
import pandas as pd
import matplotlib as ml
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

### NOTE: Config settings
# This program requires that a chromedriver is installed and that the driver is in the PATH
compound = 'butane' #compound of intrest as it appears in the NIST menu
temperature = 375 #T in Kelvin you want to look at
pressure_min = 0.08 #MPa minimum pressure to look at
pressure_max = 0.12 #MPa maximum pressure to look at
x_property = 'Density' # property wanted on the x-axis as listed in NIST
y_property = 'Pressure' # property wanted on the y-axis as listed in NIST
###

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

try:
	### Driver setup
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('--disable-gpu') #windows only -- can delete otherwise
	#This program requires that a chromedriver is installed and that the driver is in the PATH

	driver = webdriver.Chrome('.../chromedriver.exe',chrome_options=options) #linux
	driver.get('https://webbook.nist.gov/chemistry/fluid/')
	###

	### First Page
	driver.find_element_by_xpath('//*[@id="ID"]').send_keys(compound) #Molecule selector ID
	driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[5]/input[1]').click()
	#driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[2]/div/table/tbody/tr[6]/td/fieldset/label[3]/input').click()
	###
	time.sleep(3) # Should eventualy be replaced with a proper wait method
	### Second Page
	driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[1]/input').send_keys(str(temperature)) # T input
	driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[2]/table/tbody/tr[1]/td[1]/input').send_keys(str(pressure_min)) # PLow input
	driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[2]/table/tbody/tr[2]/td[1]/input').send_keys(str(pressure_max)) # PHigh input
	driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[3]/input').click() # checkbox
	driver.find_element_by_xpath('//*[@id="main"]/form/ol/li[5]/input[1]').click()
	###
	time.sleep(3)
	### Third Page
	table = driver.find_element_by_xpath('//*[@id="main"]/table[1]/tbody') # table
	###
	### Logic
	headers = []
	for col in table.find_elements_by_css_selector('th'):
		headers.append(clean_str_HTML(col.get_attribute('innerHTML')))

	x_index = headers.index(substr_in_list(x_property[1:],headers,fetch=True))
	y_index = headers.index(substr_in_list(y_property[1:],headers,fetch=True))

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

df = pd.DataFrame(df_scaffold).T
df.columns = [headers[x_index], headers[y_index]]
df = df.convert_objects(convert_numeric=True,)
df = df.dropna(axis=0)

ml.use("Agg")

df.plot.scatter(x=headers[x_index],y=headers[y_index],title=compound + " at " + str(temperature) + "K",s=15)

ml.pyplot.savefig(compound)
###