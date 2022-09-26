import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    list_all_pages = list(dict.keys(corpus))
    count_all_pages = len(list_all_pages)
    next_probability = {}
    

    # check if page has no outgoing links. if so return all page evenly

    if len(corpus[page]) == 0:
        even_probability = 1 / count_all_pages
        for item in list_all_pages:
            next_probability[item] = even_probability
        return next_probability
        
    # if not, calculate probabilty. check if certain page in the next page, then move on

    else:
        total_proba = 0
        for item in list_all_pages:
                if not item in corpus[page]: # corpus[page] is set of the next pages, given page
                    next_probability[item] = (1 - damping_factor) / count_all_pages
                    total_proba += next_probability[item]
                else:
                    next_probability[item] = (1 - damping_factor) / count_all_pages + damping_factor / len(corpus[page])
                    total_proba += next_probability[item]
        
        # check total proba
        if round(total_proba, 5) != 1:
            print(total_proba)
            raise Exception("transition_probaility_error")
        
        return next_probability

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    count_of_steps = 0
    count_of_sample_pages = {}
    proportion_of_pages = {} # similar to proba

    list_all_pages = list(dict.keys(corpus))
    count_all_pages = len(list_all_pages)

    # choose 1st page to start

    even_proba_list = []
    for i in range(count_all_pages):
        even_proba_list.append(1 / count_all_pages)
    page_now = random.choices(population=list_all_pages, weights=even_proba_list)[0]

    # go from 1st page to next 10000 steps

    while count_of_steps < n:

        # check if dict continue current page
        if not page_now in dict.keys(count_of_sample_pages):
            count_of_sample_pages[page_now] = 1
        # add count if exist
        else:
            count_of_sample_pages[page_now] += 1
        
        # move to next page
        next_page_with_proba = transition_model(corpus, page_now, damping_factor)
        page_now = random.choices(population=list(dict.keys(next_page_with_proba)), weights=list(dict.values(next_page_with_proba)))[0]

        count_of_steps += 1
    
    # check if run N times
    if sum(list(dict.values(count_of_sample_pages))) != n:
        print(list(dict.values(count_of_sample_pages)))
        raise Exception("sample_pagerank_count_fail")

    # convert count to proportion
    for item in count_of_sample_pages:
        proportion_of_pages[item] = count_of_sample_pages[item] / n
    
    return proportion_of_pages



def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    list_all_pages = list(dict.keys(corpus))
    old_proba_pages = {}
    new_proba_pages = {}

    # assign initial proba

    for page in list_all_pages:
        old_proba_pages[page] = 1 / len(list_all_pages)

    # loop till no value changes by more than 0.001

    def converged_old_new(old_proba_pages, new_proba_pages):
        # initial condition
        if len(new_proba_pages) == 0:
            return False
        for old_pages in old_proba_pages:
            if abs(old_proba_pages[old_pages] -  new_proba_pages[old_pages]) > 0.001:
                return False
        return True

    # see if sum of proba = 1

    def sum_to_one(new_proba_pages):
        if abs(sum(list(dict.values(new_proba_pages))) - 1) < 0.001:
            return True
        return False


    # while converged_old_new(old_proba_pages, new_proba_pages) is False:
    while converged_old_new(old_proba_pages, new_proba_pages) is False or sum_to_one(new_proba_pages) is False:
        # update new_proba_pages to old_proba
        if len(new_proba_pages) != 0:
            for page in old_proba_pages:
                old_proba_pages[page] = new_proba_pages[page]

        # if A page that has no links at all should be interpreted as 
        # having one link for every page in the corpus (including itself)
        for old_proba_page in old_proba_pages:
            # formula
            formula_former = (1 - damping_factor) / len(list_all_pages)
            formula_latter = 0

            # check what page link to old_proba_page
            for link_page in old_proba_pages:
                minus_self_link = corpus[link_page]
                # remove page to itself
                try:
                    minus_self_link.remove(link_page)
                except:
                    pass
                if link_page == old_proba_page:
                    # if self page has no other link
                    if len(minus_self_link) == 0:
                        formula_latter += damping_factor * old_proba_pages[link_page] / len(old_proba_pages)
                    else:
                        continue
                #  other page has no link
                elif len(minus_self_link) == 0:
                    formula_latter += damping_factor * old_proba_pages[link_page] / len(old_proba_pages)
                # page has link
                else:
                    if not old_proba_page in minus_self_link:
                        continue
                    else:
                        formula_latter += damping_factor * old_proba_pages[link_page] / len(minus_self_link)
            
            new_proba_pages[old_proba_page] = formula_former + formula_latter
    
    return new_proba_pages


if __name__ == "__main__":
    main()
