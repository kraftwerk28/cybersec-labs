#!/usr/bin/env python
import math
from matplotlib import pyplot as plt
import matplotlib
import re
import random
import string

ALPHABET = string.ascii_lowercase
matplotlib.use('GTK3Agg')


def set_alphabet(alphabet):
    global ALPHABET
    ALPHABET = alphabet


def get_alphabet():
    return ALPHABET


def expand_key(key, length):
    return (key * math.ceil(length / len(key)))[:length]


def xor_strings(message, key, msg_len=0) -> str:
    if type(message) == str:
        bmessage = bytes(message, encoding='utf-8')
    else:
        bmessage = bytes(message)
    if type(key) in (str, bytes):
        byteskey = bytes(key, encoding='utf-8') if type(key) == str else key
        bkey = expand_key(byteskey, len(bmessage))
    elif type(key) == int:
        if key > 255:
            byteskey = key.to_bytes((key.bit_length() + 7) // 8, 'big')
            bkey = expand_key(byteskey, len(bmessage))
        else:
            if msg_len > 0:
                padded_arr = [0] * (msg_len - 1) + [key]
                bkey = expand_key(padded_arr, len(bmessage))
            else:
                bkey = [key] * len(bmessage)
    return ''.join(chr(a ^ b) for a, b in zip(bmessage, bkey))


def repeats(s, start_length=2, end_length=None):
    found_strings = {}
    for substr_len in range(end_length or len(s), start_length, -1):
        for i in range(len(s) - substr_len):
            searched_str = s[i:i + substr_len]
            rep_count, current_offset = 0, 0
            s_copy, found_indexes = s[:], []
            idx = s_copy.find(searched_str)
            while idx >= 0 and s_copy:
                found_indexes.append(idx + current_offset)
                current_offset = idx + substr_len
                s_copy = s_copy[current_offset:]
                idx = s_copy.find(searched_str)
                rep_count += 1
            if (rep_count > 1
                    and all(searched_str not in s
                            for s in found_strings.keys())):
                found_strings[searched_str] = found_indexes
    return found_strings


def letter_frequencies(text, l):
    ans = {}
    for l in text:
        if l in ans:
            ans[l] += 1
        else:
            ans[l] = 1
    return dict(sorted(ans.items(), key=lambda item: item[1], reverse=True))


def vigenere(message, key, alphabet=ALPHABET):
    m_l, k_l, a_l = len(message), len(key), len(alphabet)
    fullkey = key * (m_l // k_l) + key[:m_l % k_l]
    return ''.join(alphabet[(alphabet.index(m) + alphabet.index(k)) % a_l]
                   for m, k in zip(message, fullkey))


def devigenere(message, key, alphabet=ALPHABET):
    m_l, k_l, a_l = len(message), len(key), len(alphabet)
    fullkey = key * (m_l // k_l) + key[:m_l % k_l]
    return ''.join(alphabet[(alphabet.index(m) - alphabet.index(k)) % a_l]
                   for m, k in zip(message, fullkey))


def IoC(text, alphabet=ALPHABET):
    ans = 0
    tl = len(text)
    for letter in alphabet:
        occ = sum(letter == x for x in text)
        ans += (occ * (occ - 1)) / (tl * (tl - 1))
    return ans


def group(text, t):
    ans = [[] for _ in range(t)]
    i = 0
    for l in text:
        ans[i].append(l)
        i = (i + 1) % t
    return ans


def ungroup(groups):
    glists = [list(group) for group in groups]
    i, t = 0, len(glists)
    ans = []
    while glists[i]:
        ans.append(glists[i].pop(0))
        i = (i + 1) % t
    return ''.join(ans)


def plot_ioc(text, alphabet=ALPHABET, start=2, end=50):
    iocs = []
    for i in range(start, end):
        iocs_local = [IoC(g, alphabet) for g in group(text, i)]
        iocs.append(sum(iocs_local) / len(iocs_local))
    plt.plot(iocs)
    plt.show()


def caesar(text, letter, alphabet=ALPHABET):
    if type(letter) == str:
        letter = alphabet.find(letter)
    return ''.join(alphabet[(alphabet.find(t) + letter) % len(alphabet)]
                   for t in text)


def split_to_ngrams(text, t):
    return [''.join(text[i:i+t])
            for i in range(len(text) - t + 1)]


def ngram_freq(ngrams):
    return {ngram: ngrams.count(ngram) for ngram in ngrams}


def parse_ngrams(filename):
    ans = {}
    for line in open(filename, 'r'):
        ngram, cnt = line.split()
        ans[ngram] = int(cnt)
    return ans


def calc_freq(ngrams):
    return {ngram: ngrams.count(ngram) for ngram in ngrams}


def prepare_text(text, upper=True):
    text = train_text = re.sub(r'[^A-Za-z]+', '', text)
    if upper:
        return text.upper()
    return text


def calc_tournament_probabilities(initial, tournament_size):
    prev = initial
    ans = [initial]
    for _ in range(tournament_size - 1):
        p = prev * (1 - prev)
        ans.append(p)
        prev = p
    return ans


def prob(probability: float):
    return random.random() < probability

# def chi_squared(text, expected=EXPECTED,
#                 alphabet=ALPHABET):
#     return sum((sum(letter == x for x in text) - expected[index]) ** 2 /
#                expected[index]
#                for index, letter in enumerate(alphabet))
