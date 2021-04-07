#!/usr/bin/env python3 

from CORONER import AST
import time
from multiprocessing import Process

##########################################################################################
#
# CSCI563: CORONER - Compiler Optimizer, Dead-code Remover (CTL ALGORITHM)
# Code by: Jessyliao
#
##########################################################################################

def execute_ctl_parallel(AST):
    start = time.time()
    p1 = Process(target=unreachable_if, args=(AST,))
    p1.start()
    p2 = Process(target=unreachable_return, args=(AST,))
    p2.start()
    p3 = Process(target=unused_variables, args=(AST,))
    p3.start() 
    p4 = Process(target=unused_parameters, args=(AST,))
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

    end = time.time()

    print("TOTAL TIME:     ", (end-start))

def execute_ctl_serial(AST):
    start1 = time.time()
    unreachable_if(AST)
    end1 = time.time()
    
    start2 = time.time()
    unreachable_return(AST)
    end2 = time.time()
    
    start3 = time.time()
    unused_variables(AST)
    end3 = time.time()
    
    start4 = time.time()
    unused_parameters(AST)
    end4 = time.time()

    #print("Time (If):      ", (end1-start1))
    #print("Time (Return):  ", (end2-start2)) 
    #print("Time (Vars):    ", (end3-start3))
    #print("Time (Params):  ", (end4-start4))

    print("TOTAL TIME:     ", (end4-start1))


########################################
# Case 1: CHECK FOR UNREACHABLE IF
########################################
def unreachable_if(AST):
    states, if_states = check_if(AST, {}, {})
    dead_if = find_unreachable_if(if_states)
    #print("States:         ", states)
    #print("If:             ", if_states)
    if dead_if == []:
        print("Dead If:         None")
    else:
        print("Dead If:        ", dead_if)

def check_if(AST, states, if_states):
    # if node is a if statement check the conditional statement, add it to the if_states dictionary
    # if_states will be used to check if all conditions were all true or false (this leads to unreachable code)
    if AST.node_type == "if":
        cond = int(check_condition(AST.children[0], states))
        if AST in if_states:
            if_states[AST].append(cond)
        else:
            if_states[AST] = [cond]
    
    # add parameter values into states dictionary
    if AST.node_type == "parameter" and AST.id == 2:
        for p in AST.children:
            states[p.name] = int(p.children[0].name)

    # update states or add states into states dictionary
    if AST.node_type == "assign":
        value = ""
        if AST.children[1].node_type == "operator":
            value = perform_operation(AST.children[1], states)
        elif AST.children[1].node_type == "value":
            value = AST.children[1].name
        if value != "":
            states[AST.children[0].name] = value
    
    # if encountered while loop, enter recursion 
    if AST.node_type == "while":
        while check_condition(AST.children[0], states):
            for c in range(1, len(AST.children)):
                states, if_states = check_if(AST.children[c], states, if_states)
    else:
        for c in AST.children:
            check_if(c, states, if_states)

    return states, if_states

def find_unreachable_if(if_states):
    answer = []
    for f in if_states:
        current = if_states[f][0]
        constant_if = True
        for cond in if_states[f]:
            if current != cond:
                constant_if = False
        if constant_if:
            answer.append((f,current))

    return answer

########################################
# Case 2: CHECK FOR UNREACHABLE RETURN
########################################
def unreachable_return(AST):
    states, dead_return, ignore = check_return(AST, {}, "", False)
    if not ignore:
        print("Dead Return:     None") 
    else:
        print("Dead Return:    ", dead_return)

def check_return(AST, states, node, returned):

    if AST.node_type == "return" and not returned:
        returned = True
        node = AST
        return states, node, returned
    # add parameter values into states dictionary
    if AST.node_type == "parameter" and AST.id == 2:
        for p in AST.children:
            states[p.name] = int(p.children[0].name)

    # update states or add states into states dictionary
    if AST.node_type == "assign":
        value = ""
        if AST.children[1].node_type == "operator":
            value = perform_operation(AST.children[1], states)
        elif AST.children[1].node_type == "value":
            value = AST.children[1].name
        if value != "":
            states[AST.children[0].name] = value
    
    # if encountered while loop, enter recursion 
    if AST.node_type == "while":
        while check_condition(AST.children[0], states):
            for c in range(1, len(AST.children)):
                states, node, returned= check_return(AST.children[c], states, node, returned)
                if returned:
                    break
            if returned:
                break
    else:
        for c in AST.children:
            states, node, returned = check_return(c, states, node, returned)
            if returned:
                break

    return states, node, returned

    
########################################
# Case 3: CHECK FOR UNUSED VARIABLES
########################################
def unused_variables(AST):
    alias, used, dead, ignore = check_variables(AST, [], {}, [], False)
    dead_variables = find_dead_variables(used, alias, dead)
    #print("Alias:          ", alias)
    #print("Used:           ", used)
    #print("Dead:           ", dead)
    if dead_variables == []:
        print("Dead Variables:  None")
    else:
        print("Dead Variables: ", dead_variables)
    
# check_variables: get all used variables and all alias of variables
#   alias: assign nodes should make the variables it assigning to be treated the same
#       eg. d = c + w
#           if d is used, c and w is used
def check_variables(AST, used, alias, dead, returned):
    if not returned:
        # handle alias variables
        if AST.node_type == "assign": 
            alias[AST.children[0]] = expand(AST.children[1], AST.children[0], [])

        # paramter nodes (function calls) are useful variables
        if AST.node_type == "parameter" and AST.id != 2:
            used += expand(AST, AST, [])

        # check if its used in conditional
        if AST.node_type == "comparator":
            used += expand(AST,AST,[])

        # checks for return statement, stops after that (after return everything should be unreachable)
        if AST.node_type == "return":
            used += expand(AST,AST,[])
            return alias, used, dead, True
    else:
        dead += expand(AST,AST,[])

    # continue traversal
    for c in AST.children: 
        alias, used, dead, returned = check_variables(c, used, alias, dead, returned)
    
    return alias, used, dead, returned

