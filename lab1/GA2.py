import string
import random
from utils import *
from typing import List, Tuple
from pprint import pprint
from GA import BaseGA
from base_GA import BaseGA


class Key:
    def __init__(self, key, alphabet=string.ascii_uppercase):
        if len(key) != len(alphabet):
            raise ValueError('Alphabet must be same length as key')
        self.key, self.alphabet = list(key), list(alphabet)

    def encode(self, text: str) -> str:
        return ''.join(self.key[self.alphabet.index(letter)]
                       for letter in text)

    def decode(self, text: str) -> str:
        return ''.join(self.alphabet[self.key.index(letter)]
                       for letter in text)

    def __repr__(self):
        return ''.join(self.key)

    def __iter__(self):
        return iter(self.key)

    def crossover_(self, other: 'Key', k_count: int) -> 'Key':
        k_points = random.sample(range(len(self.key)), k=k_count)
        rev_k = [k for k in range(len(self.alphabet)) if k not in k_points]
        remaining = other.key[:]
        child = [None] * len(self.alphabet)
        for k in k_points:
            letter = self.key[k]
            child[k] = letter
            remaining.remove(letter)
        for index, letter in zip(rev_k, remaining):
            child[index] = letter
        return Key(child)

    def crossover(self, other: 'Key', k_count: int) -> 'Key':
        keylen = len(self.key)
        perm = random.sample(range(keylen), keylen)
        child = [None] * keylen
        taken = set()
        for i in perm[:k_count]:
            letter = self.key[i]
            child[i] = letter
            taken.add(letter)
        i = 0
        for idx in perm[k_count:]:
            while other.key[i] in taken:
                i += 1
            child[idx] = other.key[i]
            i += 1
        return Key(child)

    def swap_mutate(self) -> 'Key':
        a, b = random.sample(range(len(self.alphabet)), 2)
        new_key = self.key[:]
        new_key[a], new_key[b] = new_key[b], new_key[a]
        return Key(new_key, self.alphabet)

    @staticmethod
    def random(alphabet=string.ascii_uppercase) -> 'Key':
        return Key(random.sample(alphabet, len(alphabet)), alphabet)


class Individ:
    def __init__(self, keys: List[Key]):
        self.keys = keys

    def encode(self, text: str) -> str:
        groups = group(text, len(self.keys))
        enc_groups = [key.encode(group)
                      for key, group in zip(self.keys, groups)]
        return ungroup(enc_groups)

    def decode(self, text: str) -> str:
        groups = group(text, len(self.keys))
        dec_groups = [key.decode(group)
                      for key, group in zip(self.keys, groups)]
        return ungroup(dec_groups)

    def crossover(self, other: 'Individ', k_count: List[int]) -> 'Individ':
        new_keys = [key1.crossover(key2, k_count)
                    for key1, key2 in zip(self.keys, other.keys)]
        return Individ(new_keys)

    def mutate(self) -> 'Individ':
        new_keys = [key.swap_mutate() for key in self.keys]
        return Individ(new_keys)

    def __repr__(self):
        indent = '\n' + ' ' * 5
        return '\n<ind ' + indent.join(repr(key) for key in self.keys) + '>'

    @staticmethod
    def random(key_length: int, alphabet=string.ascii_uppercase) -> 'Individ':
        return Individ([Key.random(alphabet) for _ in range(key_length)])


class PolyGA(BaseGA):
    def __init__(self, cipher_text, key_length=None,
                 train_ngrams={}, predefined_keys=None):
        self.cipher_text = cipher_text
        self.train_ngrams = train_ngrams

        self.current_generation = 0
        self.best_solution: Tuple[Individ, float] = None
        self.generation = [Key.random]

        if predefined_keys is None:
            self.generation = [Individ.random(key_length,
                                              string.ascii_uppercase)
                               for _ in range(self.population_size)]
            self.key_length = key_length
        else:
            self.generation = [Individ(predefined_keys)
                               for _ in range(self.population_size)]
            self.key_length = len(predefined_keys)

        self.tournament_probabilities = calc_tournament_probabilities(
            self.tournament_win_prob,
            self.tournament_size)

        self.unchanged_gens = 0

    def step(self):
        self.current_generation += 1
        fitnesses = [self.fitness(ind) for ind in self.generation]
        zipped = zip(self.generation, fitnesses)
        best_individ, best_fitness = max(zipped, key=lambda item: item[1])

        report = (f'\nGeneration #{self.current_generation}: '
                  'key = {}, fitness = {}'.format(best_individ, best_fitness))

        if self.current_generation > 1:
            prev_ind, prev_fit = self.best_solution
            is_better = best_fitness > prev_fit
            if prev_fit == best_fitness:
                report += '; same'
                self.unchanged_gens += 1
                if self.unchanged_gens >= self.unchanged_threshold:
                    self.terminate()
            else:
                report += '; {}'.format('better' if is_better else 'worse')
                self.unchanged_gens = 0

        print(report)

        self.best_solution = (best_individ, best_fitness)
        parents = self.selection(fitnesses)
        next_generation = []
        for p1, p2 in parents:
            c1, c2 = p1, p2
            if prob(self.crossover_probability):
                c1, c2 = (c1.crossover(c2, self.crossover_k_count),
                          c2.crossover(c1, self.crossover_k_count))
            if prob(self.mutation_probability):
                c1, c2 = c1.mutate(), c2.mutate()
            next_generation.append(c1)
            next_generation.append(c2)

        self.generation = next_generation

    def run(self):
        while self.current_generation < self.generation_count:
            self.step()
            best_individ, _ = self.best_solution
            dec = best_individ.decode(self.cipher_text)
            print(dec)
            # if all(word in dec for word in ['THE', 'AND']):
            #     print(best_individ)
            #     print(dec)

    def fitness(self, individ: Individ):
        result = 0
        for ngram_size, train_ngrams in self.train_ngrams.items():
            decoded = individ.decode(self.cipher_text)
            dec_ngrams = split_to_ngrams(decoded, ngram_size)
            dec_freq = calc_freq(dec_ngrams)

            def F(ngram):
                ft = train_ngrams.get(ngram, 0)
                if ft == 0:
                    return 0
                fp = dec_freq.get(ngram, 0)
                return fp * math.log2(ft)

            fitness = sum(map(F, dec_freq.keys()))
            result += fitness
        return result
        # decoded = individ.decode(self.cipher_text)
        # decoded_ngrams = split_to_ngrams(decoded, self.ngram_size)
        # decoded_freq = calc_freq(decoded_ngrams)

        # def F(ngram):
        #     ft = self.train_ngrams.get(ngram, 0)
        #     if ft == 0:
        #         return 0
        #     fp = decoded_freq.get(ngram, 0)
        #     return fp * math.log2(ft)

        # return sum(map(F, decoded_freq.keys()))

    def selection(self, fitnesses):
        sorted_fenotypes = sorted(zip(self.generation, fitnesses),
                                  key=lambda item: item[1],
                                  reverse=True)
        for sf in sorted_fenotypes:
            print(sf[1])
        tournament_pool = [ft[0] for ft
                           in list(sorted_fenotypes)[:self.tournament_size]]
        # return [random.choices(tournament_pool, k=2,
        #                        weights=self.tournament_probabilities)
        #         for _ in range(self.population_size // 2)]
        result = []
        i = 0
        for _ in range(self.population_size // 2):
            c1 = tournament_pool[i]
            c2 = tournament_pool[(i + 1) % self.tournament_size]
            i = (i + 1) % self.tournament_size
            result.append([c1, c2])
        return result

    def terminate(self):
        self.current_generation = self.generation_count
