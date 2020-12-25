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

func getNgramPath(root string, n int) string {
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
	return path.Join(root, fmt.Sprintf("english_%sgrams.txt", wd))
}

type NgramFreqMap map[string]int
type NgramSet map[int]NgramFreqMap

func ParseFreq(filepath string) NgramFreqMap {
	result := make(map[string]int)

	fptr, err := os.Open(filepath)
	defer fptr.Close()
	if err != nil {
		log.Fatalf("Failed to open file %v\n", filepath)
	}

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

func ParseFrequencies(path string) map[int]NgramFreqMap {
	result := make(map[int]NgramFreqMap, ngramSetLength)
	wg := sync.WaitGroup{}
	wg.Add(ngramSetLength)
	for i := 3; i < 3+ngramSetLength; i++ {
		path := getNgramPath(path, i)
		go func(k int, v string) {
			defer wg.Done()
			result[k] = ParseFreq(v)
		}(i, path)
	}
	wg.Wait()
	return result
}

func ParseTopWords(path string) map[string]int {
	fd, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
	}
	sc, lines := bufio.NewScanner(fd), make([]string, 0)
	for sc.Scan() {
		word := strings.ToUpper(sc.Text())
		lines = append(lines, word)
	}
	result := make(map[string]int, len(lines))
	for i := range lines {
		result[lines[i]] = len(lines) - i
	}
	return result
}
