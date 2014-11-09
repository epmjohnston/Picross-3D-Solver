"""
Picross 3D solver by Emily Johnston
with some help from David Johnston and Charlotte Foran
for Andy Exley's Artificial Intelligence class, Carleton College, Spring 2014

Utilizes SATSolver.py and zChaff to solve Picross 3D puzzles using propositional logic.
Displays 3D solution using VPython.

Does not support puzzles with multiple grouping (circle or square numbers) (yet).
"""

import sys
from copy import deepcopy
import itertools as it
import visual as v
import SATSolver as SAT

class PicrossPuzzle:
    def __init__(self, infile):

        # Initialize size of puzzle and constraints (sides of starting blocks)
        self.width, self.height, self.depth = 0,0,0
        self.sides = self.constructPuzzleFromFile(infile)

        # The presence of each block in the solution is one literal.
        # An int is assigned to each block in initIndices, and stored in self.indices.
        # The 3D index in indices corresponds to the 3D coordinate in the puzzle of that block.
        self.numLiterals = 1
        self.indices = self.initIndices()

        # Holds descriptions of constraints in propositional logic (PL)
        # in Conjunctive Normal Form (CNF) for SATSolver
        self.clauses = []

        # Holds solution of puzzle, as 3D list of ints where:
        # 0 = block not present in solution
        # 1 = block present in solution
        # -1 = SATSolver could not determine whether block should be in solution
        self.solution = []

    def constructPuzzleFromFile(self, f):
        """
        Takes a file in the format described in README.
        Sets instance height, width, and depth.
        Returns constraints of the puzzle (sides) in list format.
        """

        def getLineAsList():
            """ Local function to format input from file """
            return f.readline().strip('\n').split(' ')

        sides = []

        # First line is the bounds of the puzzle: width, height, depth.
        bounds = getLineAsList()
        self.width = int(bounds[0])
        self.height = int(bounds[1])
        self.depth = int(bounds[2])

        # discard line of whitespace
        f.readline()

        # Construct sides in order
        # (0: first in file, on right side of puzzle, lines input going vertically down;
        #  1: next in file, on top of puzzle, lines input going horizontally right;
        #  2: last in file, on left of puzzle, lines input going vertically down)
        for bound in [self.height, self.width, self.height]:
            # construct each side line by line, then add to self.sides.
            thisSide = []
            for i in range(bound):
                thisLine = getLineAsList()
                thisSide.append(thisLine)
            sides.append(thisSide)
            # discard line of whitespace
            f.readline()

        return sides

    def initIndices(self):
        """
        Creates indices list that stores unique integer id's of literals,
        each literal representing the presence of the block at the corresponding
        3D index in the solution.
        """
        # for each block in the 3D puzzle, assign it a unique integer id,
        # and increment the puzzle's total number of literals.
        indices = range(self.width)
        for x in indices:
            indices[x] = range(self.height)
            for y in indices[x]:
                indices[x][y] = range(self.depth)
                for z in indices[x][y]:
                    indices[x][y][z] = self.numLiterals
                    self.numLiterals += 1
        return indices

    def solve(self):
        self.clauses = self.makePLSentences()
        self.solution = self.constructSolution()

    def makePLSentences(self):
        """
        Constructs clauses in KB (self.clauses).
        Does not yet handle circles or squares.
        """
        KB = []
        # look at each side of the input puzzle
        for sideIndex in range(len(self.sides)):
            side = self.sides[sideIndex]
            # look at each x,y coordinate on that side
            for rowIndex in range(len(side)):
                row = side[rowIndex]
                for colIndex in range(len(row)):
                    col = row[colIndex]
                    # if there is a number in that square, construct a sentence and add it to KB,
                    # else (if there is no information available), do nothing.
                    if col != '-':
                        stack = self.getStackOfBlocks(sideIndex, rowIndex, colIndex)
                        if col[0] == '(':
                            sideNum = int(col[1])
                            KB += self.PLSentencesCircleStack(stack, sideNum)
                        elif col[0] == '[':
                            sideNum = int(col[1])
                            KB += self.PLSentencesSquareStack(stack, sideNum)
                        else:
                            sideNum = int(col)
                            KB += self.PLSentencesPlainStack(stack, sideNum)
        return KB

    def PLSentencesPlainStack(self, stack, sideNum):
        """
        Constructs a CNF clause for one stack of blocks and appends them to KB.
        """
        sentences = []
        # If none of the blocks in this stack must be in soln,
        # add not of all literals in stack to KB.
        if sideNum == 0:
            for block in stack:
                sentences.append([block*-1])

        # If all blocks in this stack must be in soln,
        # add all literals in stack to KB.
        elif sideNum == len(stack):
            for block in stack:
                sentences.append([block])

        # If neither trivial case applies, construct sentences such that
        # there must be exactly sideNum blocks in stack all in a row in solution.
        else:
            # at least sideNum blocks per stack
            combos = list(it.combinations(stack, len(stack) - sideNum + 1))
            for combo in combos:
                sentences.append(list(combo))

            # no more than sideNum blocks per stack
            combos = list(it.combinations(stack, sideNum + 1))
            for c in range(len(combos)):
                combo = list(combos[c])
                for i in range(len(combo)):
                    combo[i] *= -1
                sentences.append(combo)

            # blocks must appear in a row
            for start in range(len(stack)):
                for nextBlock in range(start+sideNum, len(stack)):
                    sentences.append([stack[start]*-1, stack[nextBlock]*-1])

        return sentences

    def PLSentencesCircleStack(self, stack, sideNum):
        sys.exit("Error: Circles have not yet been implemented.")

    def PLSentencesSquareStack(self, stack, sideNum):
        sys.exit("Error: Squares have not yet been implemented.")

    def constructSolution(self):
        """
        Test the KB (self.clauses) using SATSolver.py testLiteral function.
        Returns a solved puzzle in the form of a 3D list.
        Each block is 1 if block is in solved puzzle, 0 if not, -1 if unknown.
        """
        solved = deepcopy(self.indices)
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    curLiteral = self.indices[x][y][z]
                    truthVal = SAT.testLiteral(curLiteral, self.clauses)
                    if truthVal == True:
                        solved[x][y][z] = 1
                    elif truthVal == False:
                        solved[x][y][z] = 0
                    else:
                        solved[x][y][z] = -1
        return solved

    def getStackOfBlocks(self, sideIndex, rowIndex, colIndex):
        """
        Given the indices in the puzzle constraints
        of a number on the side of the unsolved puzzle,
        returns the list of blocks in the associated stack.
        """
        stack = []
        if sideIndex == 0:
            y = rowIndex
            z = colIndex
            for x in range(self.width):
                stack.append(self.indices[x][y][z])
        elif sideIndex == 1:
            x = self.width - rowIndex - 1
            z = colIndex
            for y in range(self.height):
                stack.append(self.indices[x][y][z])
        elif sideIndex == 2:
            x = self.width - colIndex - 1
            y = rowIndex
            for z in range(self.depth):
                stack.append(self.indices[x][y][z])
        return stack

    def printSolution(self):
        """
        Prettily prints the solution for this puzzle to the terminal in slices.
        """
        # If the solution has not already been constructed, construct it.
        if not self.solution:
            self.solve()
        print "\nSolution:"
        for x in self.solution:
            for y in x:
                for z in y:
                    print z,
                print
            print

    def displaySolution3D(self, scale):
        """
        Display a 3D representation of this solution using VPython.
        """
        # If the solution has not already been constructed, construct it.
        if not self.solution:
            self.solve()
        for x in range(len(self.solution)):
            for y in range(len(self.solution[x])):
                for z in range(len(self.solution[x][y])):
                    if self.solution[x][y][z]:
                        block = v.box(pos=(x*scale, y*scale, z*scale),
                                   length = scale,
                                   height = scale,
                                   width = scale,
                                   color = v.color.blue)

                        # display undefined blocks in red
                        if self.solution[x][y][z] == -1:
                            block.color = v.color.red

def main():
    usageStr = """
USAGE: Picross3D.py <filename>
    filename: name of a file that contains an unsolved puzzle.
See included README files for more information on the rules of Picross 3D,
how to input a puzzle, and the implementation of this solver.
    """

    # get filename of puzzle to solve from command line arguments.
    if len(sys.argv) != 2:
        sys.exit(usageStr)
    filename = sys.argv[1]

    # open unsolved puzzle file, construct puzzle, close file.
    try:
        infile = open(filename)
    except IOError:
        errorStr = "Error: " + filename + " is not a valid filename."
        sys.exit(errorStr)
    puzz = PicrossPuzzle(infile)
    infile.close()

    puzz.solve()
#    puzz.printSolution()
    puzz.displaySolution3D(3)

if __name__ == "__main__":
    main()
