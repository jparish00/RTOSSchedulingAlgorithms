"""
EDF CC Algorithm --- Earliest Deadline First Cycle Conserving --- Priority based on deadline 

EDF CC is a Dynamic Voltage Scaling which purpose is to save powe by reducing CPU frequency when possible
-Power is proportional to frequency

Input :  List of initialized 'Task', including invocations; Max time

Gilberto A. Lopez Astorga
31/03/22
UBC-O ENGR 467 2021W - RT Embedded Systems
"""

from schedulers.helpers.Classes import Task, Timeline, PseudoQueue
from math import isclose

def dummy_input_vars():
    # Task Number, Period, Execution
    # Task_master_dummy = [Task(1,8,7), Task(2,5,2), Task(3,10,2)]
    # Task_master_dummy = [Task(1,8,1), Task(2,15,3), Task(3,20,4), Task(4,22,6)]
    # Task_master_dummy = [Task(1,5,3), Task(2,8,3)]
    # Task_master_dummy = [Task(1,8,1), Task(2,5,4), Task(3,10,2)]
    t1_ac = [2,1]
    t2_ac = [1,1]
    t3_ac = [1,1]
    
    Task_master_dummy = [Task(1,8,3,t1_ac), Task(2,10,3,t2_ac), Task(3,14,1,t3_ac)]

    return Task_master_dummy


def utilization_EDF_CV(Task_master: PseudoQueue, tl: Timeline):
    task: Task
    util = 0
    if tl.c_time == 0:
        for task in Task_master.tasks_list:
            util = util + (task.exec_t/task.period)
    else:
        for task in Task_master.tasks_list:
            if len(task.start) == 0 or len(task.invocations) == 0:
                util = util + (task.exec_t/task.period)
            elif task.d_it-1<len(task.invocations):
                if task.priority == 1:
                    util = util + (task.exec_t/task.period)
                else:
                    util = util + (task.invocations[task.d_it-1]/task.period)

    return util


def cpu_freq(utilization, tl: Timeline):
    if len(tl.available_frequencies) == 0:
        return utilization
    else:
        i=0
        pFm=0
        for freq in tl.available_frequencies:
            if (freq - utilization) <= 0:
                pFm = tl.available_frequencies[i]
                break
            i+=1
        if pFm == 0:
            pFm = tl.avaiblable_frequencies[-1]
        # freq = min(tl.available_frequencies, key = lambda x: abs(x-utilization))
    return freq


def released_tasks_dynamic(tasks, tl: Timeline):
    task: Task
    for task in tasks:
        task.invocations[task.d_it-1]
        if len(task.invocations) == task.d_it:
            if task.finished:
                task.released =  False
            continue
        tl.c_time = round(tl.c_time,3)
        if isinstance(task.released_ts[-1], str):
            already_released = False
        else:
            already_released = isclose(task.released_ts[-1],tl.c_time)

        if isclose(tl.c_time % task.period, 0) and not isclose(tl.c_time,0) and not already_released: 
            if not isclose(task.remaining_t,0) and not task.finished:
                task.missed_deadlines.append(tl.c_time)

                if len(task.deadlines)-1 > task.d_it:
                    task.d_it += 1

            task.released_ts.append(tl.c_time)
            task.released = True
            task.finished = False
            tl.new_release = True
            if len(task.invocations) != 0:
                task.remaining_t = task.invocations[task.d_it-1]
                
        elif task.finished:
            task.released =  False


def priorities_EDF(Task_master : PseudoQueue, tl: Timeline):
    #Sorting priorities based on Deadline
    task : Task

    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.deadlines[x.d_it])
    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.released, reverse = True)
    i=1
    for task in Task_master.tasks_list:
        task.priority = i
        i += 1
 
def deadlines_gen(Task_master: PseudoQueue, tl: Timeline):
    # Generating deadlines
    task: Task
    for task in Task_master.tasks_list:
        dl = 0
        while(dl <= tl.max_time):
            dl = dl + task.period
            task.deadlines.append(dl)


def task_schedulable (task: Task, tl: Timeline):
    if ((task.remaining_t + tl.c_time) < task.deadlines[task.d_it]):
        task.schedulable = True
   
    else:
        task.schedulable = False
    

