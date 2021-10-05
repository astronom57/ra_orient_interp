#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 11:17:48 2021

Perform interpolation and extrapolation of the orientation file. 

"""
__author__ = 'Mikhail Lisakov'
__credits__ = ['Mikhail Lisakov']
__maintainer__ = 'Mikhail Lisakov'
__email__ = 'mlisakov@mpifr-bonn.mpg.de'
__copyright__ = 'Copyright 2021'
__license__ = 'GNU GPL v3.0'
__version__ = '0.1'
__status__ = 'Dev'


import datetime as dt
import csv
import sys, getopt

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from mylogger import create_logger

def read_orientation(file):
    """Read orientation file into a pandas DataFrame.
    raks21j 2018-04-26 11:00:42 -167.740376339451   -5.73912255740709   -89.011655625893    62.787723385126 105.132039892413    26.501463329714

    Args:
        file (string): 
            filename to read
    
    Returns:
        df (DataFrame): 
            dataframe with data. Columns obscode, time, xra, xdec, yra,ydec, zra, zdec,
            i.e. RA and DEC coordinates for all three axes of RadioAstron.
        
    """
        
        
    df = pd.read_csv(file, sep='\s+', comment='#', 
                     names=['obscode', 'tmp1', 'tmp2', 
                            'xra', 'xdec',
                            'yra', 'ydec',
                            'zra', 'zdec'],
                     parse_dates={'time':[1,2]})
    

    return df




# to be read from the command line later
exp_start = None
exp_end = None

try:
    opts, args = getopt.getopt(argv,"hb:a:",["add_before=","add_after="])
except getopt.GetoptError:
    print() 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)





# logger = create_logger()
file = '/homes/mlisakov/data/correlation/gg083j/orientation.txt'
df = read_orientation(file)
obscode = max(set(df.obscode.values), key=list(df.obscode.values).count)



# deal with 360 degrees wraps
# TEST
for col in ['xra', 'xdec', 'yra', 'ydec', 'zra', 'zdec']:
    df.loc[:, col] = np.degrees(np.unwrap(np.radians(df.loc[:, col])))


fig, ax = plt.subplots(2,1, sharex=True)
ax[0].plot(df.time.values, df.xra.values, '-o')
ax[1].plot(df.time.values, df.yra.values, '-o')


if exp_start is None:
    exp_start = df.time[0] - dt.timedelta(hours=1)
if exp_end is None:
    exp_end = df.time[df.index.max()] + dt.timedelta(hours=1)

delta_t = df.time.diff().median() # median sampling time. Should be 1 minute

time_interpolated = pd.date_range(start=exp_start,
                                  end=exp_end,
                                  freq='T') # T == minute

# new dataframe with the same columns but different index.
dfn = pd.DataFrame(columns = df.columns)
dfn.loc[:, 'time'] = time_interpolated
# merge old with new to get 'time' from new in the old. The data are preserved where they should.
df = pd.merge(df, dfn.loc[:, 'time'], how='right', on='time', suffixes=['', '1'])
# interpolate
df.interpolate(limit_direction='both', inplace=True)
df.loc[:, 'obscode'] = obscode

ax[0].plot(df.time.values, df.xra.values, 'x')
ax[1].plot(df.time.values, df.yra.values, 'x')


# write results to a new file
f = open('{}_interpolated'.format(file), 'a')
f.write('# RadioAstron position information for experiment {}\n'.format(obscode))
f.write('# Coordinates are equatorial J2000 measured in degrees\n')
f.write('# Time us UTC\n')
f.write('#obscode    time            X R.A.      X DEC       Y R.A.      Y DEC       Z R.A.      Z DEC\n')

df.to_csv(f, sep=' ', columns=['obscode', 'time', 'xra', 'xdec', 'yra', 'ydec', 'zra', 'zdec'],
          header=False, index=False, mode='a', quotechar=' ')
f.close()





    