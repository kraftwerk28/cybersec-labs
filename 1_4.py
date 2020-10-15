#!/usr/bin/env python
import math
from pprint import pprint
import random
import string
from utils import *


m = """EFFPQLEKVTVPCPYFLMVHQLUEWCNVWFYGHYTCETHQEKLPVMSAKSPVPAPVYWMVHQLUSPQLYWLASLFVWPQLMVHQLUPLRPSQLULQESPBLWPCSVRVWFLHLWFLWPUEWFYOTCMQYSLWOYWYETHQEKLPVMSAKSPVPAPVYWHEPPLUWSGYULEMQTLPPLUGUYOLWDTVSQETHQEKLPVPVSMTLEUPQEPCYAMEWWYTYWDLUULTCYWPQLSEOLSVOHTLUYAPVWLYGDALSSVWDPQLNLCKCLRQEASPVILSLEUMQBQVMQCYAHUYKEKTCASLFPYFLMVHQLUPQLHULIVYASHEUEDUEHQBVTTPQLVWFLRYGMYVWMVFLWMLSPVTTBYUNESESADDLSPVYWCYAMEWPUCPYFVIVFLPQLOLSSEDLVWHEUPSKCPQLWAOKLUYGMQEUEMPLUSVWENLCEWFEHHTCGULXALWMCEWETCSVSPYLEMQYGPQLOMEWCYAGVWFEBECPYASLQVDQLUYUFLUGULXALWMCSPEPVSPVMSBVPQPQVSPCHLYGMVHQLUPQLWLRPOEDVMETBYUFBVTTPENLPYPQLWLRPTEKLWZYCKVPTCSTESQPQULLGYAUMEHVPETFWMEHVPETBZMEHVPETB"""


m = """AFFRONTINGDISCRETIONASDOISANNOUNCINGNOWMONTHSESTEEMOPPOSENEARERENABLETOOSIXSHENUMEROUSUNLOCKEDYOUPERCEIVESPEEDILYAFFIXEDOFFENCESPIRITSORYEOFOFFICESBETWEENREALONSHOTITWEREFOURANASABSOLUTEBACHELORRENDEREDSIXNAYYOUJUVENILEVANITYENTIREANCHATTYTOATDISTANTINHABITAMONGSTBYAPPETITEWELCOMEDINTERESTTHEGOODNESSBOYNOTESTIMABLEEDUCATIONFORDISPOSINGPRONOUNCEHERJOHNSIZEGOODGAYPLANSENTOLDROOFOWNINQUIETUDESAWUNDERSTOODHISFRIENDSHIPFREQUENTLYYETNATUREHISMARKEDHAMWISHEDWOODYEQUALASKSAWSIRWEEKSAWAREDECAYENTRANCEPROSPECTREMOVINGWEPACKAGESSTRICTLYISNOSMALLESTHEFORHOPESMAYCHIEFGETHOURSDAYROOMSOHNOTURNEDBEHINDPOLITEPIQUEDENOUGHATFORBADEFEWTHROUGHINQUIRYBLUSHESYOUCOUSINNOITSELFELDESTITINDINNERLATTERMISSEDNOBOISTEROUSESTIMATINGINTERESTEDCOLLECTINGGETCONVICTIONFRIENDSHIPSAYBOYHIMMRSSHYARTICLESMILINGRESPECTOPINIONEXCITEDWELCOMEDHUMOUREDREJOICEDPECULIARTOINANNOWINDULGENCEDISSIMILARFORHISTHOROUGHLYHASTERMINATEDAGREEMENTOFFENDINGCOMMANDEDMYANCHANGEWHOLLYSAYWHYELDESTPERIODAREPROJECTIONPUTCELEBRATEDPARTICULARUNRESERVEDJOYUNSATIABLEITSINTHENDAREGOODAMROSEBREDORONAMINNEARERSQUAREWANTEDTOSHEWINGANOTHERDEMANDSTOMARIANNEPROPERTYCHEERFULINFORMEDATSTRIKINGATCLOTHESPARLORSHOWEVERBYCOTTAGEONINVIEWSITORMEANTDRIFTTOBECONCERNPARLORSSETTLEDORDOSHYNESSADDRESSREMAINDERNORTHWARDPERFORMEDOUTFORMOONLIGHTYETLATEADDNAMEWASRENTPARKFROMRICHHEALWAYSDODOFORMERHEHIGHLY"""

