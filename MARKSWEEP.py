#!/usr/bin/env python3 

#from CORONER import AST
import time
from multiprocessing import Process

##########################################################################################
#
# CSCI563: CORONER - Compiler Optimizer, Dead-code Remover (MARK SWEEP ALGORITHM)
# Code by: Jessyliao
#
##########################################################################################

def mark_sweep(AST):
    start = time.time()
    mark(AST, {}, False)
    dead = sweep(AST,[])
    print("Dead Variables: ", dead)
    end = time.time()
    print("TOTAL TIME:     ", (end-start))

def mark(AST,states,returned):
    AST.mark = True
    if AST.node_type == "return" and not returned:
        returned = True
        return states, returned
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
                states, returned= mark(AST.children[c], states, returned)
                if returned:
                    break
            if returned:
                break
    else:
        for c in AST.children:
            states, returned = mark(c, states, returned)
            if returned:
                break

    return states, returned

def sweep(AST, dead):
    if not AST.mark and AST.node_type == "variable":
        dead.append(AST)
    for c in AST.children:
        sweep(c, dead)
    return dead

# expand: get all variables in a subtree
def expand(AST, current, variables):
    AST.mark = True
    if AST.node_type == "variable" and current.name != AST.name:
        variables.append(AST)

    for c in AST.children:
        expand(c, current, variables)

    return variables

def check_condition(AST, states):
    AST.mark = True
    for c in AST.children:
        c.mark = True
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
