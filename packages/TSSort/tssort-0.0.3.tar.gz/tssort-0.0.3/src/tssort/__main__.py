import sys, os
import argparse

sys.path.append(os.path.dirname(__file__))
from pairwise_ranking import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='TSSort Algorithm Implementation', 
                                     description='This repository contains an implementation of the TSSort algorithm proposed in "TSSort – Probabilistic Noise Resistant Sorting" (Hees et al., 2011).')
    parser.add_argument('infile', nargs=2, action='store')
    parser.add_argument('-n', '--next_comparisons', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')
    args = parser.parse_args()

    comparisons, sentences = open(sys.argv[1]).readlines(), open(sys.argv[2]).readlines()
    sentences = [sentence.strip() for sentence in sentences]
    comparisons = [[int(c.split(",")[0]), int(c.split(",")[1])] for c in comparisons]
    sorted_list, m, c = mle(comparisons, sentences)
    if args.list:
        for item in sorted_list:
            print(item)
    if args.next_comparisons:
        relevance = best_rankings(m, c)
        print(relevance)


