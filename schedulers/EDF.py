"""
EDF Algorithm --- Earliest Deadline First --- Priority based on deadline
Input :  List of initialized 'Task' ; Max time

Gilberto A. Lopez Astorga
31/03/22
UBC-O ENGR 467 2021W - RT Embedded Systems
"""

from schedulers.helpers.Classes import Task, Timeline, PseudoQueue
from schedulers.helpers.Helpers import released_tasks, priorities, deadlines_gen, task_schedulable, cpu_idle, fill_timeline


def schedulability_test_EDF_WC(Task_master: PseudoQueue):
    """
    EDF Schedulability test for Worst Case
    """
    task: Task
    util = 0

    for task in Task_master.tasks_list:
        util = util + (task.exec_t/task.period)

    if (util <= 1):
        return (True, util)
    else:
        return (False, util)

def timeline_completion_EDF(Task_master: PseudoQueue, tl: Timeline):
    task: Task
    check_idle = 0 
    while(1):
        for task in Task_master.tasks_list:

            released_tasks(Task_master.tasks_list, tl)
            priorities(Task_master,tl,'EDF')

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


def run_EDF(Task_master, max_t):
    '''
    Runs EDF algorithm and returns timeline

    Input: List of Task Objects
    
    Output: Dictionary, key: tasks, values: tupple with start and end times

    '''
    tl = Timeline(max_time = max_t)

    schedulability_test_EDF_WC(Task_master)

    deadlines_gen(Task_master,tl)

    timeline_completion_EDF(Task_master,tl)

    return Task_master, tl


            
            
