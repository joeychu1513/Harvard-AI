import itertools
import random
import copy



class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # raise NotImplementedError

        # if length of cells == count, all are mines
        if len(self.cells) == self.count:
            return self.cells
        
    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # raise NotImplementedError

        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # raise NotImplementedError
        
        # if cell in sentence, remove from cells, count -=1 from sentense
        
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # raise NotImplementedError

        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # raise NotImplementedError

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.safes.add(cell)

        # 3) add a new sentence to the AI's knowledge base, based on the value of `cell` and `count`
        cell_row = cell[0]
        cell_column = cell[1]

        new_sentense_set = set()
        new_sentense_count = count

        for i in range(cell_row - 1, cell_row + 2):
            for j in range(cell_column - 1, cell_column + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # bypass corner and edge case
                elif  0 <= i < self.height and 0 <= j < self.width:
                    # Be sure to only include cells whose state is still undetermined in the sentence.
                    if (i, j) in self.mines:
                        new_sentense_count -= 1
                        continue
                    elif (i, j) in self.safes:
                        continue
                    new_sentense_set.add((i, j))
                    
        # create new sentence
        new_sentence = Sentence(new_sentense_set, new_sentense_count)

        # add to knowledge list
        self.knowledge.append(new_sentence)

        # 4) mark any additional cells as safe or as mines, if it can be concluded based on the AI's knowledge base
        for sentense in self.knowledge:
            # if cell in sentense.cells:
            self.mark_safe(cell)
            while True:
                # check if other known mines / safe
                known_mines = sentense.known_mines()
                if known_mines is not None and len(known_mines) != 0:
                    self.mines = self.mines.union(known_mines)
                    for mine in copy.copy(known_mines):
                        self.mark_mine(mine)
                    continue
                known_safes = sentense.known_safes()
                if known_safes is not None and len(known_safes) != 0:
                    self.safes = self.safes.union(known_safes)
                    for safe in copy.copy(known_safes):
                        self.mark_safe(safe)
                    continue
                break
        
        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge

        while True:
            count_new_sentense = 0
            for sentense1 in self.knowledge:
                for sentense2 in self.knowledge:
                    if sentense1.cells < sentense2.cells:
                        new_subset = sentense1.cells.intersection(sentense2.cells)
                        if new_subset == sentense1.cells:
                            break
                        new_count = sentense2.count - sentense1.count
                        new_sentense_by_inference = Sentence(new_subset, new_count)
                        count_new_sentense += 1
                        self.knowledge.append(new_sentense_by_inference)
                    elif sentense2.cells < sentense1.cells:
                        new_subset = sentense2.cells.intersection(sentense1.cells)
                        if new_subset == sentense2.cells:
                            break
                        new_count = sentense1.count - sentense2.count
                        new_sentense_by_inference = Sentence(new_subset, new_count)
                        count_new_sentense += 1
                        self.knowledge.append(new_sentense_by_inference)
            if count_new_sentense == 0:
                break


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # raise NotImplementedError

        safe_move_set = self.safes - self.moves_made
        if len(safe_move_set) > 0:
            return list(safe_move_set)[random.randrange(len(safe_move_set))]
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # raise NotImplementedError

        # set of all possible move
        all_move = set()
        for i in range(self.height):
            for j in range(self.width):
                all_move.add((i, j))
        random_move = all_move - self.moves_made - self.mines
        if len(random_move) == 0:
            return None
        return list(random_move)[random.randrange(len(random_move))]
