package main

import "strings"

type Individ struct{ keys []Key }

func crossover(i1, i2 Individ) (Individ, Individ) {
	nKeys := len(i1.keys)
	k1, k2 := make([]Key, nKeys), make([]Key, nKeys)
	for i := range i1.keys {
		k1[i], k2[i] = pbx(i1.keys[i], i2.keys[i])
	}
	return Individ{k1}, Individ{k2}
}

// func (self Individ) crossover(other Individ) Individ {
// 	keys := make([]Key, len(self.keys))
// 	for i := range self.keys {
// 		keys[i] = self.keys[i].crossover(other.keys[i])
// 		self.keys[i] = self.keys[i].crossover(other.keys[i])
// 	}
// 	return Individ{keys}
// }

func (self Individ) mutate() Individ {
	keys := make([]Key, len(self.keys))
	for i := range self.keys {
		keys[i] = self.keys[i].swapMutate()
	}
	return Individ{keys}
}

func randomIndivid(keyLen int) Individ {
	keys := make([]Key, keyLen)
	for i := range keys {
		keys[i] = randomKey()
	}
	return Individ{keys}
}

func (self *Individ) decode(text []rune) []rune {
	groups := groups(text, len(self.keys))
	for i, key := range self.keys {
		groups[i] = key.decode(groups[i])
	}
	return ungroups(groups)
}

func (self *Individ) encode(text []rune) []rune {
	keyLen := len(self.keys)
	groups := groups(text, keyLen)
	for i, key := range self.keys {
		groups[i] = key.encode(groups[i])
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

func FromStrKeys(skeys []string) Individ {
	nKeys := len(skeys)
	keys := make([]Key, nKeys)
	for i := range keys {
		keys[i] = FromString(skeys[i])
	}
	return Individ{keys}
}
