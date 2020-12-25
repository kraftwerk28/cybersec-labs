package main

import (
	"encoding/hex"
	"flag"
	"io/ioutil"
	"log"
	"math/rand"
	"time"
)

func prepare(path string) []rune {
	raw, err := ioutil.ReadFile(path)
	if err != nil {
		log.Fatal(err)
	}

	rawhex := make([]byte, 0)
	for _, c := range raw {
		if (c >= 97 && c < 103) || (c >= 48 && c < 58) {
			rawhex = append(rawhex, c)
		}
	}

	result := make([]byte, hex.DecodedLen(len(rawhex)))
	_, err = hex.Decode(result, rawhex)

	if err != nil {
		log.Fatal(err)
	}

	resultRunes := make([]rune, len(result))
	for i := range result {
		resultRunes[i] = rune(result[i])
	}
	return resultRunes
}

func main() {
	log.SetFlags(0)
	rand.Seed(time.Now().UnixNano())

	ngramDir := flag.String("n", "ngrams", "Directory with ngrams")
	wordFreqsFilename := flag.String("w", "20k_wordlist.txt", "Path to top words")
	inputFname := flag.String("i", "", "Filename with cipher text")
	keyLen := flag.Int("s", 1, "Key length")
	flag.Parse()

	trainNgrams := ParseFrequencies(*ngramDir)
	wordFreqs := ParseTopWords(*wordFreqsFilename)
	ciphTextBytes, _ := ioutil.ReadFile(*inputFname)
	ciphText := []rune(string(ciphTextBytes))

	ga := NewPolyGA(ciphText, *keyLen, trainNgrams, wordFreqs)
	ga.Run()
}
