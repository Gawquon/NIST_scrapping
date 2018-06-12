import csv
import pandas as pd

#Begin functions -----------------------------------------------------
"""Summary

	desc """
def calcMolWeight(molecule,di):
	weight = 0
	atom = ""
	digits = ""
	alpha = True

	for char in molecule:
		if (char.isupper() and atom != "" and alpha and atom[0].isupper()):
			weight += float(di[atom])
			atom = char
		elif char.isalpha() and alpha:
			atom = ''.join([atom,char])
		elif char.isdigit():
				alpha = False
				digits = ''.join([digits,char])
		elif char.isalpha() and not alpha:
			weight += float(di[atom]) * int(digits)
			atom = ""
			digits = ""
			alpha = True
			atom = ''.join([atom,char])
		else:
			print("Invalid String error")

	if molecule[-1].isdigit():
		weight += float(di[atom]) * int(digits)
	else:
		weight += float(di[atom])
	return weight

"""Converts a mol percent into a mass percent"""
def convtToWeightPer(molPerOf_1, mol1, mol2,di):
	mw1 = calcMolWeight(mol1,di)
	mw2 = calcMolWeight(mol2,di) #hmmm
	
	mp = float(molPerOf_1)

	weightPer = (mp * mw1) / ((mp * mw1) + (1- mp) * mw2)
	return weightPer

"""Populates a dictionary with atomic masses accesed by thier atomic symbol as a keyword"""
def generatePerTabl(filename):
	with open(filename, mode='r') as infile:
		reader = csv.reader(infile)
		perTabl = {rows[0]:rows[1] for rows in reader}
	return perTabl
# End Functions ----------------------------------------------------------

def execute(df,solute,solvent,col):
	perDict = generatePerTabl("AtomicMasses.csv")

	l = []

	for el in df[col]:
		l.append(convtToWeightPer(el,solute,solvent,perDict))
		df[col] = pd.Series(l)
	return df