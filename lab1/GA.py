import string
import random
from utils import *
from base_GA import BaseGA


class MonoGA(BaseGA):
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
        self.best_solution = None
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
        best_individ, best_fitness = max(zipped, key=lambda item: item[1])
        report = (f'Generation #{self.current_generation}: '
                  'key = {}, fitness = {}'.format(''.join(best_individ),
                                                  best_fitness))
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

        self.best_solution = (best_individ[:], best_fitness)
        print(report)

        parents = self.selection(fitnesses)
        next_generation = []
        for p1, p2 in parents:
            c1, c2 = p1, p2
            c1, c2 = self.crossover(p1, p2)
            c1, c2 = self.mutate(c1, c2)
            next_generation.append(c1)
            next_generation.append(c2)
        self.generation = next_generation

    def run(self):
        while self.current_generation < self.generation_count:
            self.step()
            dec = self.decode(self.best_solution[0], self.cipher_text)
            print(dec)

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
        best_individ, _ = self.best_solution
        print(self.decode(best_individ, self.cipher_text))

    def mutate(self, child1, child2):
        if self.bin_rand(self.mutation_probability):
            a, b = random.sample(range(len(self.alphabet)), 2)
            child1[a], child1[b] = child1[b], child1[a]
        if self.bin_rand(self.mutation_probability):
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
        if self.bin_rand(self.crossover_probability):
            c1 = self.PBX(parent1, parent2, k)
        else:
            c1 = parent1
        if self.bin_rand(self.crossover_probability):
            c2 = self.PBX(parent2, parent1, k)
        else:
            c2 = parent2
        return c1, c2

    def report(self):
        best_solution, best_fitness = self.best_solution
        print(self.decode(best_solution, self.cipher_text))

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
        remaining = parent2[:]
        child = [None] * len(self.alphabet)
        for i in k:
            elem = parent1[i]
            child[i] = elem
            remaining.remove(elem)
        for index, i in zip(rev_k, remaining):
            child[index] = i
        return child

    @staticmethod
    def bin_rand(probability):
        return random.random() < probability
