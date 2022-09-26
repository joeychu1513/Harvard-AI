import nltk
import sys
import os
import string
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
    
    txt_dict = {}
    
    # loop over all file in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            separator = os.sep
            file_name = file_path.split(separator)[1]
            file_type = file_name.split(".")[1]
            # check if it is .txt file
            if file_type == "txt":
                # add content into dict
                with open(file_path, encoding='cp437') as f:
                    file_content = f.read()
                    txt_dict[file_name] = file_content
    
    return txt_dict

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    filtered_list = []
    tokens = nltk.word_tokenize(document)
    
    # loop over
    for token in tokens:
        # ignore punctuation
        if token in string.punctuation \
                    or token == '``' \
                    or token == '"' \
                    or token == "''" \
                    or token == "==" \
                    or token == "===":
            continue
        # ignore stopwords
        token_lower = token.lower()
        if token_lower in nltk.corpus.stopwords.words("english"):
            continue
        # convert to lowercase and add to list
        filtered_list.append(token_lower)
    
    return filtered_list
    

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    num_of_documents = len(documents)
    idf_dict = {}

    # loop over each documents
    for document in documents:
        #loop over each word in the document
        for word in documents[document]:
            if word in idf_dict: # already calculate the idf
                continue
            num_doc_containing = 1
            # loop over OTHER document to check:
            for other_document in documents:
                if document == other_document:
                    continue # same document
                # loop over each word on OTHER document to check
                for word_other_doc in documents[other_document]:
                    if word == word_other_doc: # found the same word in OTHER doc
                        num_doc_containing += 1
                        break
            # calculate idf for the word and app to dict
            idf_word = math.log(num_of_documents/num_doc_containing)
            idf_dict[word] = idf_word

    return idf_dict
    
    
def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    
    query_list = list(query)

    sum_tf_idf = {} # file : sum of tf_idf for each word in the query

    all_word_file_list = list(dict.keys(idfs))

    for word_query in query_list:
        # check if it is in the file word
        if word_query not in all_word_file_list:
            continue # check for next word in the query
        # loop over each doc to calculte the tf idf
        for document in files:
            tf_word_query = files[document].count(word_query)
            idf_word_query = idfs[word_query]
            tf_idf_word_query = tf_word_query * idf_word_query
            # if the dict[doc] not exist yet
            if document not in sum_tf_idf:
                sum_tf_idf[document] = tf_idf_word_query
            else:
                sum_tf_idf[document] += tf_idf_word_query

    # unsorted list of file name
    unranked_files_list = list(dict.keys(files))
    # sort by tf-idf
    ranked_files_list = sorted(unranked_files_list, key=lambda x : - sum_tf_idf[x])
    # chop by N
    chopped_list = ranked_files_list[:n]

    return chopped_list
    

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    query_list = list(query)

    sum_idf = {} # file : sum of tf_idf for each word in the query
    query_density ={}
    
    all_word_file_list = list(dict.keys(idfs))

    for word_query in query_list:
        # loop over each doc to calculte the idf
        for sentence in sentences:
            # check if it is in the sentense, and add to sum_idf
            if word_query in sentences[sentence]:
                idf = idfs[word_query]
                if sentence not in sum_idf:
                    sum_idf[sentence] = idf
                else:
                    sum_idf[sentence] += idf

    # calculate density
    for sentence in sum_idf:
        count_word_in_query = 0
        length_sentence = len(sentences[sentence])
        for word in sentences[sentence]:
            if word in query_list:
                count_word_in_query += 1
        query_density[sentence] = count_word_in_query / length_sentence

    # unsorted list of sentences
    unranked_sentences_list = list(dict.keys(sum_idf))
    # sort by idf, then density
    ranked_sentences_list = sorted(unranked_sentences_list, key=lambda x : (- sum_idf[x], - query_density[x]))
    # chop by N
    chopped_list = ranked_sentences_list[:n]

    return chopped_list

if __name__ == "__main__":
    main()
