package main

import (
	"math"
	"math/rand"
)

func alphabet2map(alphabet []rune) map[rune]int {
	m := make(map[rune]int)
	for i, letter := range alphabet {
		m[letter] = i
	}
	return m
}

func groups(text string, keyLen int) [][]rune {
	ans := make([][]rune, keyLen)
	i := 0
	for _, char := range text {
		ans[i] = append(ans[i], char)
		i = (i + 1) % keyLen
	}
	return ans
}

func ungroups(groups [][]rune) string {
	result := make([]rune, 0)
	i := 0
	for {
		if len(groups[i]) == 0 {
			break
		}
		r := groups[i][0]
		groups[i] = groups[i][1:]
		result = append(result, r)
		i = (i + 1) % len(groups)
	}
	return string(result)
}

func isProbably(prob float64) bool {
	return rand.Float64() < prob
}

func splitToNgrams(str string, ngramSize int) []string {
	nngrams := len(str) - ngramSize + 1
	result := make([]string, nngrams)
	for i := 0; i < nngrams; i++ {
		result[i] = str[i : i+ngramSize]
	}
	return result
}

func countFreqs(ngrams []string) NgramFreqMap {
	result := make(map[string]int)
	for _, w := range ngrams {
		result[string(w)]++
	}
	return result
}

func calcTournProb(initial float64, tournament_size int) []uint {
	const multiplier = 100000
	prev := initial
	ans := []uint{uint(math.Floor(initial * multiplier))}
	for i := 0; i < tournament_size-1; i++ {
		prev = prev * (1 - prev)
		floored := uint(math.Floor(multiplier * prev))
		ans = append(ans, floored)
	}
	return ans
}
