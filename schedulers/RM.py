"""
RM Algorithm --- Rate Monothonic --- Priority based on period
Input :  List of initialized 'Task' ; Max time

Gilberto A. Lopez Astorga
31/03/22
UBC-O ENGR 467 2021W - RT Embedded Systems
"""

from math import isclose
from schedulers.helpers.Classes import Task, Timeline, PseudoQueue
from schedulers.helpers.Helpers import released_tasks, deadlines_gen, task_schedulable, cpu_idle, fill_timeline

def schedulability_test(Task_master: PseudoQueue):
    """
    RM Schedulability Test
    """
    task: Task
    util = 0
    util_bound = util_bounds_RM(Task_master.tasks_list)

    for task in Task_master.tasks_list:
        util = util + (task.exec_t/task.period)

    print('Utilization from tasks:')
    print(util)
    print('Utilization bound:')
    print(util_bound)
    if (util<= util_bound):
        print("Schedulability test passed. Tasks schedulable under RM")
    else:
        print("Schedulability test not passed. Need to draw timeline to further test")

    
def util_bounds_RM(Task_master_list):
    # Getting number of tasks and getting boundary for sufficient test
    n_tasks = len(Task_master_list)
    util_bound = ((2**(1/n_tasks))-1)*n_tasks

    return util_bound


def priorities_RM(Task_master : PseudoQueue, tl: Timeline):
    #Sorting priorities based on period
    task : Task

    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.period)
    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.released, reverse = True)
    i=1
    for task in Task_master.tasks_list:
        task.priority = i
        i += 1  
    


def timeline_completion(Task_master: PseudoQueue, tl: Timeline):
    task: Task
    check_idle = 0 
    while(1):
        for task in Task_master.tasks_list:

            released_tasks(Task_master.tasks_list, tl)
            priorities_RM(Task_master,tl)

            if task.released and not task.finished and task.priority == 1:
                check_idle = 0 
                task_schedulable(task, tl)     # check if task will finish on time
                if len(task.start) != 0 and task.end[-1] == tl.c_time:
                    del(task.end[-1])
                else:
                    task.start.append(tl.c_time)
                if task.released and tl.new_release:
                    tl.new_release = False
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



def run_RM(Task_master, max_t):
    '''

    Runs RM algorithm and returns timeline

    Input: List of Task Objects
    
    Output: Dictionary, key: tasks, values: tupple with start and end times

    '''
    #
    Task_master = PseudoQueue(Task_master)

    tl = Timeline(max_time = max_t)

    schedulability_test(Task_master)

    deadlines_gen(Task_master,tl)

    timeline_completion(Task_master,tl)

    for task in Task_master.tasks_list:
        print(task.name)
        print('S:', task.start)
        print('F:', task.end)
        print('Missed deadlines:', task.missed_deadlines[1:])

    return Task_master, tl
            


