####################
####################
# This script is built on top of Characterization_demo.py. It opens the recorded waveform traces (i.e. acquiered using a scope).
# Then an Interval of interest is selected. The traces are cut in this interval and smoothed.
# Then the average trace is calculated and an interval selected. This is the "pattern" that is considered as reference.
# All traces are shifted step by step and the best shift is decided using Pearson correlation against the reference pattern.
####################
# Author : LoesZe
# Date : 14/04/2018
# Last review : 19/04/2018
####################

#####
# Importing libraries
#####
##
# Numpy is fundamental for scientific computing using python. It deals here with arrays a lot, opens and saves file in CSV form.
import numpy as np
from numpy import pi
from numpy import genfromtxt
##
# SciPy is opeen source software for mathematics, science and engineering. Here it deals with signal processing (i.e. filter). And we may want to use their correlation function.
import scipy as sp
from scipy.signal import butter, lfilter, freqz, filtfilt
from scipy.stats.stats import pearsonr
#undertest
import scipy.spatial as spatial
# Matplotlib is use to generate figures :
import matplotlib.colors as colors
import matplotlib.pyplot as plt

#######################################
### Define some usefull functions : ###
#######################################
##
# This function get the raw data in.
# After reshaping the file is saved as a csv file.
def handle_Traces(path,verbose):
    # Data is made with a C program that just apends the sample value and ','
    # So we get an extra emplty column appended.
    # We get that one removed.
    # Finally the properly formated input is saved in /Data/data_demo.csv
    data = genfromtxt(path, delimiter=',')
    data = data[:,:-1]
    if verbose :
        nb_samples = data[0].size
        nb_inputs = data.size/nb_samples
        print ('The input data is %d samples long.' % nb_samples)
        print ('There are %d inputs.' % nb_inputs)
        print ('Hereafter an partial view of this data set:')
        print (data)
    return data

##
# This is a lowpass filter that I need to investigate.
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

##
# MAIN #
data = handle_Traces('IN/traces_demo.txt',1)
nb_samples = data[0].size
nb_inputs = int(data.size/nb_samples)

##################################################
#  generate slide "references and time interval" #
##################################################
x = range(nb_samples)
fig = plt.figure()
fig.clf()
## sublopt 1 - raw data :
plot_P_vs_t = plt.subplot("111")
#plot_P_vs_t.set_ylabel('Power traces')
plot_P_vs_t.set_xlabel('samples')
plot_P_vs_t.set_title('Power traces recorded with an oscilloscope')
for idx in range(nb_inputs):
    labeli = "input " + str(idx)
    plot_P_vs_t.plot(x,data[idx], '-', linewidth=0.5, label=labeli)
plot_P_vs_t.legend(loc="upper right", fontsize=8)
## save and show
plt.savefig('Figures/traces_record.png')
plt.show()
plt.close()
##################################################
## a prompt can ask for a reference trace (to do)
## invalidate some inputs based on some criteria ?
nb_trace = nb_inputs
## decide a time interval for work
print("-- Interval of interest --")
first_search = int(input("first: (50)"))
last_search = int(input("last: (300)"))
search_range = last_search - first_search
## filter Parameters - can be changed when the human interface gets more visual
cutoff = 1500
fs = 50000
##################################################

# Generating the smoothed input data to remove noise
# for this we use butter_lowpass_filtfilt function
data_smooth = np.zeros( (nb_trace,search_range), dtype=np.int16  )
for idx in range(nb_trace):
    data_smooth[idx] = butter_lowpass_filtfilt(data[idx,first_search:last_search], cutoff, fs)  

# Generating the average smoothed traces
# this one will be used as a "fair"-reference
data_smooth_avrg = np.zeros(search_range, dtype=np.int16  )
for idx in range(nb_trace):
    data_smooth_avrg = data_smooth_avrg+data_smooth[idx]
data_smooth_avrg = data_smooth_avrg/nb_trace

#######################################################
#  generate slide "before-after smooth and reference" #
#######################################################
x = range(search_range)
figure_trace = plt.figure()
figure_trace.clf()
#### sublopt 1 - raw data :
##plot_P_vs_t = plt.subplot("211")
###plot_P_vs_t.set_ylabel('Power traces')
##plot_P_vs_t.set_xlabel('samples')
##plot_P_vs_t.set_title('Power traces recorded with an oscilloscope')
##for idx in range(nb_inputs):
##    labeli = "input " + str(idx)
##    plot_P_vs_t.plot(x,data[idx,first_search:last_search], '-', linewidth=0.5, label=labeli)
##plot_P_vs_t.legend(loc="upper right", fontsize=8)
## sublopt 2 - filtered data :
#plot_PS_vs_t = plt.subplot("212")
plot_PS_vs_t = plt.subplot("111")
#plot_PS_vs_t.set_ylabel('')
plot_PS_vs_t.set_xlabel('samples (within interval of interest)')
plot_PS_vs_t.set_title('Smoothed power traces')
plot_PS_vs_t.plot(x, data_smooth_avrg, 'b', linewidth=1, color='green',label='reference (average)')
for idx in range(nb_trace):
    labeli = "input " + str(idx)
    plot_PS_vs_t.plot(x, data_smooth[idx], '--', linewidth=0.5, label=labeli)
