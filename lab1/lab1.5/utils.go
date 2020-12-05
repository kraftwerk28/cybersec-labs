package main

import (
	"math"
	"math/rand"
)

type ngram []rune

func alphabet2map(alphabet []rune) map[rune]int {
	m := make(map[rune]int)
	for i, letter := range alphabet {
		m[letter] = i
	}
	return m
}

func groups(text []rune, keyLen int) (result [][]rune) {
	result = make([][]rune, keyLen)
	i := 0
	for _, char := range text {
		result[i] = append(result[i], char)
		i = (i + 1) % keyLen
	}
	return
}

func ungroups(groups [][]rune) (result []rune) {
	result = make([]rune, 0)
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
	return
}

func isProbably(prob float64) bool {
	return rand.Float64() < prob
}

func splitToNgrams(text []rune, ngramSize int) (result []ngram) {
	nngrams := len(text) - ngramSize + 1
	result = make([]ngram, nngrams)
	for i := 0; i < nngrams; i++ {
		result[i] = text[i : i+ngramSize]
	}
	return
}

func splitToNgramsWhitespaced(text []rune, ngramSize int) (result []ngram) {
	var idx int
	currentChunk := make([]rune, 0)
	for {
		if idx >= len(text) {
			break
		}
		if text[idx] == ' ' {
			if len(currentChunk) >= ngramSize {
				result = append(result, splitToNgrams(currentChunk, ngramSize)...)
			}
			currentChunk = make([]rune, 0)
		} else {
			currentChunk = append(currentChunk, text[idx])
		}
		idx++
	}
	if len(currentChunk) >= ngramSize {
		result = append(result, splitToNgrams(currentChunk, ngramSize)...)
	}
	return
}

func countFreqs(ngrams []ngram) NgramFreqMap {
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

func partialEq(a, b float64) bool {
	return math.Abs(a-b) < epsilon
}

func getSpacePositions(text string) map[int]bool {
	result := make(map[int]bool)
	var idx int
	for _, c := range text {
		if c == ' ' {
			result[idx] = true
		} else {
			idx++
		}
	}
	return result
}

func insertWhiteSpaces(raw []rune, positions map[int]bool) []rune {
	result := make([]rune, 0, len(raw)+len(positions))
	for i, c := range raw {
		if _, isWS := positions[i]; isWS {
			result = append(result, ' ')
		}
		result = append(result, c)
	}
	return result
}

func insertWhiteSpace(cipher, text string) string {
	textLen := len(text)
	ciphRunes := []rune(cipher)
	resRunes := make([]rune, 0, textLen)
	var idx int
	for _, c := range text {
		_, exists := alphMap[c]
		if exists {
			resRunes = append(resRunes, ciphRunes[idx])
			idx++
		} else {
			resRunes = append(resRunes, ' ')
		}
	}
	return string(resRunes)
}
