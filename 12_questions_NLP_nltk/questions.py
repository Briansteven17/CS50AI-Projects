from copy import copy
from curses.ascii import isalpha
from multiprocessing.sharedctypes import Value
import string
import nltk
import sys
import os
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    corpus = {}
    for pages in os.listdir(directory):
        page = os.path.join(directory, pages)
        content = open(page, "r").read()
        corpus[pages] = content
    return corpus
    #raise NotImplementedError


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = []
    tokens = nltk.word_tokenize(document)
    for word in tokens:
        # Check is need to check if "isalpha or isalnum"
        if not word in string.punctuation and word not in nltk.corpus.stopwords.words("english"):
            words.append(word.lower())
    words = sorted(words)

    return words
    #raise NotImplementedError


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = {}
    word_document = {}
    for document in documents:
        fdist = nltk.FreqDist(word for word in documents[document])
        for words in fdist:
            if any(words == word for word in word_document):
                word_document[words] += 1
            else:
                word_document[words] = 1

    for words in word_document:
        idfs[words] = math.log(len(documents)/word_document[words])
    
    return idfs

    #raise NotImplementedError


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    file_values = {}
    for document in files:
        tf_idf = {}
        word_count = {}
        file_values[document] = 0
        for words in files[document]:
            if any(words == word for word in word_count):
                word_count[words] += 1
            else:
                word_count[words] = 1

        fdist = nltk.FreqDist(word for word in files[document])
        for words in fdist:
            tf_idf[words] = idfs[words] * word_count[words]

        for word in query:
            if any(word == words for words in tf_idf):
                file_values[document] += tf_idf[word]

    sort_files = [file for file, value in sorted(file_values.items(), key=lambda v:v[1], reverse=True)]

    return sort_files[:n]

    #raise NotImplementedError


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_idf = {}
    sentence_in_query = {}
    for sentence in sentences:
        sentence_in_query[sentence] = 0
        sentence_idf[sentence] = 0
        words = set ()
        for word in sentences[sentence]:
            if word in query and not word in words and not word in nltk.corpus.stopwords.words("english"):
                sentence_in_query[sentence] += 1
                sentence_idf[sentence] += idfs[word]
                words.add(word)
    
    sort_senteces = [(sentence, idf) for sentence, idf in sorted(sentence_idf.items(), key=lambda v:v[1], reverse=True)] 
    #for sentence in sort_senteces[:2]:
    #    tokens = sentences[sentence[0]]
    #    print(sentence)
    #    for token in tokens:
    #        if any(token.lower() == word for word in idfs) and token.lower() in query:
    #            print(f"word: {token.lower()}, value: {idfs[token.lower()]}")

    #sys.exit()
    top = 0
    top_tie = []
    for sentence in sort_senteces:
        if top == 0:
            top = sentence[1]
            top_tie.append(sentence)
        elif top == sentence[1]:
            top_tie.append(sentence)
        else:
             break
    
    query_density = {}
    if len(top_tie) > 1:
        for sentence in top_tie:
            query_density[sentence] = sentence_in_query[sentence[0]]/len(sentences[sentence[0]])
    
        sort_tie = [sentence for sentence, density in sorted(query_density.items(), key=lambda v:v[1], reverse=True)]
        i = 0
        for sentence in sort_tie:
            sort_senteces[i] = sentence
            i += 1

    sort_senteces = [sentence[0] for sentence in sort_senteces]
    return sort_senteces[:n]

    #raise NotImplementedError


if __name__ == "__main__":
    main()
