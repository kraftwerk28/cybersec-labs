from typing import List
from mtimpl import MT19937Gen, UPPER, LOWER


def unshift_r(inp, n):
    res = inp
    for _ in range(32):
        res = inp ^ res >> n
    return res


def unshift_l(inp, n, bitmask):
    res = inp
    for _ in range(32):
        res = inp ^ (res << n & bitmask)
    return res


class MTCrack:
    def __init__(self, inputs: List[int]):
        self.mt = inputs

    def backtrack(self) -> MT19937Gen:
        self.mt = [self._unstep(n) for n in self.mt]
        rng = MT19937Gen()
        rng.mt = self.mt[:]
        rng.index = 0
        return rng

    def make_rng(self) -> MT19937Gen:
        rng = self.backtrack()
        [rng.next() for _ in range(624)]
        return rng

    def _unstep(self, n):
        res = n
        res = unshift_r(res, 18)
        res = unshift_l(res, 15, 0xefc60000)
        res = unshift_l(res, 7, 0x9d2c5680)
        res = unshift_r(res, 11)
        return res


if __name__ == '__main__':
    rng = MT19937Gen(1303091290)
    inputs = [rng.next() for _ in range(624)]

    cracked_rng = MTCrack(inputs).make_rng()
    for _ in range(20):
        x, y = rng.next(), cracked_rng.next()
        assert x == y
