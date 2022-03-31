"""
Schedulability test format RM - EDF
# input -> tasks[Task(), ...]
# output -> schedulability, utilization

# Timeline RM EDF
input -> tasks[Task(), ...], time=int
output -> Timelines[(name=str, blockstart=int, blockend=int), ...], misseddeadline[(name=str, timemissed=int)]

EDF DVSCyclic Conserving 

input -> tasks[Task(), ...], time=int, freqs[], invocationCount=int
output -> Timelines[((name=str, blockstart=int, blockend=int, percentofMaxFreq=float, misseddeadline=bool), ...]

"""

from schedulers.EDF import run_EDF
from schedulers.EDF_CC import run_EDF_CC
from schedulers.helpers.Helpers import dummy_input_vars, output_RM_EDF, output_EDF_CC
from schedulers.RM import run_RM


max_t = 18
# #RM
Task_master = dummy_input_vars()
tm,tl = run_RM(Task_master, max_t)
output = output_RM_EDF(tm,tl)

# # EDF
Task_master = dummy_input_vars()
tm,tl = run_EDF(Task_master,max_t)
output = output_RM_EDF(tm,tl)

#EDF CC
av_freqs=[1,.75,.5]
av_freqs=[]
# av_freqs=[]

Task_master = dummy_input_vars()
tm,tl = run_EDF_CC(Task_master, max_t, av_freqs)
output = output_EDF_CC(tm,tl)
