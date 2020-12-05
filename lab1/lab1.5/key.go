package main

import (
	"math/rand"
	"strings"
)

type Key struct{ key []rune }

func randomKey() Key {
	letters := rand.Perm(len(alphabet))
	key := make([]rune, len(alphabet))
	for i, idx := range letters {
		key[idx] = alphabet[i]
	}
	return Key{key}
}

func (self *Key) encode(text []rune) []rune {
	ans := text
	for i, l := range text {
		if idx, exists := alphMap[l]; exists {
			ans[i] = self.key[idx]
		}
	}
	return ans
}

func (self *Key) decode(text []rune) []rune {
	ans := text
	keyStr := string(self.key)
	for i, l := range text {
		idx := strings.IndexRune(keyStr, l) // 2
		if idx >= 0 {
			ans[i] = alphabet[idx]
		}
	}
	return ans
}

func pbx(k1, k2 Key) (Key, Key) {
	kPoints := rand.Perm(keyLen)
	taken1, taken2 := make(map[rune]bool), make(map[rune]bool)
	res1, res2 := make([]rune, keyLen), make([]rune, keyLen)

	for _, kPoint := range kPoints[:crossover_k_count] {
		l1, l2 := k1.key[kPoint], k2.key[kPoint]
		taken1[l1], taken2[l2] = true, true
		res1[kPoint], res2[kPoint] = l1, l2
	}

	var idx1, idx2 int
	for _, kPoint := range kPoints[crossover_k_count:] {
		l1, l2 := k2.key[idx1], k1.key[idx2]
		for {
			if _, taken := taken1[l1]; taken {
				idx1++
				l1 = k2.key[idx1]
			} else {
				break
			}
		}
		for {
			if _, taken := taken2[l2]; taken {
				idx2++
				l2 = k1.key[idx2]
			} else {
				break
			}
		}
		res1[kPoint], res2[kPoint] = k2.key[idx1], k1.key[idx2]
		idx1++
		idx2++
	}

	return Key{res1}, Key{res2}
}

func (self Key) crossover(other Key) Key {
	kPoints := rand.Perm(keyLen)
	taken := make(map[rune]bool)
	result := make([]rune, keyLen)
	for _, kPoint := range kPoints[:crossover_k_count] {
		letter := self.key[kPoint]
		taken[letter] = true
		result[kPoint] = letter
	}

	var idx int
	for _, kPoint := range kPoints[crossover_k_count:] {
		letter := other.key[idx]
		for {
			if _, taken := taken[letter]; taken {
				idx++
				letter = other.key[idx]
			} else {
				break
			}
		}
		result[kPoint] = letter
		idx++
	}

	return Key{result}
}

func (self Key) swapMutate() Key {
	perm := rand.Perm(len(self.key))
	key := make([]rune, keyLen)
	copy(key, self.key)
	i1, i2 := perm[0], perm[1]
	key[i1], key[i2] = key[i2], key[i1]
	return Key{key}
}

func (self *Key) String() string {
	return string(self.key)
}

func (self *Key) isValid() bool {
	letters := make(map[rune]bool)
	for _, letter := range self.key {
		_, taken := letters[letter]
		if taken {
			return false
		}
		letters[letter] = true
	}
	return true
}

func (self *Key) Copy() Key {
	key := make([]rune, keyLen)
	for i := range key {
		key[i] = self.key[i]
	}
	return Key{key}
}

func FromString(key string) Key {
	return Key{[]rune(key)}
}
