UPPER = 0x80000000
LOWER = 0x7fffffff


class MT19937Gen:
    def __init__(self, seed=None):
        self.mt = [0 for _ in range(624)]
        self.index = 624
        if seed is not None:
            self._seed(seed)

    def _seed(self, seed):
        self.mt[0] = seed
        for i in range(1, 624):
            init = 0x6c078965 * (self.mt[i - 1] ^ (self.mt[i - 1] >> 30)) + i
            self.mt[i] = self._i32(init)

    def next(self):
        if self.index >= 624:
            self._twist()
        x = self.mt[self.index]
        x ^= x >> 11
        x ^= (x << 7) & 0x9d2c5680
        x ^= (x << 15) & 0xefc60000
        x ^= x >> 18
        self.index += 1
        return self._i32(x)

    def _twist(self):
        for i in range(624):

            x = self._i32((self.mt[i] & UPPER) +
                          (self.mt[(i + 1) % 624] & LOWER))
            self.mt[i] = self.mt[(i + 397) % 624] ^ (x >> 1)

            if x & 1 != 0:
                self.mt[i] ^= 0x9908b0df

        self.index = 0

    def _i32(self, x):
        return x & 0xffffffff


if __name__ == '__main__':
    mt = MT19937Gen(0)
    for _ in range(10):
        print(mt.extract())
