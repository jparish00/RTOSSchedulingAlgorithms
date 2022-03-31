"""
RM Algorithm --- Rate Monothonic --- Priority based on period
Input :  Task_master dictionary, with period and execution time

Gilberto A. Lopez Astorga
14/03/22
UBC-O ENGR 467 2021W 
"""

from schedulers.helpers.Classes import Task, Timeline, PseudoQueue
from schedulers.helpers.Helpers import released_tasks


def schedulability_test_EDF_WC(Task_master: PseudoQueue):
    task: Task
    util = 0

    for task in Task_master.tasks_list:
        util = util + (task.exec_t/task.period)

    print('Utilization from tasks:')
    print(util)

    if (util <= 1):
        print("Tasks schedulable under EDF")
    else:
        print("Tasks are not schedulable under EDF")


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
    

def fill_timeline(task: Task,tl: Timeline, Task_master : PseudoQueue):
    if task.schedulable:
        while(task.remaining_t != 0): 
            task.remaining_t -=1
            tl.cpu_task_usage.append(task.name)
            tl.time.append(tl.c_time)
            tl.c_time += 1
            released_tasks(Task_master.tasks_list, tl)
            if tl.new_release:
                break

    else:
        while (tl.c_time < task.deadlines[task.d_it]):
            tl.cpu_task_usage.append(task.name)
            tl.time.append(tl.c_time)
            tl.c_time += 1
            task.remaining_t -=1
            released_tasks(Task_master.tasks_list, tl)
            if tl.new_release:
                break
        task.remaining_t = task.exec_t     
        task.finished = True
        if len(task.deadlines)-1 > task.d_it:
            task.d_it += 1

    if task.remaining_t == 0:
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


def timeline_completion_EDF(Task_master: PseudoQueue, tl: Timeline):
    task: Task
    check_idle = 0 
    while(1):
        for task in Task_master.tasks_list:

            released_tasks(Task_master.tasks_list, tl)
            priorities_EDF(Task_master,tl)

            if task.released and not task.finished and task.priority == 1:
                check_idle = 0 
                task_schedulable(task, tl)     # check if task will finish on time
                if len(task.start) != 0 and task.end[-1] == tl.c_time:
                    del task.end[-1] 
                else:
                    task.start.append(tl.c_time)
                fill_timeline(task,tl, Task_master)         # filling timeline with task usage
                task.end.append(tl.c_time)
            else:
                check_idle +=1
                if check_idle == len(Task_master.tasks_list):
                    cpu_idle(tl)
                    check_idle = 0

            if (tl.c_time > tl.max_time):
                break
        else:
            continue
        break
    
    print(tl.cpu_task_usage)    


def format_output(Task_master):
    task: Task
    
    for task in Task_master:
        x=1


def run_EDF(Task_master, max_t):
    '''
    Runs EDF algorithm and returns timeline

    Input: List of Task Objects
    
    Output: Dictionary, key: tasks, values: tupple with start and end times

    '''
    #
    Task_master = PseudoQueue(Task_master)

    tl = Timeline(max_time = max_t)

    # schedulability_test(Task_master)

    deadlines_gen(Task_master,tl)

    timeline_completion_EDF(Task_master,tl)

    for task in Task_master.tasks_list:
        print(task.name)
        print('S:', task.start)
        print('F:', task.end)
        print('Missed deadlines:', task.missed_deadlines[1:])

    return Task_master, tl


            
            
