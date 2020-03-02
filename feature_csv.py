#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 09:37:55 2018

@author: sm7gc
"""

import time
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import warnings
from collections import defaultdict

def group_files(filenames):
    filt_files = defaultdict(list)
    for f in filenames:
        filename = os.path.basename(f)
        base = os.path.splitext(filename)[0]
        terms = base.split('_')
        key = terms[0]+'_'+terms[1]
        filt_files[key].append(f)
    return filt_files

def strp(timestamp):
    return datetime.strptime(timestamp[:19],"%Y-%m-%d %H:%M:%S")

warnings.filterwarnings("ignore")

absolute_start_time = time.time() # Program Start Time

data_path = '/Users/sanjanamendu/Desktop/MS&H/features'

filenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(data_path) for f in filenames if os.path.splitext(f)[1] == '.csv']

filt_files = group_files(filenames)

features = defaultdict(list)
complete_features = ['mean_hr','num_peaks','ppg_duration','ppg_energy','gsr_duration','gsr_energy','gsr_num_peaks']

for key in filt_files:
    print(key)
    features['participant'].append(key.split('_')[1])
    features['label'].append(key.split('_')[0])
    group = filt_files[key]
    todo_feat = complete_features.copy()
    for file in group:
        filename = os.path.basename(file)
        base = os.path.splitext(filename)[0]
        data_type = base.split('_')[2]
        
        if data_type == 'Unknown': continue
        
        start_time = time.time()
        raw_df = pd.read_csv(file)
        
        data_key = list(raw_df.keys())[1]
        data = raw_df[data_key]
        
        peaks = list(find_peaks(data)[0])
        
        plt.plot(data,markevery=peaks, marker="X", markerfacecolor='red', markeredgecolor='red')
        plt.show()
        
        timestamps = raw_df['Timestamp']
        
        if data_type == 'HR':
            features['mean_hr'].append(np.mean(data))
            
            todo_feat.remove('mean_hr')
            
        elif data_type == 'IBI':
            
#            todo_feat.remove('num_peaks')
            
        elif data_type == 'PPG':
            features['ppg_duration'].append((strp(timestamps[len(timestamps)-1]) - strp(timestamps[0])).total_seconds())
            features['ppg_energy'].append(np.sum(np.power(data,2)))
        
            todo_feat.remove('ppg_duration')
            todo_feat.remove('ppg_energy')
            
        if data_type == 'EDA':
            features['gsr_duration'].append((strp(timestamps[len(timestamps)-1]) - strp(timestamps[0])).total_seconds())
            features['gsr_energy'].append(np.sum(np.power(data,2)))
            features['gsr_num_peaks'].append(len(find_peaks(data)[0]))
    
            todo_feat.remove('gsr_duration')
            todo_feat.remove('gsr_energy')
            todo_feat.remove('gsr_num_peaks')
    
    for feat in todo_feat:
        features[feat].append(0)
        

final_feat = pd.DataFrame(features)
final_feat.to_csv('/Users/sanjanamendu/Desktop/MS&H/extracted_features.csv', index=False)
print("Total Program Runtime: " + str(time.time() - absolute_start_time)) # Program End Time
