#!/usr/bin/env python
import os
import sys
import string

from utils import parse_ngrams, fitness


def hex2bytes(s):
    result = []
    while s:
        he = s[:2]
        result.append(int(he, 16))
        s = s[2:]
    return result


if __name__ == '__main__':
    trigrams = parse_ngrams('../lab1/ngrams/english_trigrams.txt')
    ngram_set = {3: trigrams}

    with open('input.txt') as f:
        inputs = [s.strip() for s in f.readlines()]

    inpbytes = [hex2bytes(s) for s in inputs]

    for idx, line in enumerate(inpbytes):
        output = ['_'] * len(line)
        for l in inpbytes[:idx] + inpbytes[idx+1:]:
            for charidx, (b1, b2) in enumerate(zip(line, l)):
                xored = b1 ^ b2
                next_str = output[:]
                if xored in range(65, 91):
                    next_str[charidx] = chr(xored)
                fitn1, fitn2 = (
                    fitness(output, string.ascii_uppercase, ngram_set),
                    fitness(next_str, string.ascii_uppercase, ngram_set)
                )
                if fitn2 >= fitn1:
                    output = next_str
        print(''.join(output))
