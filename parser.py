import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP Conj S | NP VP Conj VP
NP -> N | Det N | NP P NP | Det Adj N | Det Adj Adj N | Det Adj Adj Adj N
VP -> V | V NP | Adv VP | VP Adv | V P | V P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    rough_word_list = []
    filtered_word_list = []

    # e.g. "28", "word", "." 
    rough_word_list = nltk.word_tokenize(sentence)

    # loop rough list

    for word in rough_word_list:
        count_alphe_check = 0

        # check if it contain at least 1 alphbet
        for char in word:
            if char.isalpha() is True:
                # lower case for the list
                lower_word = word.lower()
                # add to new list
                filtered_word_list.append(lower_word)
                break

    return filtered_word_list
    

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_chunk_list = []
    
    # loop over all subtrees with label NP
    for np_tree in tree.subtrees(lambda t: t.label() == "NP"):
        # loop over all subtree and see if there is NP under it
        no_np_in_subtree = True
        for subtree in np_tree:
            if subtree.label() == "NP":
                no_np_in_subtree = False
                break
        # if no NP under, add to list
        if no_np_in_subtree is True:
            np_chunk_list.append(np_tree)

    return np_chunk_list


if __name__ == "__main__":
    main()