plot_PS_vs_t.legend(loc="upper right", fontsize=8)
## save and show
plt.savefig('Figures/traces_smoothed.png')
plt.show()
plt.close()
#######################################################
## decide a time interval for the pattern recognition
print("-- Interval of alignment pattern --")
first_sample = int(input("first: (42)"))
last_sample = int(input("last: (202)"))
pattern_size = last_sample-first_sample
#######################################################

# generating pattern
pattern = np.zeros(pattern_size, dtype=np.int16  )
pattern = data_smooth_avrg[first_sample:last_sample]

#########################################################
# generate slide "alignement using pearson correlation" #
#########################################################
x = range(pattern_size)
figure_trace = plt.figure()
figure_trace.clf()
## sublopt 1 - raw data :
plot_P_vs_t = plt.subplot("111")
plot_P_vs_t.set_ylabel('Shifted traces')
plot_P_vs_t.set_xlabel('samples (+shift)')
plot_P_vs_t.set_title('Aligning using Pearson correlation demo on first input')
plot_P_vs_t.plot(x, pattern, 'b', linewidth=1, color='green',label='Reference pattern')
#scanning search interval for trace ref
corr = np.zeros( (2,search_range-pattern_size))
ids_best = 0
for ids in range(search_range-pattern_size):
    plot_P_vs_t.plot(x, data_smooth[0,ids:ids+pattern_size], '--', linewidth=0.1)
    corr[0,ids],corr[1,ids]  = pearsonr(pattern,data_smooth[0,ids:ids+pattern_size])
    if (corr[0,ids] > corr[0,ids_best]):
        ids_best = ids
plot_P_vs_t.plot(x, data_smooth[0,ids_best:ids_best+pattern_size], 'b', linewidth=1, color='red',label='After Alignement')
plot_P_vs_t.plot(x, data_smooth[0,first_sample:last_sample], 'b', linewidth=1, color='pink',label='Before alignement')
plot_P_vs_t.legend(loc="upper right", fontsize=8)
plt.savefig('Figures/traces_alignement_demo.png')
plt.show()
plt.close()
#########################################################

# scanning all traces to find the best alignement
ids_best = np.zeros(nb_trace, dtype=np.int16  )
for idx in range(nb_trace):
    corr = np.zeros( (2,search_range-pattern_size))
    for ids in range(search_range-pattern_size):
        corr[0,ids],corr[1,ids]  = pearsonr(pattern,data_smooth[idx,ids:ids+pattern_size])
        if (corr[0,ids] > corr[0,ids_best[idx]]):
            ids_best[idx] = ids
            
# generating a new cut, smoothed and aligned data file
data_smooth_aligned = np.zeros( (nb_trace,search_range-ids_best.max()), dtype=np.int16  )
for idx in range(nb_trace):
    data_smooth_aligned[idx] = data_smooth[idx,ids_best[idx]:ids_best[idx]+search_range-ids_best.max()]

#np.savetxt("Data/data_smooth_aligned.csv",data_smooth_aligned, delimiter=",")
#######################################################
#  generate slide "before-after smooth and reference" #
#######################################################
x = range(search_range-ids_best.max())
figure_trace = plt.figure()
figure_trace.clf()
#### sublopt 1 - raw data :
##plot_P_vs_t = plt.subplot("211")
###plot_P_vs_t.set_ylabel('Smoothed power traces')
##plot_P_vs_t.set_xlabel('samples')
##plot_P_vs_t.set_title('Smoothed power traces before alignement')
##for idx in range(nb_inputs):
##    labeli = "input " + str(idx)
##    plot_P_vs_t.plot(x, data_smooth[idx,0:search_range-ids_best.max()], '-', linewidth=0.5, label=labeli)
##plot_P_vs_t.legend(loc="upper right", fontsize=8)
## sublopt 2 - rfiltered data :
#plot_PS_vs_t = plt.subplot("212")
plot_PS_vs_t = plt.subplot("111")
#plot_PS_vs_t.set_ylabel('Aligned smoothed power traces')
plot_PS_vs_t.set_xlabel('samples (within interval of interest)')
plot_PS_vs_t.set_title('Smoothed and aligned power traces')
for idx in range(nb_trace):
    labeli = "input " + str(idx)
    plot_PS_vs_t.plot(x, data_smooth_aligned[idx], '-', linewidth=0.5, label=labeli)
plot_PS_vs_t.legend(loc="upper right", fontsize=8)
## save and show
plt.savefig('Figures/traces_smoothed_aligned.png')
plt.show()
plt.close()
#######################################################

## The pattern is saved to align the full batch of traces.
np.savetxt("Data/pattern_search_%d_%d_smooth_%d_%d_select_%d_%d.csv"%(first_search,last_search,cutoff,fs,first_sample,last_sample), pattern, delimiter=",")
## As weel as the parameter for cut smooth and alignement.
np.savetxt("Data/pattern_info.csv",[first_search,last_search,cutoff,fs,first_sample,last_sample], delimiter=",")