"""
Functions acting as assisters for scheduling algorithms

Gilberto A. Lopez Astorga
31/03/22
UBC-O ENGR 467 2021W - RT Embedded Systems
"""
from itertools import groupby 
from schedulers.helpers.Classes import Task, Timeline, PseudoQueue

def dummy_input_vars():
    # Task Number, Period, Execution
    # Task_master_dummy = [Task(1,8,7), Task(2,5,2), Task(3,10,2)]
    # Task_master_dummy = [Task(1,8,1), Task(2,15,3), Task(3,20,4), Task(4,22,6)]
    # Task_master_dummy = [Task(1,5,3), Task(2,8,3)]
    # Task_master_dummy = [Task(1,8,1), Task(2,5,4), Task(3,10,2)]
    # t1_ac = [2,1]
    # t2_ac = [1,1]
    # t3_ac = [1,1]
    
    # Task_master_dummy = [Task(1,8,3,t1_ac), Task(2,10,3,t2_ac), Task(3,14,1,t3_ac)]
    t1_ac = [1,1]
    t2_ac = [1,1]
    t3_ac = [2,1]
    
    Task_master_dummy = [Task(1,6,2,t1_ac), Task(2,8,3,t2_ac), Task(3,12,3,t3_ac)]

    return Task_master_dummy

def released_tasks (tasks, tl: Timeline):
    task: Task

    for task in tasks:
        if tl.c_time % task.period == 0 and tl.c_time != 0 and task.released_ts[-1] != tl.c_time: 
            if task.remaining_t !=0 and not task.finished:
                task.missed_deadlines.append(tl.c_time)

                if len(task.deadlines)-1 > task.d_it:
                    task.d_it += 1

            task.released_ts.append(tl.c_time)
            task.released = True
            task.finished = False
            tl.new_release = True
            task.remaining_t = task.exec_t

        elif task.finished:
            task.released =  False

def output_RM_EDF(Task_master : PseudoQueue, tl: Timeline):
    """
    Formatting Backend output RM EDF
    input -> tasks[Task(), ...], time=int
    output -> Timelines[(name=str, blockstart=int, blockend=int), ...], misseddeadline[(name=str, timemissed=int)]

    """
    task: Task
    tl_tasks = [i[0] for i in groupby(tl.cpu_task_usage)]
    i=0
    output = []
    timelines_o = []
    m_d = [] 
    while (i < len(tl_tasks)):
        for task in Task_master.tasks_list:
            if tl_tasks[i] == task.name:
                tppl_o = (task.name, task.start[task.cnt_o], task.end[task.cnt_o])
                timelines_o.append(tppl_o)
                task.cnt_o += 1
        i+=1
    for task in Task_master.tasks_list:
        tppl_o = (task.name, task.missed_deadlines[1:])
        m_d.append(tppl_o)
    output.append(timelines_o)
    output.append(m_d)

    print(output)
    return output

def output_EDF_CC(Task_master : PseudoQueue, tl: Timeline):
    """
    Formatting Backend output RM EDF
    input -> tasks[Task(), ...], time=int
    output -> Timelines[(name=str, blockstart=int, blockend=int), ...], misseddeadline[(name=str, timemissed=int)]

    """
    task: Task
    tl_tasks = [i[0] for i in groupby(tl.cpu_task_usage)]
    i=0
    output = []
    timelines_o = []
    m_d = [] 
    while (i < len(tl_tasks)):
        for task in Task_master.tasks_list:
            if tl_tasks[i] == task.name:
                tppl_o = (task.name, task.start[task.cnt_o], task.end[task.cnt_o], task.cpu_freqs[task.cnt_o])
                timelines_o.append(tppl_o)
                task.cnt_o += 1
        i+=1
    for task in Task_master.tasks_list:
        tppl_o = (task.name, task.missed_deadlines[1:])
        m_d.append(tppl_o)
    output.append(timelines_o)
    output.append(m_d)

    print(output)
    return output    