def find_dead_variables(used, alias, dead):
    temp_used = []

    # iterate through alias variables and see if one of its alias exists in used
    # if it does, then it isnt dead
    for u in used:
        largest_alias = AST(0,"","",[])
        max_alias = u.id
        for a in alias:
            if u.name in a.name and largest_alias.id < a.id and a.id < max_alias:
                largest_alias = a
        if largest_alias.name != "":
            used += alias[largest_alias]
            temp_used.append(largest_alias)

    used += temp_used

    # for all alias variables not in used, it is dead
    dead_variables = []
    for a in alias:
        if a not in used:
            dead_variables.append(a)

    for d in dead:
        if d not in dead_variables:
            dead_variables.append(d)


    return dead_variables
        
########################################
# Case 4: CHECK FOR UNUSED PARAMETERS
########################################
def unused_parameters(AST):
    alias, used, dead, params, ignore = check_parameters(AST, [], {}, [], set(), False)
    dead_parameters = find_dead_parameters(used, alias, params)
    #print("Alias:          ", alias)
    #print("Used:           ", used)
    #print("Dead:           ", dead)
    if dead_parameters == set():
        print("Dead Params:     None")
    else:
        print("Dead Params:    ", dead_parameters)
 

def check_parameters(AST, used, alias, dead, params, returned):
    if not returned:
        # handle alias variables
        if AST.node_type == "assign": 
            alias[AST.children[0]] = expand(AST.children[1], AST.children[0], [])

        # handle the parameters (differentiates between parameter from this function and parameters from calling functions)
        if AST.node_type == "parameter" and AST.id != 2:
            used += expand(AST,AST,[])
        elif AST.node_type == "parameter" and AST.id == 2:
            temp = expand(AST,AST,[])
            for t in temp: 
                params.add(t.name)

        # check if its used in conditional
        if AST.node_type == "comparator":
            used += expand(AST,AST,[])

        # checks for return statement, stops after that (after return everything should be unreachable)
        if AST.node_type == "return":
            used += expand(AST,AST,[])
            return alias, used, dead, params, True
    else:
        dead += expand(AST,AST,[])

    # continue traversal
    for c in AST.children: 
        alias, used, dead, params, returned = check_parameters(c, used, alias, dead, params, returned)
    
    return alias, used, dead, params, returned

def find_dead_parameters(used, alias, params):
    temp_used = []

    # iterate through alias variables and see if one of its alias exists in used
    # if it does, then it isnt dead
    for u in used:
        largest_alias = AST(0,"","",[])
        max_alias = u.id
        for a in alias:
            if u.name in a.name and largest_alias.id < a.id and a.id < max_alias:
                largest_alias = a
        if largest_alias.name != "":
            used += alias[largest_alias]
            temp_used.append(largest_alias)

    used += temp_used

    for u in used: 
        if u.name in params:
            params.remove(u.name)

    return params
 












# expand: get all variables in a subtree
def expand(AST, current, variables):
    if AST.node_type == "variable" and current.name != AST.name:
        variables.append(AST)

    for c in AST.children:
        expand(c, current, variables)

    return variables

def check_condition(AST, states):
    if AST.node_type == "connector":
        if AST.name != "!":
            var1 = check_condition(AST.children[0], states)
            var2 = check_condition(AST.children[1], states)
        if AST.name == "&&":
            return var1 and var2
        if AST.name == "||":
            return var1 or var2
        if AST.name == "!":
            return not(check_condition(AST.children[0], states))
             
    if AST.node_type == "comparator":
        var1 = 0
        var2 = 0
    
        if AST.children[0].node_type == "variable":
            var1 = states[AST.children[0].name]
        if AST.children[0].node_type == "value":
            var1 = int(AST.children[0].name)
        if AST.children[0].node_type == "operator":
            var1 = perform_operation(AST.children[0], states)
        
        if AST.children[1].node_type == "variable":
            var2 = states[AST.children[1].name]
        if AST.children[1].node_type == "value":
            var2 = int(AST.children[1].name)
        if AST.children[1].node_type == "operator":
            var2 = perform_operation(AST.children[1], states)

        if AST.name == "==":
            return (var1 == var2)
        if AST.name == "<":
            return (var1 < var2)
        if AST.name == ">":
            return (var1 > var2)
        if AST.name == "<=":
            return (var1 <= var2)
        if AST.name == ">=":
            return (var1 >= var2)
        if AST.name == "!=":
            return (var1 != var2)
 

def perform_operation(AST, states):

    if AST.children[0].node_type == "value":
        var1 = int(AST.children[0].name)
    else:
        var1 = states[AST.children[0].name]
    if AST.children[1].node_type == "operator": 
        var2 = perform_operation(AST.children[1], states)
    else:
        if AST.children[1].node_type == "value":
            var2 = int(AST.children[1].name)
        else: 
            var2 = states[AST.children[1].name]

    if AST.name == "+":
        value = int(var1) + int(var2)
    elif AST.name == "-":
        value = int(var1) -  int(var2)
    elif AST.name == "*":
        value = int(var1) * int(var2)
    elif AST.name == "/":
        value = int(var1) / int(var2)
 
    return value
