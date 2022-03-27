
# Dummy Tasks

taskk = { (50,12) : 'T1', (40,10) : 'T2', (30,10) : 'T3' }#120
#taskk = { (5,2) : 'T1', (6,2) : 'T2', (7,2) : 'T3', (8,2) : 'T4' } #24

#Uncomment the below lines and comment the above 

#taskk = {}

#for task in tasks_from_gui:
#    r = []
#    r.append(task.period)
#    r.append(task.exec_t)
#    a = tuple(r)
#    n = task.name
#    taskk[a]=n


p = 120 #Timeline


schedulability = False

def sch (tsk):
    s = 0
    for key in tsk:
        s = s + int(key[1]) / int(key[0])
        
    print(round(s,3))
    print()
    
    if(s <= 1):
        schedulability = True
    else:
        schedulability = False
    
    return schedulability

s = sch(taskk)

if(not s):
    print("Not Scheduable")
    print()

result=[] # A list to store the final result of algorithm
final_result = []
output = []
output_m = []
queue = [] # A list to store the Tasks
tasks = [] # A list to store all the deadlines of tasks from time T = 0 to T = p
deadline = [] # A list to store the execution times of individual tasks
release = [] # A list to store all the release times of tasks from time T = 0 to T = p
missed = [] # List for tasks that missed deadline
pending = [] # A list to store all the tasks released at a given time (current time)
current_time = 0 # A varialble to keep track of current time
change_status = False #Variables to keep track if the task execution has changed from one to another 
m = False
change_task = 'Tx'


# Adding the tasks from dictonary into the list "queue"
for v in taskk.values():
    queue.append(v)

#print(queue)
#print()

# Adding the execution times of individual tasks into the list "deadline"
for key in taskk:
    deadline.append( int(key[0]) )

dead_max = max(deadline) # finding the maximum execution time of the given tasks

# Calculating all the deadlines from time T = 0 to T = p (including the immediate deadlines after time p)
for i in range(0,len(taskk)):
    for j in range(1,p+dead_max+1):
        a = []
        if(j % deadline[i] == 0):
            a.append(j)
            a.append(queue[i])
            tasks.append(a)

tasks = sorted(tasks) # Sorting based on the deadlines
#print(tasks)
#print()

# Manually adding the time T = 0
for v in taskk.values():
    temp = []
    temp.append(0)
    temp.append(v)
    release.append(temp)
    
# Calculating all the release times from time T = 0 to T = p  
for i in range(0,len(taskk)):
    for j in range(1,p+1):
        if(j % deadline[i] == 0):
            temp = []
            temp.append(j)
            temp.append(queue[i])
            release.append(temp)

release = sorted(release) # Sorting based on the release times
#print(release)
#print()

while(current_time <= p): # Checking the condition if our current time is less than the ending time p

    # Calculating the tasks released at a given time (current time)
    for i in release:
        if(i[0] == current_time):
            temp = []
            temp.append(list(taskk.keys())[list(taskk.values()).index(i[1])][1])
            temp.append(i[1])
            pending.append(temp)

    if(m):
        r=[]
        r.append(change_task)
        r.append(current_time)
        result.append(r)
        change_status = False
        m = False

    # If the execution has changed from one task to another, We are storing the current time and the Task which was being executed till now in the list "result"
    if(len(pending)>0 and change_status and not m):
        r=[]
        r.append(change_task)
        r.append(current_time)
        result.append(r)
        change_status = False 

    # Checking if atleast one task is ready to run;
    if(len(pending)>0):
        
        e2 = True
        
        w = 0
        while(e2):
            for x in pending: # Choosing the task which has earliest deadline to run and adding that to the list "result"
                if(x[1] == tasks[w][1] and current_time < tasks[w][0] ):
                  
                    e2 = False

                    indx = -1
                    
                    for g in tasks:
                        if(g[1] == tasks[w][1]):
                            indx = tasks.index(g)
                            break

                    #print(tasks[w][1], end=" ")
                    #print(current_time)
                    #print(pending)
                    #print(tasks)

                    r=[]
                    r.append(tasks[w][1])
                    r.append(current_time)
                    result.append(r)
                
                    x[0] = x[0] - 1 #reducing the execution time of the task by 1

                    if(len(pending)==1):
                        change_status = True
                        change_task = tasks[w][1]
                        
                    current_time = current_time+1 #increasing the current time by 1

                    # If the task's execution time has become 0 (i.e., it has executed fully we are storing it to the list "result"
                    if(x[0] == 0):
                        #print(tasks[w][1], end=" ")
                        #print(current_time)
                        #print(pending)
                        #print(tasks)
                        r=[]
                        r.append(tasks[w][1])
                        r.append(current_time)
                        result.append(r)                        
                        pending.remove(x) # Removing the task from pending list, as it's execution is complete
                        tasks.pop(indx)# Removing the task from deadlines list "tasks", as it's execution is complete
  
                    break


                if(x[1] == tasks[w][1] and current_time >= tasks[w][0] ):
                    
                    e2 = False

                    indx = -1
                    
                    for g in tasks:
                        if(g[1] == tasks[w][1]):
                            indx = tasks.index(g)
                            break
                    r=[]
                    r.append(tasks[w][1])
                    r.append(current_time)
                    missed.append(r)

                    m = True
                    change_status = True
                    change_task = tasks[w][1]
                    
                    pending.remove(x)# Removing the task from pending list, as it's deadline is passed
                    tasks.pop(indx) # Removing the task from deadlines list "tasks", as it's deadline is passed

                    break
            w = w+1
                         
    else: # If there is no pending task, We are just incrementing the current time
        if(change_status):
            r=[]
            r.append(change_task)
            r.append(current_time)
            result.append(r)
            change_status = False
        current_time = current_time+1

# We are going through results and prepare a final list of tasks with the execution start time and end time

error = False
e = -1
x = 0
s = True
counter = 0

if(result[len(result)-1][0] == result[len(result)-2][0]):
    error = True
    e = result[len(result)-1][1]

while(x < len(result)-1):
    if(s):
        final_result.append(result[x])
        s = False
    if(result[x][0] == result[x+1][0]):
        x = x+1
    else:
        final_result[counter].append(result[x][1])
        counter = counter + 1
        s = True
        x = x+1
if(error):
    if(len(final_result[len(final_result)-1])<3):
        if(e>p):
            e=p
        final_result[len(final_result)-1].append(e)
    
for q in final_result:
    t = tuple(q)
    output.append(t)

print("Timeline")
print(output)
    
print()

for q in missed:
    t = tuple(q)
    output_m.append(t)

if(len(missed)>0):
    print("Tasks that missed Deadlines")
    print(output_m)
    print()
                   
            