def fill_timeline_Dynamic(task: Task,tl: Timeline, Task_master : PseudoQueue):
    """
    Main Challenge is making c_time a decimal/float
    Don't care if schedulable or not. If not schedulable, just go to normal EDF and run @Fmax
    """
    if task.schedulable:
        while(not isclose(task.remaining_t, 0)): 
            task.remaining_t = round(task.remaining_t,3)
            task.remaining_t -=.001
            tl.cpu_task_usage.append(task.name)
            tl.time.append(tl.c_time)
            tl.c_time += .001
            released_tasks_dynamic(Task_master.tasks_list, tl)
            if tl.new_release:
                tl.new_release == False
                break

    else:
        while (tl.c_time < task.deadlines[task.d_it]):
            task.remaining_t = round(task.remaining_t,3)
            task.remaining_t -=.001
            tl.cpu_task_usage.append(task.name)
            tl.time.append(tl.c_time)
            tl.c_time += .001
            released_tasks_dynamic(Task_master.tasks_list, tl)
            if tl.new_release:
                tl.new_release == False
                break
        if len(task.deadlines)-1 > task.d_it:
            task.d_it += 1
        if len(task.invocations) != 0 and task.d_it<len(task.invocations):
            # task.remaining_t = task.invocations[task.d_it-1]     
            task.remaining_t = task.invocations[task.d_it]     
        else:
            task.remaining_t = task.exec_t
        task.finished = True


    if isclose(task.remaining_t, 0):
        task.finished = True
        if len(task.deadlines)-1 > task.d_it:
            task.d_it += 1


def cpu_idle(tl: Timeline, dynamic = False):
    tl.time.append(tl.c_time)
    tl.cpu_task_usage.append('IDLE')
    if dynamic:
        tl.c_time += .001
    else:
        tl.c_time += 1


def timeline_completion_EDF_CV(Task_master: PseudoQueue, tl: Timeline):
    task: Task
    check_idle = 0 
    while(1):
        for task in Task_master.tasks_list:

            released_tasks_dynamic(Task_master.tasks_list, tl)
            priorities_EDF(Task_master,tl)

            if task.d_it >= len(task.invocations):
                continue 
            if task.released and not task.finished and task.priority == 1:
                check_idle = 0 
                if len(task.invocations) == 0:
                # if isclose(tl.c_time,0) or len(task.invocations) == 0:
                    pFm = round(cpu_freq(utilization_EDF_CV(Task_master,tl),tl),3)
                    task.remaining_t = round(task.exec_t/cpu_freq(utilization_EDF_CV(Task_master,tl),tl),3)
                else:
                    pFm = round(cpu_freq(utilization_EDF_CV(Task_master,tl),tl),3)
                    task.remaining_t = round(task.invocations[task.d_it]/cpu_freq(utilization_EDF_CV(Task_master,tl),tl),3)
                task.cpu_freqs.append(pFm)
                task_schedulable(task, tl)     # check if task will finish on time
                if len(task.start) != 0 and task.end[-1] == tl.c_time:
                    del(task.end[-1])
                else:
                    task.start.append(tl.c_time)
                if task.released and tl.new_release:
                    tl.new_release = False
                fill_timeline_Dynamic(task,tl, Task_master)         # filling timeline with task usage
                task.end.append(tl.c_time)
            else:
                check_idle += 1
                if check_idle == len(Task_master.tasks_list):
                    cpu_idle(tl, True)
                    check_idle = 0

            if (tl.c_time > tl.max_time):
                break
        else:
            continue
        break
    
    # print(tl.cpu_task_usage)    


def format_output(Task_master):
    task: Task
    
    for task in Task_master:
        x=1


def run_EDF_CC(Task_master, max_t, av_freqs):
    '''

    Runs EDF algorithm and returns timeline

    Input: List of Task Objects
    
    Output: PseudoQueue, Timeline

    '''
    #
    Task_master = PseudoQueue(Task_master)

    tl = Timeline(av_freqs, max_t)

    # schedulability_test(Task_master)

    deadlines_gen(Task_master,tl)

    timeline_completion_EDF_CV(Task_master,tl)

    for task in Task_master.tasks_list:
        print(task.name)
        print('S:', task.start)
        print('F:', task.end)
        print('Missed deadlines:', task.missed_deadlines[1:])
    return Task_master, tl
            
            

