package main

import (
	"log"
	"math/rand"
	"time"
)

var recentKeys = []string{

	// "ZKEQJDGSTLPAVCFLMNHYWUXROI",
	// "FGLPEQOTMVJDBSZHAIYWRUXKCN",
	// "LOICSQWMNFKJPBAZTUVHDXGEYR",
	// "KJDTGOWZMVXAFSHPBENYRUIQCL",

//  "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
	"ZXKQJIDRTBMAGCFVLPNHWESYOU",
	"FGWJEQPTMONDUSZBAHYILVRXCK",
	"AGICSQWOLKEPJBVMTUNHDRZFYX",
	"KUECGPWZMXBAJSHFLTNYRVODIQ",
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

	ind := FromStrKeys(recentKeys)
	dec := ind.decode([]rune(ciphText5))
	log.Println(string(dec))

	// ga := NewPolyGA(ciphText4, 1)
	// ga := NewPolyGA(ciphText5, 4)
	// ga := NewPolyGAwKeys(ciphText5, recentKeys)
	// ga.Run()
}
