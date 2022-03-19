
def schEDF(tsk):
    s = 0
    for key in tsk:
        s = s + int(key[1]) / int(key[0])
        
    print(round(s,3))
    print()
    
    if(s <= 1):
        schedulability = True
    else:
        schedulability = False
    
    return schedulability, s

# I need help with the main algorithm :(