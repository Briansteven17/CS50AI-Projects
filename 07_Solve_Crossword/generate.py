from copy import deepcopy
import random
from sre_constants import FAILURE
import sys
from typing import overload
from xml import dom

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains = deepcopy(self.domains)
        
        for domain in domains:
            for number in domains[domain]:
                if domain.length != len(number):
                    self.domains[domain].remove(number)
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        domains = deepcopy(self.domains)
        
        count = 0        
        overlap_xy = self.crossword.overlaps[x, y]
        if overlap_xy != None:
            for domain_x in domains[x]:
                match = 0
                for domain_y in self.domains[y]:
                    if domain_x[overlap_xy[0]] == domain_y[overlap_xy[1]]:
                        match += 1
                if match == 0:
                    self.domains[x].remove(domain_x)
                    count += 1     
        if count > 0:
            return True
        else:
            return False

        #raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            for overlap in self.crossword.overlaps:
                check = self.revise(overlap[0], overlap[1])
                if check == True:
                    check_overlaps = []
                    for check_domain in self.crossword.overlaps:
                        if overlap[0] in check_domain:
                            check_overlaps.append(check_domain)
                    check_queue = self.ac3(check_overlaps)
                    if check_queue == False:
                        return False
            for domain in self.domains:
                if len(self.domains[domain]) == 0:
                    return False
            return True
        else:
            for overlap in arcs:
                check = self.revise(overlap[0], overlap[1])
                if check == True:
                    if len(self.domains[overlap[0]]) == 0:
                        return False
                    check_overlaps = []
                    for check_domain in self.crossword.overlaps:
                        if overlap[0] in check_domain:
                            check_overlaps.append(check_domain)
                    self.ac3(check_overlaps)
            
        #raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.domains):
            for variable in self.domains:
                if isinstance(assignment[variable], str):
                    continue
                else:
                    return False
            return True
        else:
            return False
        #raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if words in domain suit the length required and not repeat values
        words = set()
        for domain in assignment:
            if isinstance(assignment[domain], str):
                if domain.length != len(assignment[domain]):
                    #print("length problem")
                    return False
                elif assignment[domain] in words:
                    #print("distinct problem")
                    return False
                words.add(assignment[domain])
        
        
        # Check if there is any conflict between neighboring variables
        overlaps = self.crossword.overlaps
        for overlap in overlaps:
            if overlaps[overlap] != None and isinstance(assignment[overlap[0]], str) and isinstance(assignment[overlap[1]], str):
                domain_x = assignment[overlap[0]]
                domain_y = assignment[overlap[1]]
                if domain_x[overlaps[overlap][0]] != domain_y[overlaps[overlap][1]]:
                    #print("neighboring problem")
                    return False
        #print("Good")
        return True


                

        #raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        if isinstance(assignment[var], str):
            unique_value = [assignment[var]]
            return unique_value
        else:
            rule_out = dict()
            values_order = []
            for value in assignment[var]:
                rule_out[value] = 0
                for variable in assignment:
                    if value in assignment[variable] and variable != var:
                        rule_out[value] += 1
            
            sorted_values = {k: v for k, v in sorted(rule_out.items(), key=lambda variable: variable[1])}
            
            for variable in sorted_values:
                values_order.append(variable)
            return values_order

            

        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        remaining_values = dict()
        for variable in assignment:
            if isinstance(assignment[variable], str) == False:
                remaining_values[variable] = len(self.domains[variable])
        sorted_list =  {k: v for k, v in sorted(remaining_values.items(), key=lambda variable: variable[1])}
        count = 0
        neighbors = dict()
        for variable in sorted_list:
            if count == 0:
                first_value = sorted_list[variable]
                first_variable = variable
            if first_value == sorted_list[variable]:
                count += 1
            neighbors[variable] = len(self.crossword.neighbors(variable))
        if count <= 1:
            return first_variable
        else:
            sorted_neighbors = {k: v for k, v in sorted(neighbors.items(), key=lambda variable: variable[1], reverse=True)}
            random_variable = []
            number_neigbors = []
            for neighbor in sorted_neighbors:
                if len(number_neigbors) == 0:
                    number_neigbors.append(sorted_neighbors[neighbor])
                    random_variable.append(neighbor)
                elif number_neigbors[0] == sorted_neighbors[neighbor]:
                    random_variable.append(neighbor)
            return random.choice(random_variable)
            
        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        #print(assignment)
        if len(assignment) == 0:
            assignment = deepcopy(self.domains)

        if self.assignment_complete(assignment):
            print(assignment)
            return assignment
        
        # try a new variable
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assigment = assignment.copy()
            new_assigment[var] = value
            if self.consistent(new_assigment):
                result = self.backtrack(new_assigment)
                if result is not None:
                    return result
        return None
        
        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
