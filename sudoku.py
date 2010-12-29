#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Created by Izidor "iyonius" Matušov <izidor.matusov@gmail.com>
#            on 29.12.2010

import sys
import copy
import logging

logger = logging.getLogger()

class SudokuFileException(Exception): pass

def readSudoku(fileName):
    """ Parse file with sudoku """
    sudoku = []

    f = open(fileName, "r")
    for line in f.readlines():
        line = line.strip()
        if len(line) != 9:
            raise SudokuFileException("Each line must have 9 items")

        lineItems = []

        for item in line:
            if ord('1') <= ord(item) <= ord('9'):
                lineItems.append( (ord(item) - ord('0'), None) )
            else:
                lineItems.append( (None, [1,2,3,4,5,6,7,8,9]) )

        sudoku.append(lineItems)

    if len(sudoku) != 9:
        raise SudokuFileException("Sudoku should have 9 lines")

    return sudoku

def printBoard(board):
    """ Print current state of board """

    hSpace = 3
    for line in board:
        output = ""

        vSpace = 3
        for number, possible in line:
            if vSpace <= 0:
                output += " "
                vSpace = 3
            vSpace -= 1

            if number is None:
                output += "." 
            else:
                output += str(number)

        if hSpace <= 0:
            print("")
            hSpace = 3
        hSpace -= 1
        print(output)

def printPossible(board):
    for y, line in enumerate(board):
        for x, (number, possible) in enumerate(line):
            if number is None:
                print("[%d][%d] ?: %s" % (y, x,possible))
    print()

def isUniqueList(l):
    """ Each item should be in the list just once """
    for item in l:
        if l.count(item) != 1:
            return False

    return True

def checkInRows(board):
    """ There should not be two same numbers in one row """
    for y, line in enumerate(board):
        numbers = [num for num, pn in line if num is not None]

        if not isUniqueList(numbers):
            return False

    return True

def checkInCols(board):
    """ There should not be two same numbers in one column """
    for x in range(len(board[0])):

        numbers = []
        for line in board:
            num, pn = line[x]

            if num is not None:
                numbers.append(num)

        if not isUniqueList(numbers):
            return False

    return True

def checkInOneSqr(board, dy, dx):
    """ Each number should be unique in a square """
    numbers = []

    for y in range(3):
        for x in range(3):
            num, pn = board[dy+y][dx+x]
            if num is not None:
                numbers.append(num)

    return isUniqueList(numbers)

def checkInSqrs(board):
    """ Check each square """
    for dy in range(0, 9, 3):
        for dx in range(0, 9, 3):
            if not checkInOneSqr(board, dy, dx):
                return False
    return True

def checkBoard(board):
    """ Is board in correct state? Is no rule broken? """
    return checkInRows(board) and checkInCols(board) and checkInSqrs(board)

def isSolved(board):
    """ Check if everything has been solved """
    for line in board:
        for number, possible in line:
            if number is None:
                return False

    return True

def listDifference(a, b):
    """ Make a-b on lists """
    return list(set(a).difference(set(b)))

def repairPossibleNumbersInRows(board):
    """ Remove possible values by checking in a row """
    for y, line in enumerate(board):
        numbers = [num for num, pn in line if num is not None]
        for x, (num, possibleNumbers) in enumerate(line):
            if num is None:
                board[y][x] = (num, listDifference(possibleNumbers, numbers))
    return board

def repairPossibleNumbersInCols(board):
    """ Remove possible values by checking in a column """
    for x in range(len(board[0])):

        numbers = []
        for line in board:
            num, pn = line[x]

            if num is not None:
                numbers.append(num)

        for line in board:
            num, pn = line[x]
            if num is None:
                line[x] = (num, listDifference(pn, numbers))

    return board

def repairPossibleNumbersInOneSqr(board, dy, dx):
    """ Remove possible values by checking in a square """
    numbers = []

    for y in range(3):
        for x in range(3):
            num, pn = board[dy+y][dx+x]
            if num is not None:
                numbers.append(num)

    for y in range(3):
        for x in range(3):
            num, pn = board[dy+y][dx+x]
            if num is None:
                board[dy+y][dx+x] = (num, listDifference(pn, numbers))

    return board

def repairPossibleNumbersInSqrs(board):
    """ Check each square """
    for dy in range(0, 9, 3):
        for dx in range(0, 9, 3):
            board = repairPossibleNumbersInOneSqr(board, dy, dx)
    return board

def repairPossibleNumbers(board):
    """ Update possible values """
    board = repairPossibleNumbersInRows(board)
    board = repairPossibleNumbersInCols(board)
    board = repairPossibleNumbersInSqrs(board)
    return board

def listCommonItem(a, b):
    """ Check if two list has just one common item """
    result = list(set(a).intersection(set(b)))

    if len(result) != 1:
        return None
    else:
        return result[0]

