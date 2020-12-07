package main

import (
	"log"
	"math"
	"sort"
	"sync"

	"github.com/mroth/weightedrand"
)

const (
	STATUS_BETTER = iota
	STATUS_SAME
	STATUS_WORSE
)

type PolyGA struct {
	cipherText           []rune
	trainNgrams          NgramSet
	nGeneration          int
	unchangedGenerations int
	keyLen               int
	currentGen           []Individ
	bestIndivid          Individ
	bestFitness          float64
	status               int
}

type fitnessIndividual struct {
	individ Individ
	fitness float64
}

type parents struct {
	fst Individ
	snd Individ
}

func NewPolyGA(cipherText []rune, keyLen int, trainNgrams NgramSet) PolyGA {
	if population_size < tournament_size {
		panic("Tournament size must be <= of generation size")
	}
	generation := make([]Individ, population_size)
	for i := range generation {
		generation[i] = randomIndivid(keyLen)
	}

	return PolyGA{
		cipherText:  cipherText,
		trainNgrams: trainNgrams,
		keyLen:      keyLen,
		currentGen:  generation,
	}
}

func NewPolyGAwKeys(
	cipherText string,
	keys []string,
	trainNgrams NgramSet,
) PolyGA {
	if population_size < tournament_size {
		panic("Tournament size must be <= of generation size")
	}
	generation := make([]Individ, population_size)
	nKeys := len(keys)
	for i := range generation {
		keysCopy := make([]Key, nKeys)
		for i := range keys {
			keysCopy[i] = Key{[]rune(keys[i])}
		}
		generation[i] = Individ{keysCopy}
	}

	return PolyGA{
		cipherText:  []rune(cipherText),
		trainNgrams: trainNgrams,
		keyLen:      keyLen,
		currentGen:  generation,
	}
	// if len(keys) != self.
	// B ONG K ATULATIO
}

func (self *PolyGA) step() {
	self.nGeneration++

	indFit := self.individFitnessesPar()

	sortCb := func(i, j int) bool {
		return indFit[i].fitness >= indFit[j].fitness
	}
	sort.Slice(indFit, sortCb)

	newBest := indFit[0].fitness

	if partialEq(newBest, self.bestFitness) {
		self.unchangedGenerations++
		self.status = STATUS_SAME
	} else if newBest > self.bestFitness {
		self.unchangedGenerations = 0
		self.status = STATUS_BETTER
	} else {
		self.status = STATUS_WORSE
	}

	self.bestFitness = indFit[0].fitness
	self.bestIndivid = indFit[0].individ

	parents := self.selection(indFit)
	self.currentGen = make([]Individ, 0, population_size)

	for _, p := range parents {
		c1, c2 := p.get()
		if isProbably(crossover_probability) {
			c1, c2 = crossover(c1, c2)
		}
		if isProbably(mutation_probability) {
			c1, c2 = c1.mutate(), c2.mutate()
		}
		self.currentGen = append(self.currentGen, c1, c2)
	}
}

func (self parents) get() (Individ, Individ) {
	return self.fst, self.snd
}

// "Dumb" selection procedure
// func (self *PolyGA) selection(data []fitnessIndividual) []parents {
// 	tournament := data[:tournament_size]
// 	result := make([]parents, population_size/2)
// 	ti := 0
// 	for i := range result {
// 		child1 := tournament[ti].individ
// 		child2 := tournament[(ti+1)%tournament_size].individ
// 		result[i] = parents{child1, child2}
// 		ti = (ti + 1) % tournament_size
// 	}
// 	return result
// }

func (self *PolyGA) selection(data []fitnessIndividual) []parents {
	tournament := data[:tournament_size]

	choices := make([]weightedrand.Choice, tournament_size)
	for i := range tournament {
		choices[i] = weightedrand.NewChoice(
			&tournament[i],
			tournamentProbabilities[i],
		)
	}
	chooser, err := weightedrand.NewChooser(choices...)

	if err != nil {
		log.Fatalln(err)
	}

	result := make([]parents, 0)
	for i := 0; i < population_size/2; i++ {
		i1, i2 :=
			chooser.Pick().(*fitnessIndividual),
			chooser.Pick().(*fitnessIndividual)
		for i2 == i1 {
			i2 = chooser.Pick().(*fitnessIndividual)
		}
		par := parents{i1.individ, i2.individ}

		result = append(result, par)
	}

	return result
}

func (self *PolyGA) Run() {
	for self.unchangedGenerations < unchanged_threshold &&
		self.nGeneration < generation_count {
		self.step()
		self.report()
	}
}

func (self *PolyGA) report() {
	var strStatus string
	switch self.status {
	case STATUS_WORSE:
		strStatus = "Worse"
	case STATUS_SAME:
		strStatus = "Same  "
	case STATUS_BETTER:
		strStatus = "Better"
	}

	log.Printf("%-7v fitness: %v; key:\n", strStatus, self.bestFitness)

	for _, k := range self.bestIndivid.keys {
		log.Printf("|%v|\n", string(k.key))
	}
	decoded := self.bestIndivid.decode(self.cipherText)
	log.Println(string(decoded))
}

func (self *PolyGA) fitness(individ *Individ) (result float64) {
	for ngramSize, trainFreqs := range self.trainNgrams {
		decoded := individ.decode(self.cipherText)
		decodedNgrams := splitToNgrams(decoded, ngramSize)
		decodedFreqs := countFreqs(decodedNgrams)
		for ngram, fp := range decodedFreqs {
			if ft, ok := trainFreqs[ngram]; ok && ft > 0 {
				result += float64(fp) * math.Log2(float64(ft))
			}
		}
	}
	return
}

func (self *PolyGA) individFitnessesPar() []fitnessIndividual {
	result := make([]fitnessIndividual, 0, population_size)
	wg, ch := sync.WaitGroup{}, make(chan fitnessIndividual)

	for _, ind := range self.currentGen {
		wg.Add(1)
		go func(self *PolyGA, ind Individ, ch chan<- fitnessIndividual) {
			defer wg.Done()
			fitness := self.fitness(&ind)
			ch <- fitnessIndividual{ind, fitness}
		}(self, ind, ch)
	}

	go func(result *[]fitnessIndividual, ch <-chan fitnessIndividual) {
		for c := range ch {
			*result = append(*result, c)
		}
	}(&result, ch)

	wg.Wait()
	close(ch)

	return result
}

func (self *PolyGA) individFitnesses() []fitnessIndividual {
	result := make([]fitnessIndividual, population_size)
	for i, ind := range self.currentGen {
		fitness := self.fitness(&ind)
		result[i] = fitnessIndividual{ind, fitness}
	}
	return result
}
