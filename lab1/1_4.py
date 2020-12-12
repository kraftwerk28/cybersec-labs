#!/usr/bin/env python
import math
from pprint import pprint
import re
from utils import *
from os import path
from GA import MonoGA
from GA2 import PolyGA


m = """EFFPQLEKVTVPCPYFLMVHQLUEWCNVWFYGHYTCETHQEKLPVMSAKSPVPAPVYWMVHQLUSPQLYWLASLFVWPQLMVHQLUPLRPSQLULQESPBLWPCSVRVWFLHLWFLWPUEWFYOTCMQYSLWOYWYETHQEKLPVMSAKSPVPAPVYWHEPPLUWSGYULEMQTLPPLUGUYOLWDTVSQETHQEKLPVPVSMTLEUPQEPCYAMEWWYTYWDLUULTCYWPQLSEOLSVOHTLUYAPVWLYGDALSSVWDPQLNLCKCLRQEASPVILSLEUMQBQVMQCYAHUYKEKTCASLFPYFLMVHQLUPQLHULIVYASHEUEDUEHQBVTTPQLVWFLRYGMYVWMVFLWMLSPVTTBYUNESESADDLSPVYWCYAMEWPUCPYFVIVFLPQLOLSSEDLVWHEUPSKCPQLWAOKLUYGMQEUEMPLUSVWENLCEWFEHHTCGULXALWMCEWETCSVSPYLEMQYGPQLOMEWCYAGVWFEBECPYASLQVDQLUYUFLUGULXALWMCSPEPVSPVMSBVPQPQVSPCHLYGMVHQLUPQLWLRPOEDVMETBYUFBVTTPENLPYPQLWLRPTEKLWZYCKVPTCSTESQPQULLGYAUMEHVPETFWMEHVPETBZMEHVPETB"""


if __name__ == '__main__':
    ngrams = {3: 'ngrams/english_trigrams.txt'}
    # ngrams = {3: 'english_trigrams.txt/english_trigrams.txt',
    #           4: 'english_quadgrams.txt/english_quadgrams.txt',
    #           5: 'english_quintgrams.txt/english_quintgrams.txt'}

    ngrams = {freq: parse_ngrams(fname) for freq, fname in ngrams.items()}
    # ga = MonoGA(m, ngram_file=ngram_file)
    ga = PolyGA(m, key_length=1, train_ngrams=ngrams)
    try:
        ga.run()
    except KeyboardInterrupt:
        print('\nAborting')
    # key1 (not valid) = EOMFLGKCVZDQTWYHXUSPANRJBI
