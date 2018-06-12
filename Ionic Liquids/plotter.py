import numpy as np
import pandas as pd
import matplotlib as ml
import glob as g
import os
#End imports-------------------------------------------------

MASS_PERCENT = 'Mass fraction of 1-butyl-3-methylimidazolium bis(trifluoromethylsulfonyl)imide Liquid'
#End constant declaration------------------------------------

def get_color(solvent):
    solvent_color_map = { 
        'ch3cn' : 'blue',
        'bucn' : 'blue',
        'adpn' : 'blue',
        'benzonitrile' : 'blue',
        'ch3oh' : 'green',
        'etoh' : 'green',
        'butanol' : 'green',
        'octanol' : 'green',
        'gly' : 'green',
        'dcm' : 'orange',
        'dce' : 'orange',
        'clbenzene' : 'orange',
        'glyme' : 'red',
        'diglyme' : 'red',
        '14dio' : 'red',
        'ec' : 'black',
        'thf' : 'red',
        'pc' : 'black',
        'dma' : 'black',
        'dmso' : 'black',
        'dmf' : 'black',
        'ace' : 'black',
        'cy6one' : 'black'
    }   
    return solvent_color_map[solvent]
# ---------------------End function definetions--------------

# ----------------------configuration------------------------
property_to_view = "rho" #String of measured property name as it appears in the simulation data CSV file
property_units = "kg/m^3" #Units of measurement desired to be displayed on graph for y-axis
path_to_csv = "/" #location of FOLDER all of the molecule csv files are stored in
path_to_simData = "/" #location of FILE for simulation data
# -----------------------------------------------------------

ml.use('Agg') #still need to format for PDF release

#Temporary library of NIST names to abverviations used in FIRST data
shorthandDict = {"tetrahydrofuran.csv" : "thf", "methanol.csv" : "ch3oh", "ethanol.csv" : "etoh", "dimethyl sulfoxide.csv" : "dmso", "butan-1-ol.csv" : "butanol", "acetonitrile.csv" : "ace", "4-methyl-1,3-dioxolan-2-one.csv" : "pc"}

dfb= pd.read_csv(path_to_simData)
dfb.set_index("solvent", inplace=True)

for m in g.glob(os.path.join(path_to_csv, '*.csv')): #m is each individual molecule's collated data
    df = pd.read_csv(m)
    df.columns = ['index',MASS_PERCENT,property_units,'K','kPa'] #want to elminate this step 
    solvent = shorthandDict[m.split('/')[-1]]

    ax = df.plot.scatter(x=MASS_PERCENT,y=property_units,color='gray',title=m.split('/')[-1][:-4],s=50,label='Experimental data')

    dfm = dfb.loc[solvent]
    dfm = dfm.sort_values(by=["wtpct"])
    dfm.plot(x='wtpct',y=property_to_view,color=get_color(solvent),ax=ax,label='Simulation data',lw=3)

    ml.pyplot.savefig(m[:-4])