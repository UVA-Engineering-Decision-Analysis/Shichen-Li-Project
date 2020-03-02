#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 09:46:44 2018

@author: sm7gc
"""

import numpy as np
from scipy.fftpack import fftfreq
from scipy.stats import entropy

#def stft(x, window_size, overlap=2):
#    hop = int(window_size / overlap)
#    w = scipy.hanning(window_size+1)[:-1]
#    return [np.fft.rfft(w*x[i:i+window_size]) for i in range(0, len(x)-window_size, hop)] 

def sig_mean(x):
    return np.mean(x)

def energy(x):
    return np.sum(np.power(x,2))

def sig_time_duration(t):
    return t[len(t)] - t[0]

def sig_entropy(x):
    return entropy(x)

def fft_acc(x, y, z, window_size, overlap=2):
    fftx = np.fft.fft(x)
    timestep = 0.1
    freq = np.fft.fftfreq(len(x), d=timestep)   
    return fftx
    
