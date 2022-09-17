import sys

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
        
        # define domain and loop over it. self domain: dict: var: (SET)

        for var in self.domains:
            var_length = var.length

            # define constraint, check and update
            for word in list(self.domains[var]):
                if len(word) != var_length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        revised = False

        # check if y are neighbor of x

        overlap_position = self.crossword.overlaps[(x, y)]
        if overlap_position is None:
            return False

        # check overlapping position

        overlap_position_x = overlap_position[0]
        overlap_position_y = overlap_position[1]

        # loop to check all var in X

        for word_x in list(self.domains[x]):
            char_x = word_x[overlap_position_x]

            # loop to check all var in Y 
            check_count = 0

            for word_y in self.domains[y]:
                check_count += 1
                char_y = word_y[overlap_position_y]
                     
                # check if they are the same

                if char_x == char_y:
                    break
                
                # loop over all possible Y, not found possible Y, going to remove x and revised = true
                if check_count == len(self.domains[y]):
                    revised = True
                    self.domains[x].remove(word_x)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # all arcs in csp
        if arcs is None:
            arcs = set((dict.keys(self.crossword.overlaps)))
        
        queen = arcs

        while len(queen) != 0:
            for arc in list(queen):
                # remove 1 arc to do revise
                queen.remove(arc)
                revised = self.revise(arc[0], arc[1])
                # arc domain is changed
                if revised is True:
                    # check if there is domain left
                    if len(self.domains[arc[0]]) == 0:
                        return False
                    # find corresponding neighbor, and add back to queen
                    neighbors = self.crossword.neighbors(arc[0])
                    # remove current arc
                    neighbors.remove(arc[1])
                    # update new queen
                    for neighbor in neighbors:
                        queen.add((arc[0], neighbor))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        if len(assignment) == 0:
            return False
        for var in assignment:
            if assignment[var] is None:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        
        # check if there is conflict

        for overlap in self.crossword.overlaps:
            if self.crossword.overlaps[overlap] is None:
                continue
            variable_former = overlap[0]
            variable_latter = overlap[1]
            position_former = self.crossword.overlaps[overlap][0]
            position_latter = self.crossword.overlaps[overlap][1]
            if assignment[variable_former] is None or assignment[variable_latter] is None:
                continue
            if assignment[variable_former][position_former] != assignment[variable_latter][position_latter]:
                return False

        # check if all values are distinct

        for var1 in assignment:
            if assignment[var1] is None:
                continue # no word / assignment for that variable 
            for var2 in assignment:
                if assignment[var2] is None:
                    continue # no word / assignment for that variable 
                if var1 == var2:
                    continue
                if assignment[var1] == assignment[var2]:
                    return False # same word / assignment for different varibale

        # check if every value is the correct length, then check if there is domain left

        self.enforce_node_consistency()
        for var in assignment:
            if assignment[var] is None:
                continue
            if len(self.domains[var]) == 0:
                return False # no possible value left for the domain

        # check if there are no conflicts between neighboring variables

        arc_consistent = self.ac3()
        if arc_consistent is False:
            return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        list_domain_var = list(self.domains[var])

        def ruling_out(words):
            count_ruling_out = 0
            # check other unassigned variable's domain
            for other_var in self.crossword.neighbors(var):
                if assignment[other_var] is not None:
                    continue
                # no overlaping with neighbors
                if self.crossword.overlaps[(var, other_var)] is None:
                    continue 
                overlap_var = self.crossword.overlaps[(var, other_var)][0]
                overlap_other_var = self.crossword.overlaps[(var, other_var)][1]
                for other_var_word in self.domains[other_var]:
                    if words[overlap_var] == other_var_word[overlap_other_var]:
                        continue
                    else:
                        count_ruling_out += 1
            return count_ruling_out
        
        list_domain_var.sort(key=ruling_out)

        return list_domain_var
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # create list of unassigned
        list_unassigned = []

        for var in assignment:
            if assignment[var] is None:
                list_unassigned.append(var)
        
        def higher_degree_upfront(var):
            number_neighbor = len(self.crossword.neighbors(var))
            return - number_neighbor

        def minimum_remaining_value_upfront(var):
            number_value = len(self.domains[var])
            return number_value
            
        list_unassigned.sort(key=lambda x: (minimum_remaining_value_upfront(x), (higher_degree_upfront(x))))

        return list_unassigned[0]
        
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # set up initial dict
        if len(assignment) == 0:
            for var in self.crossword.variables:
                assignment[var] = None

        def remove_var_assignment(var):
            assignment[var] = None
            return

        # def inference(var):
        #     neighbors = self.crossword.neighbors(var)
        #     arcs = set()
        #     for neighbor in neighbors:
        #         arcs.add((var, neighbor))
        #     result = self.ac3(arcs)
        #     return result

        
        # final case / assign everything
        if self.assignment_complete(assignment) is True:
            return assignment
        
        # heuristics
        select_var = self.select_unassigned_variable(assignment)
        select_var_values = self.order_domain_values(select_var, assignment)

        for value in select_var_values:
            # set new assignment
            assignment[select_var] = value
            # check consistency
            if self.consistent(assignment) is False:
                remove_var_assignment(select_var)
                continue
            # inference
            # if inference(select_var) is False:
            #     remove_var_assignment(select_var)
            #     continue
            result = self.backtrack(assignment)
            if result is not None:
                return result
            else:
                remove_var_assignment(select_var)
                continue
        return None





        






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