def fillNumbersInRows(board):
    """ Insert missing numbers into a row """
    changed = False

    for y, line in enumerate(board):
        numbers = [num for num, pn in line if line.count(num) == 1]
        for x, (num, pn) in enumerate(line):
            if num is None and listCommonItem(pn, numbers) is not None:
                num = listCommonItem(pn, numbers)
                logger.debug("FillRow change at [%d][%d] to %d" % (y, x, num))
                line[x] = (num, None)
                changed = True

    return changed, board

def fillNumbersInCols(board):
    """ Insert missing numbers into a column """
    changed = False

    for x in range(len(board[0])):
        counts = [0] * 10

        for line in board:
            num, pn = line[x]
            if num is None:
                for possible in pn:
                    counts[possible] += 1

        numbers = [num for num, count in enumerate(counts) if count == 1]

        for y, line in enumerate(board):
            num, pn = line[x]
            if num is None and listCommonItem(pn, numbers) is not None:
                num = listCommonItem(pn, numbers)
                logger.debug("FillCol change at [%d][%d] to %d" % (y, x, num))
                line[x] = (num, None)
                changed = True

    return changed, board

def fillInOneSqr(board, dy, dx):
    """ Insert missing numbers into a square """
    occurence = []
    changed = False

    for y in range(3):
        for x in range(3):
            num, pn = board[dy+y][dx+x]
            if num is None:
                occurence += pn

    numbers = [num for num in occurence if occurence.count(num) == 1]

    for y in range(3):
        for x in range(3):
            num, pn = board[dy+y][dx+x]
            if num is None and listCommonItem(pn, numbers) is not None:
                num = listCommonItem(pn, numbers)
                logger.debug("FillSqr change at [%d][%d] to %d" % (y+dy, x+dx, num))
                board[y+dy][x+dx] = (num, None)
                changed = True

    return changed, board

def fillNumbersInSqrs(board):
    """ Check each square for filling """
    change = False
    for dy in range(0, 9, 3):
        for dx in range(0, 9, 3):
            changeInSqr, board = fillInOneSqr(board, dy, dx)
            change = change or changeInSqr

    return change, board

def fillSureNumbers(board):
    """ Fill items with just one possible number """
    changed = False
    for y, line in enumerate(board):
        for x, (number, possibleNumbers) in enumerate(line):
            if number is None and len(possibleNumbers) == 1:
                number = possibleNumbers[0]
                board[y][x] = (number, None)
                logger.debug("Change at [%d][%d] to %d" % (y,x,number))
                changed = True

    return changed, board

def solveSudoku(board):
    """ Method for solving a sudoku puzzle 
    
    Try to solve the puzzle using heuristics.
    If it fails, "guess" value by using 
    Depth-First Search algorithm.
    """

    changed = True
    while not isSolved(board) and changed:
        if logger.isEnabledFor(logging.DEBUG):
            print("-"*50)
            printBoard(board)
            print()

        if not checkBoard(board):
            return

        changed = False

        board = repairPossibleNumbers(board)
        if logger.isEnabledFor(logging.DEBUG):
            printPossible(board)
        change, board = fillSureNumbers(board)


        if change:
            changed = True

            board = repairPossibleNumbers(board)
            if logger.isEnabledFor(logging.DEBUG):
                printPossible(board)

        change, board = fillNumbersInRows(board)

        if change:
            changed = True
            board = repairPossibleNumbers(board)
            if logger.isEnabledFor(logging.DEBUG):
                printPossible(board)

        change, board = fillNumbersInCols(board)

        if change:
            changed = True
            board = repairPossibleNumbers(board)
            if logger.isEnabledFor(logging.DEBUG):
                printPossible(board)

        change, board = fillNumbersInSqrs(board)

        changed = changed or change
    # End of main while

    if isSolved(board):
        yield board
        return

    # In other case, try to guess
    # Firstly, find most problematic cell
    # i.e. cell with the most possible values
    chooseY, chooseX = 0, 0
    chooseLength, options = None, None

    for y, line in enumerate(board):
        for x, (num, pn) in enumerate(line):
            if num is None and (chooseLength is None or len(pn) > chooseLength):
                chooseY, chooseX = y, x
                options = pn
                chooseLength = len(pn)

    # Let's guess
    for guess in options:
        newBoard = copy.deepcopy(board)
        assert newBoard[chooseY][chooseX][0] is None
        newBoard[chooseY][chooseX] = (guess, None)

        logger.debug("Guess [%d][%d] => %d" % (chooseY, chooseX, guess))

        for solution in solveSudoku(newBoard):
            yield solution

if __name__ == "__main__":
    #logger.setLevel(logging.DEBUG)

    if len(sys.argv) != 2:
        print("Usage: %s <sudoku-file>" % sys.argv[0])
        sys.exit(1)

    board = readSudoku(sys.argv[1])

    foundSolution = False
    for solution in solveSudoku(board):
        foundSolution = True

        print("Solution")
        print("========")
        printBoard(solution)
        print()

    if not foundSolution:
        print("Unable to find solution :-(")

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
