#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 09:59:20 2018

@author: sm7gc

Data cleaning script that separates raw Sensus data (from JSON files) per probe into corresponding CSV
"""

import os
import shutil
import csv
#import xlsxwriter
from datetime import datetime
import time
#import numpy as np
import pandas as pd
from collections import defaultdict

# --------- READ TIMESTAMPS ---------

# Read Timestamps
timestamp_filepath = '/Users/sm7gc/Desktop/MS&H/raw_data/Timestamps.csv'
with open(timestamp_filepath) as f:
    reader = csv.DictReader(f)
    raw_timestamps = [dict(d) for d in reader]

# Pre-processing timestamp data
timestamps = []
for row in raw_timestamps:
    t = {}
    t['Participant'] = row['Participant']
    date = row['Date']
    col = [x for x in list(row.keys()) if x not in ['Participant','Date','Condition']]
    for c in range(0,len(col),2):
        start = col[c]
        end = col[c+1]
#        start_time = datetime.strptime(date + ' ' + row[start], "%m/%d/%y %H:%M")
#        end_time = datetime.strptime(date + ' ' + row[end], "%m/%d/%y %H:%M")
        start_time = pd.Timestamp(date + ' ' + row[start])
        end_time = pd.Timestamp(date + ' ' + row[end])
        cat = start.replace("Start","").lstrip()
        if cat == 'time': cat = 'Complete'
        t[cat] = [start_time,end_time]
        t[cat+'_seg'] = pd.date_range(start_time,end_time,freq='15S')
        
    timestamps.append(t)
t_df = pd.DataFrame(timestamps)
    
# --------- DATA ITERATION ---------

# Cleaning/Processing raw data
data_folder = '/Users/sm7gc/Desktop/MS&H/raw_data' # Define data filepath(s)
sub_folders = [os.path.join(data_folder, o) for o in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder,o))]

absolute_start_time = time.time()

complete_data = defaultdict(list)

for folder in sub_folders:

    data_type = os.path.basename(folder)
    print("....."+data_type+".....")
    
    filenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(folder) for f in filenames if os.path.splitext(f)[1] == '.csv']
    
    for i in range(len(filenames)):
        
        file = filenames[i]
    
        print("File " + str(i+1) + " out of " + str(len(filenames)) + ' (' + data_type + ')') # progress print statement
        
        start_time = time.time()
    
        raw_data = [dict(d) for d in csv.DictReader(open(file))]
        
        for line in raw_data:
#            try:
#                timestamp = datetime.strptime(line['Timestamp'],"%Y-%m-%d %H:%M:%S.%f")
#            except:
#                timestamp = datetime.strptime(line['Timestamp']+'.000000',"%Y-%m-%d %H:%M:%S.%f")
            timestamp = pd.Timestamp(line['Timestamp'])     
            for t in timestamps:
                if timestamp >= t['Complete'][0] and timestamp <= t['Complete'][1]:
                    
                    line['Participant'] = t['Participant']
                    labels = [x for x in list(t.keys()) if ((x not in ['Participant','Complete']) and ('_seg' not in x))]
                    for l in labels:
                        if timestamp >= t[l][0] and timestamp <= t[l][1]:
                            line['Label'] = l                                
                            
                    if 'Label' not in line: line['Label'] = 'Unknown'
                    line['Timestamp'] = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
                    filename = line['Participant'] + '_' + line['Label'] + '_' + data_type
                    complete_data[filename].append(line)
                    
                    continue

        elapsed_time = time.time() - start_time
        elapsed_total_time = time.time() - absolute_start_time        
        
        print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())


# --------- FILE I/O ---------


# Writing labeled data to file
target_folder = '/Users/sm7gc/Desktop/MS&H/noseg_features' # Define folder to store clean files
file_ext = '.xlsx'

shutil.rmtree(target_folder)
os.makedirs(target_folder)

absolute_start_time = time.time()
for key in complete_data.keys():
 
    print(key)
    ksplit = key.split('_'); pid = ksplit[0]; label = ksplit[1]; datum = ksplit[2]
    # if label in ['Unknown','Baseline','QBlock']: continue
    if label == 'Unknown': continue

    start_time = time.time()
    
    flist = complete_data[key]
    df = pd.DataFrame(flist)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'],infer_datetime_format=True)
    
    if datum == 'TEMP': df=df.reindex(columns=['TEMP','Label','Participant','Timestamp'])

    filename = key + '.xlsx'
    writer = pd.ExcelWriter(os.path.join(target_folder,filename))
    df.to_excel(writer,'Sheet1',index=False)
    writer.save()
    
#    pid_df = t_df[t_df['Participant'] == pid]
#    dt_range = pid_df[label].item()
#    segments = pid_df[label+'_seg'].item()
#
#    for s in range(len(segments)-2):
#        filename = key + '_' + str(s+1) + file_ext
#        dat = df[(df['Timestamp'] > segments[s]) & (df['Timestamp'] < segments[s+2])]
#        if dat.empty: continue
#        dat['Timestamp'] = dat['Timestamp'].dt.strftime('%m-%d-%Y %H:%M:%S.%f')
#        writer = pd.ExcelWriter(os.path.join(target_folder,filename))
#        dat.to_excel(writer,'Sheet1',index=False)
#        writer.save()

            
    elapsed_time = time.time() - start_time
    elapsed_total_time = time.time() - absolute_start_time        
    
    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())

print("Total Program Runtime: " + str(time.time() - absolute_start_time))