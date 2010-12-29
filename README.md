Sudoku solver
=============

This script solves sudoku puzzles. Puzzles are defined in file like 10.in:

    43..1..89
    6..9.8..1
    ..1...2..
    .4.3.7.9.
    8...2...3
    .5.1.9.4.
    ..8...6..
    5..8.4..7
    27..3..18

Numbers 1-9 are recognized as numbers, other characters marks an empty cell.

Program accepts a single command line parameter - name of a file with puzzle to solve:

    [130] SegFault (21:35) sudoku > ./sudoku.py 10.in 
    Solution
    ========
    435 612 789
    627 958 431
    981 743 265
    
    142 387 596
    869 425 173
    753 169 842
    
    398 271 654
    516 894 327
    274 536 918

How does it works?
------------------
Each cell in the puzzle keeps set of possible values. When there is just one possible value, fill the cell with it.

If there is just one place to put a certain number in a row, a column or a square, put it to its cell.

When a cell is filled, possible values are recomputed. If these heuristics are not able to solve the puzzle, the first, most problematic cell (with most possible values) is chosen and DFS (Depth first search) algorithm is used.

Examples
--------
*.in files are example files taken from [Sudoku book](http://www.martinus.sk/?uItem=23442).
