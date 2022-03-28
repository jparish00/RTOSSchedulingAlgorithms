"""
RM Algorithm --- Rate Monothonic --- Priority based on period
Input :  Task_master dictionary, with period and execution time

Gilberto A. Lopez Astorga
14/03/22
UBC-O ENGR 467 2021W 
"""

class Pseudo_Queue:
    tasks_list = []
    def __init__(self, tasks_list):
        self.tasks_list = tasks_list


class Task:
    period = 0
    exec_t = 0
    priority = 0

    def __init__(self, number, period, exec):
        self.name = 'T' + str(number) 
        self.period = period
        self.exec_t = exec
        
        self.remaining_t = exec

        self.priority = 0

        self.d_it = 0               #deadline iterator
        self.deadlines = []

        self.start = []
        self.end = []

        self.released_ts = ['ignore']

        self.released = True
        self.finished = False
        self.schedulable = True

        self.missed_deadlines = ['ignore']


class Timeline:
    max_time = 0 

    def __init__(self, max_time = 18):
        self.time = []

        self.max_time = max_time
        
        self.cpu_task_usage = []

        self.c_time = 0
        
        self.new_release = False


def dummy_input_vars():
    # Task Number, Period, Execution
    # Task_master_dummy = [Task(1,8,7), Task(2,5,2), Task(3,10,2)]
    # Task_master_dummy = [Task(1,8,1), Task(2,15,3), Task(3,20,4), Task(4,22,6)]
    # Task_master_dummy = [Task(1,5,3), Task(2,8,3)]
    # Task_master_dummy = [Task(1,8,1), Task(2,5,4), Task(3,10,2)]
    Task_master_dummy = [Task(1,4,1), Task(2,5,2), Task(3,7,2)]

    return Task_master_dummy


def schedulability_test(Task_master: Pseudo_Queue):
    util = 0
    util_bound = util_bounds(Task_master.tasks_list)

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


def util_bounds(Task_master_list):
    # Getting number of tasks and getting boundary for sufficient test
    n_tasks = len(Task_master_list)
    util_bound = ((2**(1/n_tasks))-1)*n_tasks

    return util_bound


def released_tasks (tasks, tl: Timeline):
    task: Task
    for task in tasks:
        if tl.c_time % task.period == 0 and tl.c_time != 0 and task.released_ts[-1] != tl.c_time: # and not task.finished:
            if task.remaining_t !=0 and not task.finished:# and task.deadlines[task.d_it-1] <= tl.c_time:
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


def priorities(Task_master : Pseudo_Queue, tl: Timeline):
    #Sorting priorities based on period
    task : Task

    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.period)
    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.released, reverse = True)
    i=1
    for task in Task_master.tasks_list:
        task.priority = i
        i += 1


def priorities_EDF(Task_master : Pseudo_Queue, tl: Timeline):
    #Sorting priorities based on period
    task : Task

    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.deadlines[x.d_it])
    Task_master.tasks_list = sorted(Task_master.tasks_list, key=lambda x: x.released, reverse = True)
    i=1
    for task in Task_master.tasks_list:
        task.priority = i
        i += 1


def deadlines_gen(Task_master: Pseudo_Queue, tl: Timeline):
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
    

def fill_timeline(task: Task,tl: Timeline, Task_master : Pseudo_Queue):
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


def cpu_idle(tl: Timeline):
    tl.time.append(tl.c_time)
    tl.cpu_task_usage.append('IDLE')
    tl.c_time +=1


def timeline_completion(Task_master: Pseudo_Queue, tl: Timeline):
    task: Task
    check_idle = 0 
    while(1):
        for task in Task_master.tasks_list:

            released_tasks(Task_master.tasks_list, tl)
            priorities(Task_master,tl)

            if task.released and not task.finished and task.priority == 1:
                check_idle = 0 
                task_schedulable(task, tl)     # check if task will finish on time
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


def timeline_completion_EDF(Task_master: Pseudo_Queue, tl: Timeline):
    task: Task
    check_idle = 0 
    while(1):
        for task in Task_master.tasks_list:

            released_tasks(Task_master.tasks_list, tl)
            priorities_EDF(Task_master,tl)

            if task.released and not task.finished and task.priority == 1:
                check_idle = 0 
                task_schedulable(task, tl)     # check if task will finish on time
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


def run_RM(Task_master):
    '''

    Runs RM algorithm and returns timeline

    Input: List of Task Objects
    
    Output: Dictionary, key: tasks, values: tupple with start and end times

    '''
    #
    Task_master = Pseudo_Queue(Task_master)

    tl = Timeline()

    schedulability_test(Task_master)

    deadlines_gen(Task_master,tl)

    timeline_completion(Task_master,tl)

    for task in Task_master.tasks_list:
        print(task.name)
        print('S:', task.start)
        print('F:', task.end)
        print('Missed deadlines:', task.missed_deadlines[1:])


def run_EDF(Task_master):
    '''

    Runs EDF algorithm and returns timeline

    Input: List of Task Objects
    
    Output: Dictionary, key: tasks, values: tupple with start and end times

    '''
    #
    Task_master = Pseudo_Queue(Task_master)

    tl = Timeline()

    # schedulability_test(Task_master)

    deadlines_gen(Task_master,tl)

    timeline_completion_EDF(Task_master,tl)

    for task in Task_master.tasks_list:
        print(task.name)
        print('S:', task.start)
        print('F:', task.end)
        print('Missed deadlines:', task.missed_deadlines[1:])



Task_master = dummy_input_vars()

run_EDF(Task_master)


