package main

import (
	"bufio"
	"math/rand"
	"os"
	"path"
	"strings"

	"github.com/mroth/weightedrand"
)

const (
	common100kpass = "common100Kpass.txt"
	common110pass  = "common100Kpass.txt"
	commonWords    = "common_words.txt"
	dataDir        = "data"
	asciiUppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	asciiLowercase = "abcdefghijklmnopqrstuvwxyz"
	punctuation    = "!\"#$%&\\'()*+,-./:;<=>?@[\\]^_`{|}~"
)

type PwdGen struct {
	randPwdCharset      []rune
	common100kPasswords []string
	common110Passwords  []string
	commonWords         []string
}

func NewPwdGen() PwdGen {
	return PwdGen{
		randPwdCharset:      []rune(asciiLowercase + asciiUppercase + punctuation),
		common100kPasswords: readFromFile(path.Join(dataDir, common100kpass)),
		common110Passwords:  readFromFile(path.Join(dataDir, common110pass)),
		commonWords:         readFromFile(path.Join(dataDir, commonWords)),
	}
}

func readFromFile(path string) []string {
	ret := make([]string, 0)
	fd, err := os.Open(path)
	defer fd.Close()
	if err != nil {
		panic(err)
	}
	sc := bufio.NewScanner(fd)

	for sc.Scan() {
		ret = append(ret, sc.Text())
	}
	return ret
}

func (pwdgen *PwdGen) randPassword() string {
	length := rand.Intn(6) + 10
	ret := make([]rune, length)
	for i := range ret {
		idx := rand.Intn(len(pwdgen.randPwdCharset))
		ret[i] = pwdgen.randPwdCharset[idx]
	}
	return string(ret)
}

func randWord(list []string) string {
	idx := rand.Intn(len(list))
	word := list[idx]
	if rand.Float64() < 0.35 {
		word = strings.Title(word)
	}
	return word
}

func (pwdgen *PwdGen) humanlike() string {
	pwdlen := rand.Intn(4) + 16
	result := make([]rune, 0)
	for {
		chrTypeIdx := rand.Float64()
		var wordPart string
		if chrTypeIdx < 0.65 {
			wordPart = randWord(pwdgen.commonWords)
		} else if chrTypeIdx < 0.9 {
			wordPart = string(rune(rand.Intn(10) + 48))
		} else {
			idx := rand.Intn(len(pwdgen.randPwdCharset))
			wordPart = string(pwdgen.randPwdCharset[idx])
		}
		if len(wordPart)+len(result) > pwdlen {
			break
		}
		result = append(result, []rune(wordPart)...)
	}
	return string(result)
}

func (pwdgen *PwdGen) Gen() func() string {
	get100k := func() string {
		l := len(pwdgen.common100kPasswords)
		return pwdgen.common100kPasswords[rand.Intn(l)]
	}
	get110 := func() string {
		l := len(pwdgen.common110Passwords)
		return pwdgen.common110Passwords[rand.Intn(l)]
	}
	wr, err := weightedrand.NewChooser(
		weightedrand.NewChoice(get100k, 75),
		weightedrand.NewChoice(get110, 700),
		weightedrand.NewChoice(pwdgen.randPassword, 30),
		weightedrand.NewChoice(pwdgen.humanlike, 195),
	)
	if err != nil {
		panic(err)
	}

	return func() string {
		return wr.Pick().(func() string)()
	}
}
