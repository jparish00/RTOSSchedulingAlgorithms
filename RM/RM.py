"""
RM Algorithm --- Rate Monothonic --- Priority based on period
Input :  Task_master dictionary, with period and execution time

Gilberto A. Lopez Astorga
14/03/22
UBC-O ENGR 467 2021W 
"""

class Task:
  def __init__(self, number, period, exec):
    self.name = 'T' + str(number) 
    self.period = period
    self.exec_t = exec
    self.missed_current_deadline = False
    self.missed_deadlines = 0
    self.missed_deadlines_times = []
    self.relative_t = 1
    self.current_deadline = 0
    self.deadlines = []


class Timeline:
  def __init__(self, max_time = 21):
    self.current_time = 0
    self.current_task = 0 
    self.current_deadline = 0
    self.missed_deadlines = 0
    self.rtos_type = 'HARD'
    self.schedulable = False
    self.max_time = max_time
    self.cpu_task_usage = []
    self.queue_next = []


def input_vars():
    Task_master_dummy = [Task(1,5,6), Task(2,8,3), Task(3,10,2)]

    return Task_master_dummy


def schedulability_test(Task_master):
    util = 0
    util_bound = util_bounds(Task_master)

    for task in Task_master:
        util = util + (task.exec_t/task.period)

    print('Utilization from tasks:')
    print(util)
    print('Utilization bound:')
    print(util_bound)
    if (util<= util_bound):
        print("Schedulability test passed. Tasks schedulable under RM")
    else:
        print("Schedulability test not passed. Need to draw timeline to further test")


def util_bounds(Task_master):
    # Getting number of tasks and getting boundary for sufficient test
    n_tasks = len(Task_master)
    util_bound = ((2**(1/n_tasks))-1)*n_tasks

    return util_bound


def priorities(Task_master):
    #Sorting priorities based on period
    return sorted(Task_master, key=lambda x: x.period)


def deadlines_gen(tasks, tl: Timeline):
    # Generating deadlines
    task: Task
    for task in tasks:
        dl = 0
        while(dl <= tl.max_time):
            dl = dl + task.period
            task.deadlines.append(dl)


def missed_deadline(task: Task, tl: Timeline):
    if (task.current_deadline < tl.current_time):
        task.missed_deadlines =+ 1
        task.missed_current_deadline = True
        task.missed_deadlines_times.append(tl.current_time)


def timeline_completion(Tasks, tl: Timeline):
    task: Task
    while (tl.current_time <= tl.max_time): ### Make sure it exits when max time exceeded, currently exits when task finishes and time exceeds
        
        for task in Tasks:
            task.current_deadline = tl.current_time + task.period

            while(tl.current_time < task.current_deadline and task.missed_current_deadline == False):
                tl.cpu_task_usage.append(task.name)
                tl.current_time += 1
            missed_deadline(task,tl)
            task.missed_current_deadline = False
            
    print(tl.cpu_task_usage)

    for task in Tasks:
        print(task.name)
        print('Missed Deadlines')
        print(task.missed_deadlines)
        print('At times:')
        print(task.missed_deadlines_times)


Task_master_dummy = input_vars()

schedulability_test(Task_master_dummy)

Task_master_dummy = priorities(Task_master_dummy)

tl = Timeline()

timeline_completion(Task_master_dummy,tl)