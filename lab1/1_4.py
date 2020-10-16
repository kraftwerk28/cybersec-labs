#!/usr/bin/env python
import math
from pprint import pprint
import random
import re
import string
from utils import *


m = """EFFPQLEKVTVPCPYFLMVHQLUEWCNVWFYGHYTCETHQEKLPVMSAKSPVPAPVYWMVHQLUSPQLYWLASLFVWPQLMVHQLUPLRPSQLULQESPBLWPCSVRVWFLHLWFLWPUEWFYOTCMQYSLWOYWYETHQEKLPVMSAKSPVPAPVYWHEPPLUWSGYULEMQTLPPLUGUYOLWDTVSQETHQEKLPVPVSMTLEUPQEPCYAMEWWYTYWDLUULTCYWPQLSEOLSVOHTLUYAPVWLYGDALSSVWDPQLNLCKCLRQEASPVILSLEUMQBQVMQCYAHUYKEKTCASLFPYFLMVHQLUPQLHULIVYASHEUEDUEHQBVTTPQLVWFLRYGMYVWMVFLWMLSPVTTBYUNESESADDLSPVYWCYAMEWPUCPYFVIVFLPQLOLSSEDLVWHEUPSKCPQLWAOKLUYGMQEUEMPLUSVWENLCEWFEHHTCGULXALWMCEWETCSVSPYLEMQYGPQLOMEWCYAGVWFEBECPYASLQVDQLUYUFLUGULXALWMCSPEPVSPVMSBVPQPQVSPCHLYGMVHQLUPQLWLRPOEDVMETBYUFBVTTPENLPYPQLWLRPTEKLWZYCKVPTCSTESQPQULLGYAUMEHVPETFWMEHVPETBZMEHVPETB"""


