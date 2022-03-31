class PseudoQueue:
    tasks_list = []
    def __init__(self, tasks_list):
        self.tasks_list = tasks_list


class Task:
    period = 0  #### Should only accept INTs
    exec_t = 0  #### Should only accept INTs
    priority = 0 
    invocations =[]
    def __init__(self, number, period, exec, invocations):
        self.name = 'T' + str(number) 
        self.period = period
        self.exec_t = exec
        
        self.remaining_t = exec

        self.invocations = invocations

        self.frequencies =[]

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

        self.cnt_o = 0

        self.cpu_freqs = []


class Timeline:
    max_time = 18 
    available_frequencies = []

    def __init__(self, available_frequencies = [], max_time=18):
        self.time = []

        self.max_time = max_time
        
        self.cpu_task_usage = []

        self.c_time = 0
        
        self.new_release = False

        self.available_frequencies = available_frequencies