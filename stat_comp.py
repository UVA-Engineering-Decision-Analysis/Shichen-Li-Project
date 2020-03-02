#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:45:13 2018

@author: sanjanamendu
"""

import itertools
import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
from scipy import stats
from collections import defaultdict

# Self-Report Measures
baseline = pd.read_csv('/Users/sm7gc/Desktop/MS&H/outcomes/baseline.csv')
responses = pd.read_csv('/Users/sm7gc/Desktop/MS&H/outcomes/outcome.csv')

# Featurized Empatica Data
raw_df = pd.read_csv('/Users/sm7gc/Desktop/MS&H/outcomes/extracted features/extracted_features_v5.csv')
#clean_df = raw_df.drop(columns=['pNN20','pNN50']) # 164

# Filtering
#clean_df = clean_df[clean_df.Label != 'Unknown'] # 142

filt_col = raw_df.columns.values[3:]
filt_df = raw_df.dropna(subset=raw_df.columns.values[3:], how='all')

nb_df = filt_df[filt_df['Label'] != 'Baseline']

outcome_df = pd.merge(responses, nb_df,  how='inner', right_on=['Participant','Label'], left_on = ['Participant','Session'])
outcome_df.drop(['Label'],axis=1).to_csv('/Users/sm7gc/Desktop/MS&H/outcomes/complete_feat.csv',index=False)


# ANOVA  & T-Test Calculations

statistics = defaultdict(list)

pairs = itertools.combinations(set(outcome_df.Label),2)
        
omit_col = ['Label','Participant','Start Time','End Time','Condition','Session','Segment']
omit_col.extend(['Pre_HT','Pre_S','Pre_A','Post_HT','Post_S','Post_A','Diff_HT','Diff_S','Diff_A'])
    
for p in pairs:
    o1 = outcome_df[outcome_df.Label == p[0]].sort_values(['Segment'])
    o2 = outcome_df[outcome_df.Label == p[1]].sort_values(['Segment'])
    o_df = pd.merge(o1, o2,  how='inner', right_on=['Participant','Segment'], left_on = ['Participant','Segment'])

    features = [f for f in list(o1.columns.values) if f not in omit_col]
    
    for f in features:
        statistics["Label A"].append(p[0])
        statistics["Label B"].append(p[1])
        statistics["Feature"].append(f)
        
        sub_df = o_df.dropna(subset=[f+'_x', f+'_y'], how='any')[[f+'_x', f+'_y']]
        statistics["Sample"].append(len(sub_df))
        
#        plt.plot(sub_df[f+'_x'])
#        plt.plot(sub_df[f+'_y'])
#        plt.show()
        
        t, t_p = stats.ttest_ind(sub_df[f+'_x'], sub_df[f+'_y'])
        f, f_p = stats.f_oneway(sub_df[f+'_x'], sub_df[f+'_y'])
        
        statistics["T-Statistic"].append(t)
        statistics["T-Test P-value"].append(t_p)
        statistics["ANOVA F-Statistic"].append(f)
        statistics["ANOVA P-value"].append(f_p)
        

analysis = pd.DataFrame.from_dict(statistics)
analysis = analysis.dropna()
filt_a = analysis[(analysis["ANOVA P-value"] <= 0.05) | (analysis["T-Test P-value"] <= 0.05)]

analysis.to_csv('/Users/sm7gc/Desktop/MS&H/outcomes/analysis.csv',index=False)
filt_a.to_csv('/Users/sm7gc/Desktop/MS&H/outcomes/sig_analysis.csv',index=False)

o_df.to_csv('/Users/sm7gc/Desktop/MS&H/outcomes/sample.csv',index=False)
