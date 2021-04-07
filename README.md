# Coroner

Coroner is a compiler optimizer that eliminates dead code. It does this by using computation tree logic (CTL) on an abstract syntax tree (AST), a common data structure used in compilers. 

The most popular algorithm for removing dead code is the mark-sweep algorithm. I implemented a naive version of this so that I could compare it to my CTL algorithm. I also created a version of the CTL code that utilizes parallelization to see if I could get better performance output. 

There is also a paper attached that goes into further details about the code. 

## Installation

```     python3 CORONER.py [input file]```

Input files are given in the inputs directory. They are formatted as such: 

```     [node id] [child id] [type of code] [value]```

## Notes

Due to time constraint I was not able to add as many cases for dead code elimination. With more time I would like to have a larger sample size of AST to test on.