class GeneticAlg:
    alphabet = list(string.ascii_uppercase)

    population_size = 100
    generation_count = 1000

    mutation_probability = 0.2

    crossover_points = 10
    crossover_k_count = 5
    crossover_probability = 0.2

    tournament_win_prob = 0.75
    tournament_size = 20

    unchanged_threshold = 20

    def __init__(self, cipher_text, train_ngrams=None,
                 train_text=None, ngram_size=3, ngram_file=None):
        self.cipher_text = cipher_text

        if train_text is not None and ngram_size is not None:
            ngrams = split_to_ngrams(train_text, ngram_size)
            self.train_ngrams = calc_freq(ngrams)
            self.ngram_size = ngram_size
        elif train_ngrams is not None:
            self.train_ngrams = train_ngrams
            first_ngram = list(train_ngrams.keys())[0]
            self.ngram_size = len(first_ngram)
        elif ngram_file is not None:
            self.train_ngrams = parse_ngrams(ngram_file)
            first_ngram = list(self.train_ngrams.keys())[0]
            self.ngram_size = len(first_ngram)
        print('N-grams generated')

        self.current_generation = 0
        self.best_ind = None
        self.generation = [random.sample(self.alphabet, len(self.alphabet))
                           for _ in range(self.population_size)]
        self.tournament_probabilities = calc_tournament_probabilities(
            self.tournament_win_prob,
            self.tournament_size)
        self.unchanged_gens = 0

    def step(self):
        self.current_generation += 1
        fitnesses = [self.fitness(fenotype) for fenotype in self.generation]
        zipped = zip(self.generation, fitnesses)
        # pprint(list(zip((''.join(k) for k in self.generation), fitnesses)))
        best_individ, best_fitness = max(zipped, key=lambda item: item[1])
        report = (f'\nGeneration #{self.current_generation}: '
                  'key = {}, fitness = {}'.format(''.join(best_individ),
                                                  best_fitness))
        if self.current_generation > 1:
            prev_ind, prev_fit = self.best_solution
            is_better = best_fitness > prev_fit
            if prev_ind == best_individ:
                report += '; unchanged'
                self.unchanged_gens += 1
                if self.unchanged_gens >= self.unchanged_threshold:
                    self.terminate()
            else:
                report += '; {}'.format('good' if is_better else 'bad')
                self.unchanged_gens = 0

        print(report)

        parents = self.selection(fitnesses)
        next_generation = []
        for p1, p2 in parents:
            c1, c2 = self.crossover(p1, p2)
            c1, c2 = self.mutate(c1, c2)
            next_generation.append(c1)
            next_generation.append(c2)

        self.best_solution = (best_individ, best_fitness)
        self.generation = next_generation

    def run(self):
        while self.current_generation < self.generation_count:
            self.step()
            best_individ, _ = self.best_solution
            print(self.decode(best_individ, self.cipher_text))

    def selection(self, fitnesses):
        sorted_fenotypes = sorted(zip(self.generation, fitnesses),
                                  key=lambda item: item[1],
                                  reverse=True)
        tournament_pool = [ft[0] for ft
                           in list(sorted_fenotypes)[:self.tournament_size]]
        return [random.choices(tournament_pool, k=2,
                               weights=self.tournament_probabilities)
                for _ in range(self.population_size // 2)]

    def terminate(self):
        self.current_generation = self.generation_count

    def mutate(self, child1, child2):
        if self.bin_rand(self.crossover_probability):
            a, b = random.sample(range(len(self.alphabet)), 2)
            child1[a], child1[b] = child1[b], child1[a]
        if self.bin_rand(self.crossover_probability):
            a, b = random.sample(range(len(self.alphabet)), 2)
            child2[a], child2[b] = child2[b], child2[a]
        return child1[:], child2[:]

    def fitness(self, individ):
        decoded = self.decode(individ, self.cipher_text)
        decoded_ngrams = split_to_ngrams(decoded, self.ngram_size)
        decoded_freq = calc_freq(decoded_ngrams)

        def F(ngram):
            ft = self.train_ngrams.get(ngram, 0)
            if ft == 0:
                return 0
            fp = decoded_freq.get(ngram, 0)
            return fp * math.log2(ft)

        return sum(map(F, decoded_freq.keys()))

    def crossover(self, parent1, parent2):
        k = random.sample(range(len(self.alphabet)), k=self.crossover_k_count)
        c1, c2 = parent1[:], parent2[:]
        if self.bin_rand(self.crossover_probability):
            c1 = self.PBX(c1, c2, k)
        if self.bin_rand(self.crossover_probability):
            c2 = self.PBX(c2, c1, k)
        return c1, c2

    @classmethod
    def decode(self, fenotype, message):
        return ''.join(self.alphabet[fenotype.index(letter)]
                       for letter in message)

    @classmethod
    def encode(self, fenotype, message):
        return ''.join(fenotype[self.alphabet.index(letter)]
                       for letter in message)

    @classmethod
    def PBX(self, parent1, parent2, k):
        rev_k = [i for i in range(len(self.alphabet)) if i not in k]
        p2_set = set(parent2)
        child = [None] * len(self.alphabet)
        for i in k:
            elem = parent1[i]
            child[i] = elem
            p2_set.remove(elem)
        p2_rem = list(p2_set)
        for index, i in enumerate(rev_k):
            child[i] = p2_rem[index]
        return child

    @staticmethod
    def bin_rand(probability):
        return random.random() < probability


freq = {
    'THE': 1.81,
    'AND': 0.73,
    'ING': 0.72,
    'ENT': 0.42,
    'ION': 0.42,
    'HER': 0.36,
    'FOR': 0.34,
    'THA': 0.33,
    'NTH': 0.33,
    'INT': 0.32,
    'ERE': 0.31,
    'TIO': 0.31,
    'TER': 0.30,
    'EST': 0.28,
    'ERS': 0.28,
    'ATI': 0.26,
    'HAT': 0.26,
    'ATE': 0.25,
    'ALL': 0.25,
    'ETH': 0.24,
    'HES': 0.24,
    'VER': 0.24,
    'HIS': 0.24,
    'OFT': 0.22,
    'ITH': 0.21,
    'FTH': 0.21,
    'STH': 0.21,
    'OTH': 0.21,
    'RES': 0.21,
    'ONT': 0.20,
}

if __name__ == '__main__':
    with open('english_trigrams.txt/english_trigrams.txt', 'r') as file:
        train_text = prepare_text(file.read())
    # pprint(calc_frequencies(split_to_ngrams(train_text, 3)))
    # print(sum(freq / 100 for freq in freq.values()))
    alg = GeneticAlg(m, ngram_file='english_trigrams.txt/english_trigrams.txt')
    alg.run()
    # key1 = EOMFLGKCVZDQTWYHXUSPANRJBI
