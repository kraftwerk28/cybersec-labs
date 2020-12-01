package main

import "strings"

type Individ struct {
	keys []Key
}

func (self Individ) crossover(other Individ) Individ {
	for i := range self.keys {
		self.keys[i] = self.keys[i].crossover(other.keys[i])
	}
	return self
}

func (self Individ) mutate() Individ {
	for i := range self.keys {
		self.keys[i] = self.keys[i].swapMutate()
	}
	return self
}

func randomIndivid(keyLen int) Individ {
	keys := make([]Key, keyLen)
	for i := range keys {
		keys[i] = randomKey()
	}
	return Individ{keys}
}

func (self *Individ) decode(text string) string {
	groups := groups(text, len(self.keys))
	for i, key := range self.keys {
		groups[i] = []rune(key.decode(string(groups[i])))
	}
	return ungroups(groups)
}

func (self *Individ) encode(text string) string {
	groups := groups(text, len(self.keys))
	for i, key := range self.keys {
		groups[i] = []rune(key.encode(string(groups[i])))
	}
	return ungroups(groups)
}

func (self *Individ) String() string {
	skeys := make([]string, len(self.keys))
	for i, key := range self.keys {
		skeys[i] = string(key.key)
	}
	return "[" + strings.Join(skeys, ", ") + "]"
}

func (self *Individ) isValid() bool {
	for _, key := range self.keys {
		if !key.isValid() {
			return false
		}
	}
	return true
}
