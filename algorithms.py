
def schEDF(tsk):
    s = 0
    for key in tsk:
        s = s + int(key[1]) / int(key[0])
        
    print(round(s,3))
    print()
    
    if(s <= 1):
        schedulability = True
    else:
        schedulability = False
    
    return schedulability, s

# I need help with the main algorithm :(


#REGULAR ALGORITHMS
# Schedualability test format

# input -> tasks[Task(), ...]
# output -> schedulability, utilization

# Algorithm

# input -> tasks[Task(), ...], time=int
# output -> Timelines[(name=str, blockstart=int, blockend=int), ...], misseddeadline[(name=str, timemissed=int)]

# Cycly Conserving Algo

# input -> tasks[Task(), ...], time=int, freqs[], invocationCount=int
# output -> Timelines[((name=str, blockstart=int, blockend=int, percentofMaxFreq=float, misseddeadline=bool), ...]

# Proposed: Cyclic Conserving
# input -> tasks[Task(), ...], time=int, freqs[]
# output -> Timelines[((name=str, blockstart=int, blockend=int, percentofMaxFreq=float), ...], misseddeadline[(name=str, timemissed=int)]

def RoundRobin(tasks, time):


    print()

def FCFS(tasks, time):

    print()