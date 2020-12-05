package main

var alphabet = []rune("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
var alphMap = alphabet2map(alphabet)
var tournamentProbabilities = calcTournProb(
	tournament_win_prob,
	tournament_size,
)
var keyLen = len(alphabet)
var whitespacePositions = getSpacePositions(recentDecoded)

const (
	population_size       = 300
	generation_count      = 1000
	mutation_probability  = 0.85
	crossover_k_count     = 20
	crossover_probability = 0.35
	tournament_win_prob   = 0.75
	tournament_size       = 40

	// After how many unchanged max fitness I should stop
	unchanged_threshold = 100

	// Used for fitness comparison
	epsilon = 0.0000001
)