# Freq (in %)
LETTER_FREQ = {
    'E': 12.02,
    'T': 9.10,
    'A': 8.12,
    'O': 7.68,
    'I': 7.31,
    'N': 6.95,
    'S': 6.28,
    'R': 6.02,
    'H': 5.92,
    'D': 4.32,
    'L': 3.98,
    'U': 2.88,
    'C': 2.71,
    'M': 2.61,
    'F': 2.30,
    'Y': 2.11,
    'W': 2.09,
    'G': 2.03,
    'P': 1.82,
    'B': 1.49,
    'V': 1.11,
    'K': 0.69,
    'X': 0.17,
    'Q': 0.11,
    'J': 0.10,
    'Z': 0.07,
}


class GeneticAlg:
    alphabet = list(string.ascii_uppercase)
    alen = len(alphabet)
    population_size = 20
    generation_count = 20
    crossover_points = 10
    mutation_probability = 0.2
    crossover_probability = 0.2

    def __init__(self, message, correct_key=None):
        self.expected = 30
        self.correct_key = correct_key
        self.message = message
        self.expected_freq = {letter: (freq / 100) * len(message)
                              for letter, freq in LETTER_FREQ.items()}
        self.real_freq = {letter: message.count(letter)
                          for letter in self.alphabet}
        self.current_generation = 0
        self.best_ind = None
        self.gen = [random.sample(self.alphabet, len(self.alphabet))
                    for _ in range(self.population_size)]

    def gen_step(self):
        self.current_generation += 1
        fitnesses = [self.fitness(ind) for ind in self.gen]
        zipped = zip(self.gen, fitnesses)
        pprint(list(zip([''.join(g) for g in self.gen], fitnesses)))
        max_ind = max(zipped, key=lambda item: item[1])
        report = (f'\nGeneration #{self.current_generation}: '
                  'key = {}, fitness = {}'.format(''.join(
                      max_ind[0]), max_ind[1]))

        if self.current_generation > 1:
            is_better = max_ind[1] > self.best_ind[1]
            report += '; {}'.format('good' if is_better else 'bad')
        print(report)

        pairs = self.selection(fitnesses)
        pprint((''.join(k), ''.join(k)))
        new_gen = []
        for p1, p2 in pairs:
            c1, c2 = self.crossover(p1, p2), self.crossover(p1, p2, True)
            # if self.bin_rand(self.mutation_probability):
            #     c1 = self.mutate(c1, c2)
            # if self.bin_rand(self.mutation_probability):
            #     c2 = self.mutate(c1, c2, True)
            new_gen.append(c1)
            new_gen.append(c2)
        self.best_ind = max_ind
        self.gen = new_gen

    def selection(self, fitnesses):
        return [random.choices(self.gen, k=2, weights=fitnesses)
                for _ in range(self.population_size // 2)]

    def run(self):
        while self.current_generation < self.generation_count:
            self.gen_step()
            if self.correct_key is not None:
                correct_let = sum(a == b for a, b in
                                  zip(self.correct_key, self.best_ind[0]))
                print(f'Correctness = {correct_let}')

            dec = self.decode(self.best_ind[0], self.message)
            if all(word in dec for word in ['OK', 'THE']):
                print(self.best_ind, dec)

    def mutate(self, c1, c2, reverse=False):
        bin_vec = random.choices((True, False), k=self.alen)
        mutant, rem_indexes = [], []
        for index, flag in enumerate(bin_vec):
            if flag and not reverse:
                mutant.append(c1[index])
            elif not flag and reverse:
                mutant.append(c2[index])
            else:
                mutant.append(None)
                rem_indexes.append(index)
        rem_letters = [letter
                       for letter in (c1 if reverse else c2)
                       if letter not in mutant]
        for index, letter in zip(rem_indexes, rem_letters):
            mutant[index] = letter
        return mutant

    def fitness(self, ind) -> float:
        ind_decrypt = self.decode(ind, self.message)
        a = 2*(len(self.message) - min(self.expected_freq.values()))
        e = sum(abs(self.expected_freq[letter] - ind_decrypt.count(letter))
                for letter in self.alphabet)
        return (a - e) / a

        # T = self.ngrams(self.message, self.ngram_size)
        # N = self.ngrams(ind_decrypt, self.ngram_size)

        # def F(ngram):
        #     ft = T.count(ngram)
        #     if ft == 0:
        #         return 0
        #     fp = N.count(ngram)
        #     return fp * math.log2(ft)

        # return sum(F(ngram) for ngram in N)

    def crossover(self, parent1, parent2, reverse=False):
        child, empty_indices = [], []
        remaining_letters = set(self.alphabet)
        zipped = list(enumerate(zip(parent1, parent2)))
        for index, (p1, p2) in reversed(zipped) if reverse else zipped:
            d1 = abs(self.real_freq[p1] - self.expected_freq[p1])
            d2 = abs(self.real_freq[p2] - self.expected_freq[p2])
            p, p_fallback = (p1, p2) if d1 < d2 else (p2, p1)
            if p not in child:
                child.append(p)
                remaining_letters.remove(p)
            elif p_fallback not in child:
                child.append(p_fallback)
                remaining_letters.remove(p_fallback)
            else:
                empty_indices.append(self.alen - index - 1 if reverse
                                     else index)
                child.append(None)
        for i, p in zip(empty_indices, remaining_letters):
            child[i] = p
        return child

    @staticmethod
    def ngrams(word, n):
        return [word[i:i + n] for i in range(len(word) - n + 1)]

    @classmethod
    def decode(self, key, message):
        return ''.join(self.alphabet[key.index(letter)] for letter in message)

    @classmethod
    def encode(self, key, message):
        return ''.join(key[self.alphabet.index(letter)] for letter in message)

    @classmethod
    def PBX(self, parent1, parent2, k):
        rev_k = [i for i in range(self.alen) if i not in k]
        p2_set = set(parent2)
        child = [None] * self.alen
        for i in k:
            elem = parent1[i]
            child[i] = elem
            p2_set.remove(elem)
        p2_rem = list(p2_set)
        for index, i in enumerate(rev_k):
            child[i] = p2_rem[index]
        return ''.join(child)

    @staticmethod
    def bin_rand(probability):
        return random.random() < probability


if __name__ == '__main__':
    key = 'UTYZKEWBADMPLIOSNHJFRVGQXC'
    enc = GeneticAlg.encode(key, m)
    alg = GeneticAlg(enc, correct_key=key)
    alg.run()

    # Mutation algorithm testing
    # bin_vec = [bool(int(i)) for i in '10111001101010100011110111']
    # c1 = 'SUQHCLADFGJKNOPTVWXZBEMRIY'
    # c2 = 'AZBYXCWDEVUFGTSHRIQJPKLOMN'
    # reverse = False
    # mutant, rem_indexes = [], []
    # for index, flag in enumerate(bin_vec):
    #     if flag and not reverse:
    #         mutant.append(c1[index])
    #     elif not flag and reverse:
    #         mutant.append(c2[index])
    #     else:
    #         mutant.append(None)
    #         rem_indexes.append(index)
    # rem_letters = [letter
    #                for letter in (c1 if reverse else c2)
    #                if letter not in mutant]
    # for index, letter in zip(rem_indexes, rem_letters):
    #     mutant[index] = letter
    # res = ''.join(mutant)
    # assert('SAQHCWVDFUJGNTPKLOXZBEMRIY' == res)

    # Crossover algorithm check
    # def tr(k, v):
    #     return dict(zip(k.split(), [int(a) for a in v.split()]))
    # T = tr('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z',
    #        '224 93 0 259 131 203 84 27 92 87 141 212 3 39 173 238 10 221 12 98 59 31 61 0 354 149')
    # E = tr('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z',
    #        '246 46 50 134 378 80 53 248 189 8 23 121 76 192 243 40 1 161 187 261 81 30 75 2 74 3')

    # p1 = tr('D N Q E P J O R G C S V K',
    #         '259 39 10 131 238 87 173 221 84 0 12 31 141')
    # p2 = tr('P Q N H D J B F I O Y V G A W S E T X R K L Z C U M',
    #         '238 10 39 27 259 87 93 203 92 173 354 31 84 224 61 12 131 98 0 221 141 212 149 0 59 3')
    # reverse = False

    # child, empty_indices = [], []
    # remaining_letters = set(GeneticAlg.alphabet)
    # zipped = list(enumerate(zip(p1, p2)))
    # for index, (p1, p2) in reversed(zipped) if reverse else zipped:
    #     d1 = abs(T[p1] - E[p1])
    #     d2 = abs(T[p2] - E[p2])
    #     print(d1, d2)
    #     p, p_fallback = (p1, p2) if d1 < d2 else (p2, p1)
    #     if p not in child:
    #         child.append(p)
    #         remaining_letters.remove(p)
    #     elif p_fallback not in child:
    #         child.append(p_fallback)
    #         remaining_letters.remove(p_fallback)
    #     else:
    #         empty_indices.append(GeneticAlg.alen - index - 1 if reverse
    #                              else index)
    #         child.append(None)
    # for i, p in zip(empty_indices, remaining_letters):
    #     child[i] = p
    # print(''.join(child))
