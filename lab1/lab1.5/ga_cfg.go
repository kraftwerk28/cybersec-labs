package main

var alphabet = getAlphabet()
var keyLen = len(alphabet)
var alphMap = alphabet2map(alphabet)
var tournamentProbabilities = calcTournProb(
	tournament_win_prob,
	tournament_size,
)

const (
	population_size       = 300
	generation_count      = 1000
	mutation_probability  = 0.85
	crossover_k_count     = 20
	crossover_probability = 0.35
	tournament_win_prob   = 0.75
	tournament_size       = 30

	// After how many unchanged max fitness I should stop
	unchanged_threshold = 50

	// Used for fitness comparison
	epsilon = 0.0000001

	// 1 - trigrams, 2 - quadgrams + 1, 3 - quintgrams + 1 + 2
	ngramSetLength = 3
)

func getAlphabet() []rune {
	alph := "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	return []rune(alph)
	// b := make([]rune, 26 + 26)
	// for i := range b {
	// 	b[i] = rune(i)
	// }
	// return b
}
