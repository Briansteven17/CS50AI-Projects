from copy import deepcopy
from curses.ascii import isalpha
import nltk
from nltk import Tree
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
S -> NP VP
NP -> N | Det N | NP PP | Det AP | NP AP | NP CP | NP AVP | NP PP
VP -> V | V NP | V PP | V AVP | V CP
PP -> P NP
AP -> Adj N | Adj AP  
CP -> Conj NP | Conj S | Conj VP
AVP -> Adv NP | Adv CP | Adv
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
    list_words = nltk.word_tokenize(sentence)
    lower_words = []
    for word in list_words:
        if not word.isalpha():
            list_words.remove(word)
            continue
        lower_words.append(word.lower())
        
    return lower_words

    #raise NotImplementedError


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_tree = []
    for node in Tree.subtrees(tree):
        if Tree.label(node) == "NP":
            np_tree.append(node)

    copy_tree = deepcopy(np_tree)
    for sub_np in copy_tree:
        np_label = 0
        for sub_tree in Tree.subtrees(sub_np):
            if Tree.label(sub_tree) == "NP":
                np_label += 1
                if np_label > 1:
                    np_tree.remove(sub_np)
                    break
    
    return np_tree

    #raise NotImplementedError


if __name__ == "__main__":
    main()
