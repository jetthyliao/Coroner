#!/usr/bin/env python3

##########################################################################################
#
# CSCI563: CORONER - Compiler Optimizer, Dead-code Remover
# Code by: Jessy Liao
#
##########################################################################################

import sys
import os
import copy
import CTL
import MARKSWEEP

##########################################################################################
# ABSTRACT SYNTAX TREE CLASS
##########################################################################################

class AST(object):
    def __init__(self, node_id = 0, name='start', node_type='root', children=None):
        self.id = node_id
        self.name = name
        self.node_type = node_type
        self.children = []
        self.mark = False
        if children is not None:
            for child in children:
                self.add(child)

    # used to print AST in string format
    #   can edit this to print AST in different formats
    def __repr__(self):
        return "(" + str(self.id) + " " + self.name + ")"

    def add(self, node):
        assert isinstance(node, AST)
        self.children.append(node)


##########################################################################################
# FORMATTING INPUT FILE INTO ABSTRACT SYNTAX TREE
##########################################################################################

# PARSE_INPUT: parse the input file, extract necessary info, and call create_tree to construct the AST tree
def parse_input(filename):
    if not os.path.exists(filename):
        print("Not a valid file >:C")
        sys.exit(1)

    # stores all necessary information about nodes in these two dictionaries
    # will transfer them into the AST class format afterwards
    node_children = {}
    node_values = {}

    with open(filename) as file_input:
        for line in file_input:
            line = line.strip('\n').split()
            
            # populate node_children 
            #   format: node id -> [list of children id]
            if line[0] in node_children:
                node_children[line[0]].append(line[1])
            else:
                node_children[line[0]] = [line[1]]
           
            # populate node_values with
            #   format: node id -> (node type, node name)
            if line[0] not in node_values:
                node_values[line[0]] = (line[2], line[3])
    
    # initialize starting root node
    node_name = "start"
    node_type = "root"
    # this should construct the rest of the tree
    children = [create_tree(1, node_children, node_values)] 

    # format root node as thhe top of the AST
    return AST(0, node_name, node_type, children)

# CREATE TREE: create the abstract syntax tree formatted to the AST class
def create_tree(node, children, values):
    # obtain name and type of the current node
    name = values[str(node)][1]
    node_type = values[str(node)][0]
    # initialize node_children,  will be used to create AST
    node_children = []

    # recursively search all children and make them AST nodes
    for c in children[str(node)]:
        if c != 'x':
            node_children.append(create_tree(int(c), children, values))
        else:
            node_children.append(AST(-1,"null","null",[]))
    return AST(node, name, node_type, node_children)

##########################################################################################
# DEBUGGING FUNCTIONS
#   - the following functions are mainly print functions to debug the code
##########################################################################################

def print_tree(AST):
    print(AST.name, "->", AST.node_type)
    for c in AST.children:
        print_tree(c)

##########################################################################################
# MAIN FUNCTION
##########################################################################################

def main(argv):
    if len(argv) < 2: 
        print('Usage: ./CORONER [input_file]')
        sys.exit(1)

    inpoot_file = argv[1]

    ast = parse_input(inpoot_file)

    print("\nCTL ALGORITHM: SERIAL")
    CTL.execute_ctl_serial(ast)
    
    print("\nCTL ALGORITHM: PARALLEL")
    CTL.execute_ctl_parallel(ast)

    print("\nMARK SWEEP ALGORITHM")
    MARKSWEEP.mark_sweep(ast)

    sys.exit(0)

if __name__ == '__main__':
    main(sys.argv)
