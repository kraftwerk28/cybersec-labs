package main

var alphabet = []rune("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
var alphMap = alphabet2map(alphabet)
var tournamentProbabilities = calcTournProb(
	tournament_win_prob,
	tournament_size,
)
var keyLen = len(alphabet)

const (
	population_size               = 100
	generation_count              = 1000
	mutation_probability  float64 = 0.65
	crossover_k_count             = 20
	crossover_probability float64 = 0.65
	tournament_win_prob           = 0.75
	tournament_size               = 10
	unchanged_threshold           = 50
)

const dbgDelay = 1000
