package main

import (
	"reflect"
	"testing"
)

const text = "loremipsumdolor"

// func runeEq(a, b [][]rune) bool {
// 	for i := range a {
// 		for j := range a[i] {
// 			x, y := a[i][j], b[i][j]
// 			if x != y {
// 				return false
// 			}
// 		}
// 	}
// 	return true
// }

func TestGroups(t *testing.T) {
	grouped := groups(text, 4)
	exp := [][]rune{
		[]rune("lmul"),
		[]rune("oimo"),
		[]rune("rpdr"),
		[]rune("eso"),
	}
	if !reflect.DeepEqual(grouped, exp) {
		t.Fail()
	}
}

func TestUngroups(t *testing.T) {
	grouped := groups(text, 4)
	ungrouped := ungroups(grouped)
	if ungrouped != text {
		t.Fail()
	}
}

func TestProbably(t *testing.T) {
	if isProbably(0) == true {
		t.Fail()
	}
	if isProbably(1) == false {
		t.Fail()
	}
}

func TestCountFreq(t *testing.T) {
	ngrams := []string{
		"AAB",
		"KEK",
		"LOL",
		"KEK",
		"AAB",
		"AAB",
	}
	freqMap := countFreqs(ngrams)
	exp := NgramFreqMap{
		"AAB": 3,
		"KEK": 2,
		"LOL": 1,
	}
	if !reflect.DeepEqual(freqMap, exp) {
		t.Fail()
	}
}
