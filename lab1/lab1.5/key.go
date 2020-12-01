package main

import (
	"math/rand"
	"strings"
)

type Key struct {
	key []rune
}

func randomKey() Key {
	letters := rand.Perm(len(alphabet))
	key := make([]rune, len(alphabet))
	for i, idx := range letters {
		key[idx] = alphabet[i]
	}
	return Key{key}
}

func (self *Key) encode(text string) string {
	ans := []rune(text)
	for i, l := range text {
		if idx, exists := alphMap[l]; exists {
			ans[i] = self.key[idx]
		}
	}
	return string(ans)
}

func (self *Key) decode(text string) string {
	ans := []rune(text)
	keyStr := string(self.key)
	for i, l := range text {
		idx := strings.IndexRune(keyStr, l)
		if idx >= 0 {
			ans[i] = alphabet[idx]
		}
	}
	return string(ans)
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
	i1, i2 := perm[0], perm[1]
	self.key[i1], self.key[i2] = self.key[i2], self.key[i1]
	return self
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
