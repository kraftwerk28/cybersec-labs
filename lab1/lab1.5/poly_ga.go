package main

import (
	"log"
	"math"
	"sort"
	"time"

	"github.com/mroth/weightedrand"
)

type PolyGA struct {
	cipherText           string
	trainNgrams          NgramSet
	nGeneration          int
	unchangedGenerations int
	keyLen               int
	currentGen           []Individ
	bestIndivid          Individ
	bestFitness          float64
}

type fitnessIndividual struct {
	individ Individ
	fitness float64
}

type parents struct {
	fst Individ
	snd Individ
}

func NewPolyGA(cipherText string, keyLen int) *PolyGA {
	generation := make([]Individ, population_size)

	for i := range generation {
		generation[i] = randomIndivid(keyLen)
	}
	return &PolyGA{
		cipherText:  cipherText,
		trainNgrams: ParseFreqs(),
		keyLen:      keyLen,
		currentGen:  generation,
	}
}

func (self *PolyGA) step() {
	self.nGeneration++

	indFit := make([]fitnessIndividual, population_size)
	for i, ind := range self.currentGen {
		fitness := self.fitness(&ind)
		indFit[i] = fitnessIndividual{ind, fitness}
	}
	sortCb := func(i, j int) bool {
		return indFit[i].fitness >= indFit[j].fitness
	}
	sort.Slice(indFit, sortCb)
	for _, indFit := range indFit {
		log.Println(indFit.fitness)
	}

	if indFit[0].fitness > self.bestFitness {
		self.unchangedGenerations = 0
	} else {
		self.unchangedGenerations++
	}
	self.bestFitness = indFit[0].fitness
	self.bestIndivid = indFit[0].individ

	parents := self.selection(indFit)
	nextGeneration := make([]Individ, 0, population_size)
	for _, p := range parents {
		c1, c2 := p.get()
		if isProbably(crossover_probability) {
			c1, c2 = c1.crossover(c2), c2.crossover(c1)
		}
		if isProbably(mutation_probability) {
			c1, c2 = c1.mutate(), c2.mutate()
		}
		nextGeneration = append(nextGeneration, c1, c2)
	}
	self.currentGen = nextGeneration

	if dbgDelay > 0 {
		time.Sleep(time.Millisecond * dbgDelay)
	}
}

func (self parents) get() (Individ, Individ) {
	return self.fst, self.snd
}

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
	log.Printf(
		"%v; fitness: %v; key:\n",
		self.unchangedGenerations,
		self.bestFitness,
	)
	for _, k := range self.bestIndivid.keys {
		log.Printf("|%v|\n", string(k.key))
	}
	log.Println(self.bestIndivid.decode(self.cipherText))
	time.Sleep(time.Millisecond * 100)
}

func (self *PolyGA) fitness(individ *Individ) (result float64) {
	// ch, wg := make(chan float64), sync.WaitGroup{}

	for ngramSize, trainFreqs := range self.trainNgrams {
		decoded := individ.decode(self.cipherText)
		decodedNgrams := splitToNgrams(decoded, ngramSize)
		decodedFreqs := countFreqs(decodedNgrams)

		for ngram, fp := range decodedFreqs {
			if ft, ok := trainFreqs[ngram]; ok && ft > 0 {
				result += float64(fp) * math.Log2(float64(ft))
				// ch <- float64(fp) * math.Log2(float64(ft))
			}
		}

		// wg.Add(1)
		// go func(ngramSize int, trainFreqs NgramFreqMap, ch chan float64) {
		// 	defer wg.Done()
		// 	decoded := individ.decode(self.cipherText)
		// 	decodedNgrams := splitToNgrams(decoded, ngramSize)
		// 	decodedFreqs := countFreqs(decodedNgrams)

		// 	for ngram, fp := range decodedFreqs {
		// 		if ft, ok := trainFreqs[ngram]; ok && ft > 0 {
		// 			ch <- float64(fp) * math.Log2(float64(ft))
		// 		}
		// 	}
		// }(ngramSize, trainFreqs, ch)
	}

	// go func() {
	// 	wg.Wait()
	// 	close(ch)
	// }()

	// for i := range ch {
	// 	result += i
	// }

	return
}
