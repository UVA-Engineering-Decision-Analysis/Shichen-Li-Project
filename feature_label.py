#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 14:36:51 2018

@author: sanjanamendu
"""

    
import os
import pandas as pd
import csv
import xlsxwriter
from datetime import datetime
import time
import shutil
from collections import defaultdict

def get_order(condition):
    if condition == 1:
        return ['HotCol','CoolScram','HotScram','CoolCol','Control']
    elif condition == 2:
        return ['Control','HotScram','HotCol','CoolScram','CoolCol']
    elif condition == 3:
        return ['CoolScram','CoolCol','Control','HotCol','HotScram']
    elif condition == 4:
        return ['HotScram','Control','CoolCol','HotCol','CoolScram']
    elif condition == 5:
        return ['CoolCol','HotScram','CoolScram','Control','HotCol']

# Read Timestamps
timestamp_filepath = '/Users/sm7gc/Desktop/MS&H/raw_data/Timestamps.csv'
with open(timestamp_filepath) as f:
    reader = csv.DictReader(f)
    raw_timestamps = [dict(d) for d in reader]

# Pre-Processing Timestamp Data
timestamps = []
for row in raw_timestamps:
    t = {}
    t['Participant'] = int(row['Participant'])
    t['Condition'] = int(row['Condition'])
    date = row['Date']
    col = [x for x in list(row.keys()) if x not in ['Participant','Date','Condition']]
    for c in range(0,len(col),2):
        start = col[c]
        end = col[c+1]
        cat = start.replace("Start","").lstrip()
        if cat == 'time': cat = 'Complete'
        start_time = datetime.strptime(date + ' ' + row[start], "%m/%d/%y %H:%M")
        end_time = datetime.strptime(date + ' ' + row[end], "%m/%d/%y %H:%M")
        t[cat] = [start_time,end_time]
    timestamps.append(t)
    
# Baseline Measures
outcomes = pd.read_csv('/Users/sm7gc/Desktop/MS&H/raw_data/Survey.csv')
baseline = ['Participant', 'Condition','Gender', 'Age (in years)','Extraversion', 'Agreeableness', 'Conscientiousness','Emotional Stability', 'Openess', 'CNS SCORE']
outcomes[baseline].to_csv('/Users/sm7gc/Desktop/MS&H/raw_data/Baseline.csv',index=False)

# Interval Measures
omit_baseline = [b for b in baseline if b not in ['Participant', 'Condition']]
surveys = outcomes.drop(columns=omit_baseline)

responses = defaultdict(list)
for t in timestamps:
#    responses['Condition'].append(t['Condition'])
    
    scores = surveys.loc[surveys['Participant'] == t['Participant']].squeeze()
    cnames = list(scores.keys())[2:]
    score_groups = [[scores[cnames[i]],scores[cnames[i+1]],scores[cnames[i+2]]] for i in range(0,len(cnames),3)]
    order = get_order(t['Condition'])
    
    sessions = list(t.keys())[2:]
    for i in range(len(order)):
        responses['Participant'].append(t['Participant'])
        responses['Condition'].append(t['Condition'])
        
        responses['Start Time'].append(t[order[i]][0])
        responses['End Time'].append(t[order[i]][1])
        responses['Session'].append(order[i])
    
        responses['Pre_HT'].append(score_groups[i][0])
        responses['Pre_S'].append(score_groups[i][1])
        responses['Pre_A'].append(score_groups[i][2])
        
        responses['Post_HT'].append(score_groups[i+1][0])
        responses['Post_S'].append(score_groups[i+1][1])
        responses['Post_A'].append(score_groups[i+1][2])
    
        responses['Diff_HT'].append(score_groups[i+1][0] - score_groups[i][0])
        responses['Diff_S'].append(score_groups[i+1][1] - score_groups[i][1])
        responses['Diff_A'].append(score_groups[i+1][2] - score_groups[i][2])
    
pd.DataFrame(responses).to_csv('/Users/sanjanamendu/Desktop/MS&H/raw_data/Outcome.csv',index=False)
    