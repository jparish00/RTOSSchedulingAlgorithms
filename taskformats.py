"""
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