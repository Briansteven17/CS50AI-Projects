from copy import deepcopy
from logging import raiseExceptions
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
    distribution = dict()


    if len(corpus[page]) > 0: # if there are link pages to this current page
        link_value = damping_factor/len(corpus[page])
        page_value = link_value + (1 - damping_factor)/len(corpus)
        for link_page in corpus[page]: # all link pages to the current key (page)
                distribution[link_page] = page_value # start to add
                
        if len(distribution) != len(corpus):
            for left_page in corpus:
                if any(left_page in link_pages for link_pages in distribution) == False:
                    distribution[left_page] = (1 - damping_factor)/len(corpus)

    else:
        page_value = 1/len(corpus)
        for unlink_page in corpus:
            distribution[unlink_page] = page_value
    # check if probability SUM UP 1
    #probability = 0
    #for pages in distribution:
    #    probability += distribution[pages]
    #if probability != 1:
    #    print(probability)
    #    print(page)
    #    raise NameError("Probability transictions model not SUM UP 1")
    return distribution   


    raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = dict()
    
    pagerank_numbers = dict()
    for page in corpus:
        pagerank_numbers[page] = 0

    pages = []
    for page in corpus:
        pages.append(page)
    first_page = random.choice(pages)
    current_transiction = transition_model(corpus, first_page, damping_factor)
    for i in range(n):
        
        pages = []
        values = []

        for page in current_transiction:
            pages.append(page)
            values.append(current_transiction[page])

        page_chosen = random.choices(pages, weights=values, k=1)
        pagerank_numbers[page_chosen[0]] += 1
        
        current_transiction = transition_model(corpus, page_chosen[0], damping_factor)

    for page in pagerank_numbers:
        pagerank[page] = pagerank_numbers[page]/n

    # Check if pagerank SUM UP 1
    #probability = 0
    #for pages in pagerank:
    #    probability += pagerank[pages]
    #if probability != 1:
    #    print(pagerank)
    #    print("Pagerank sample is not 1")
    #    raise NameError("Probability pagerank not SUM 1")
    return  pagerank

    raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    first_pagerank = dict()
    equal_rank = 1/len(corpus)
    current_links = []
    
    for page in corpus:
        first_pagerank[page] = equal_rank
        current_links.append(page)

    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = current_links   
    
    link_pages = dict()

    for pagerank_p in first_pagerank:
        current_links = []
        for link_page in corpus:
            if pagerank_p in corpus[link_page]:
                current_links.append(link_page)
        link_pages[pagerank_p] = current_links

    new_pagerank = first_pagerank
    while True:    

        pagerank = deepcopy(new_pagerank)
        new_pagerank = i_pagerank(corpus, damping_factor, pagerank, link_pages)
  
        count = 0
        for page in pagerank:
            if abs(pagerank[page] - new_pagerank[page]) <= 0.001:
                count += 1
        if count == len(pagerank):
            break

    # Check if pagerank SUM UP 1
    #probability = 0
    #for pages in new_pagerank:
    #    probability += new_pagerank[pages]
    #if probability != 1:
    #    print(probability)
    #    raise NameError("Probability pagerank not SUM 1")
    return new_pagerank
    

    raise NotImplementedError

def i_pagerank(corpus, damping_factor, pagerank, link_pages):
    """
    This function have to represent the recursive PR(i) "This function was implemented by me"
    so, it is optional to complete the whole aplication.
    """
    
    all_random = (1 - damping_factor)/len(corpus)
    new_pagerank = dict()

    for page in corpus:
        total_sum = 0
        for link_page in link_pages[page]:
            sum_pr = pagerank[link_page]/len(corpus[link_page])
            total_sum += sum_pr
        new_pagerank[page] = all_random + (damping_factor * total_sum)

    return new_pagerank

    raise NotImplementedError

if __name__ == "__main__":
    main()
