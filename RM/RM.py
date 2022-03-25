"""
RM Algorithm --- Rate Monothonic --- Priority based on period
Input :  Task_master dictionary, with period and execution time

Gilberto A. Lopez Astorga
14/03/22
UBC-O ENGR 467 2021W 
"""

from asyncio import tasks

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

        self.release_t0 = True # In case user doesn't wish to release task at t=0

        self.priority = 0

        self.d_it = 0               #deadline iterator
        self.deadlines = []

        self.start = []
        self.end = []

        self.released = True
        self.finished = False
        self.schedulable = True

        self.missed_current_deadline = False
        self.missed_deadlines = []


class Timeline:
    max_time = 0 

    def __init__(self, max_time = 21):
        self.time = []

        self.max_time = max_time
        
        self.cpu_task_usage = []

        self.c_time = 0
        
        self.new_release = False


def input_vars():
    # Task Number, Period, Execution
    Task_master_dummy = [Task(1,8,1), Task(2,5,2), Task(3,10,2)]

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
        if tl.c_time % task.period == 0 and tl.c_time != 0: # and not task.finished:
            task.released = True
            task.finished = False
            tl.new_release = True
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


def deadlines_gen(Task_master: Pseudo_Queue, tl: Timeline):
    # Generating deadlines
    task: Task
    for task in Task_master.tasks_list:
        dl = 0
        while(dl <= tl.max_time):
            dl = dl + task.period
            task.deadlines.append(dl)


def task_schedulable (task: Task, tl: Timeline):
    
    if ((task.exec_t + tl.c_time) < task.deadlines[task.d_it]):
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
        if task.remaining_t == 0:
            task.finished = True

    else:
        while (tl.c_time < task.deadlines[task.d_it]):
            tl.cpu_task_usage.append(task.name)
            tl.time.append(tl.c_time)
            tl.c_time += 1
            task.remaining_t -=1
        task.missed_deadlines.append(tl.c_time)
        task.remaining_t = task.exec_t     
        task.finished = True
        task.d_it += 1

    if task.remaining_t == 0:
        task.remaining_t = task.exec_t
        task.d_it +=1


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

    for task in Task_master.tasks_list:
        print(task.name)
        print('Missed Deadlines')
        print(task.missed_deadlines)
        print('At times:')
        print(task.missed_deadlines)


Task_master_dummy = input_vars()

Task_master = Pseudo_Queue(Task_master_dummy)
tl = Timeline()

schedulability_test(Task_master)

priorities(Task_master, tl)


deadlines_gen(Task_master,tl)
timeline_completion(Task_master,tl)

