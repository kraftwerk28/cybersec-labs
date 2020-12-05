package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"path"
	"strconv"
	"strings"
	"sync"
)

const ngramSetLength = 3

func getNgramPath(n int) string {
	var wd string
	switch n {
	case 3:
		wd = "tri"
	case 4:
		wd = "quad"
	case 5:
		wd = "quint"
	default:
		panic("Ngram length not supported")
	}
	return fmt.Sprintf("ngrams/english_%sgrams.txt", wd)
}

type NgramFreqMap map[string]int
type NgramSet map[int]NgramFreqMap

func ParseFreq(filepath string) NgramFreqMap {
	cwd, err := os.Getwd()
	result := make(map[string]int)
	if err != nil {
		panic(err)
	}

	fpath := path.Join(cwd, "..", filepath)
	fptr, err := os.Open(fpath)
	if err != nil {
		log.Fatalf("Failed to open file %v\n", fpath)
	}
	defer fptr.Close()

	scanner := bufio.NewScanner(fptr)
	for scanner.Scan() {
		arr := strings.Fields(scanner.Text())
		val, err := strconv.Atoi(arr[1])
		if err == nil {
			result[arr[0]] = val
		}
	}
	log.Printf("Parsed %d ngrams from %s\n", len(result), filepath)
	return result
}

func ParseFreqs() map[int]NgramFreqMap {
	result := make(map[int]NgramFreqMap, ngramSetLength)
	wg := sync.WaitGroup{}
	wg.Add(ngramSetLength)
	for i := 3; i < 3+ngramSetLength; i++ {
		path := getNgramPath(i)
		go func(k int, v string) {
			defer wg.Done()
			result[k] = ParseFreq(v)
		}(i, path)
	}
	wg.Wait()
	return result
}