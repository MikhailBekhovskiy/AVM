# AVM
Program for Master's thesis
The work can be roughly divided in following stages:
1. Creating framework for multivariable polynomial symbolic algebra (including symb. derivatives) (fine-tuned for this project) Done
2. Implementing Additional Variables Method algorithms for multivariable functions and PDE systems (introduced by late L. K. Babadzhanyants) Done
3. Designing and implementing AVM Library of functions TODO
3.1 Adding compatibility for non-autonomous parametric library systems
3.2 Implementing external storage
(4. Create GUI\) Primitive but sufficient text file interface created.
References to be added.


Currently program works for transforming systems of functions and calculating their 1st order symbolic derivatives or transforming PDE systems to polynomial form. Your input system has to be described in 'scrolls/[input_file]' in a fashion similar to examples (input_small, input_big, input_de_small, input_de_big). 
NB! F or DE mode, independent variables explicitly specified and blank line at the end (user-friendliness is not a priority ATM, expressions are parsed with \n last symbol in mind). 
Special functions may be defined with parameters. Parameters values may be symbolic or numeric. See example input files.
Readme will be updated as needed.
Launch main.py, after changing input file name there as required