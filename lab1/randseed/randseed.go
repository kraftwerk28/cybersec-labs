package main

import (
	"fmt"
	"math/rand"
)

func main() {
	rand.Seed(0)
	for i := 0; i < 10; i++ {
		fmt.Println(rand.Int() % 1000)
	}
}
