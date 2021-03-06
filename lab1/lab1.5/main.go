package main

import (
	"encoding/hex"
	"flag"
	"io/ioutil"
	"log"
	"math/rand"
	_ "sort"
	"time"
)

var recentKeys = []string{
	//  "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"ZXKQJIDRTBMAGCFVLPNHWESYOU",
	"FGWJEQPTMONDUSZBAHYILVRXCK",
	"AGICSQWOLKEPJBVMTUNHDRZFYX",
	"KUECGPWZMXBAJSHFLTNYRVODIQ",
}

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

	// return []rune(string(result))
}

func main() {
	log.SetFlags(0)
	rand.Seed(time.Now().UnixNano())

	for _, ks := range recentKeys {
		key := FromString(ks)
		if !key.isValid() {
			log.Fatalf("Key %v isn't valid", ks)
		}
	}

	ngramDir := flag.String("n", "ngrams", "")
	inputFname := flag.String("i", "", "")
	keyLen := flag.Int("s", 1, "")
	flag.Parse()

	trainNgrams := ParseFreqs(*ngramDir)
	ciphTextBytes, _ := ioutil.ReadFile(*inputFname)
	ciphText := []rune(string(ciphTextBytes))

	// m := make(map[rune]bool)
	// for i := range ciphText {
	// 	m[ciphText[i]] = true
	// }
	// sl := make([]rune, 0, len(m))
	// for i := range m {
	// 	sl = append(sl, i)
	// }
	// sort.Slice(sl, func(i, j int) bool { return sl[i] < sl[j] })
	// log.Println(sl, len(sl))

	// ga := NewPolyGA(ciphText, 1, trainNgrams)
	ga := NewPolyGA(ciphText, *keyLen, trainNgrams)
	// ga := NewPolyGAwKeys(ciphText5, recentKeys)
	ga.Run()
}
