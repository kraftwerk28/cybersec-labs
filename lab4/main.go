package main

import (
	"crypto/md5"
	"crypto/sha1"
	"encoding/base64"
	"encoding/csv"
	"encoding/hex"
	"flag"
	"math/rand"
	"os"
	"path"
	"sync"
	"time"

	"github.com/cheggaaa/pb/v3"
	"golang.org/x/crypto/bcrypt"
)

var h16enc = hex.EncodeToString
var b64enc = base64.StdEncoding.EncodeToString

func genMD5(password string) []string {
	hash := md5.Sum([]byte(password))
	return []string{b64enc(hash[:])}
}

func genSHA1(password string) []string {
	salt := make([]byte, 16)
	rand.Read(salt)
	hash := sha1.Sum([]byte(password))
	return []string{b64enc(hash[:]), h16enc(salt)}
}

func genBcrypt(password string) []string {
	hash, err := bcrypt.GenerateFromPassword(
		[]byte(password[:]),
		bcrypt.DefaultCost,
	)
	if err != nil {
		panic(err)
	}
	return []string{string(hash)}
}

type getCSVRow func(string) []string

func genCSV(
	outpath string,
	count int,
	header []string,
	password2row func(string) []string,
) {
	fd, err := os.Create(outpath)
	defer fd.Close()
	if err != nil {
		panic(err)
	}
	csvf, pwdgen := csv.NewWriter(fd), NewPwdGen()
	genpass := pwdgen.Gen()
	csvf.Write(header)
	bar := pb.StartNew(count)

	wg, ch := sync.WaitGroup{}, make(chan []string)
	wg.Add(count)

	for i := 0; i < count; i++ {
		go func(ch chan<- []string) {
			defer wg.Done()
			password := genpass()
			row := password2row(password)
			ch <- row
		}(ch)
	}

	for i := 0; i < count; i++ {
		bar.Increment()
		csvf.Write(<-ch)
	}

	csvf.Flush()
	bar.Finish()
	wg.Wait()
}

func main() {
	rand.Seed(time.Now().UnixNano())
	outPath := flag.String("o", "out", "Output dir")
	count := flag.Int("c", 1000, "Count of hashes to generate")
	flag.Parse()

	if _, err := os.Stat(*outPath); os.IsNotExist(err) {
		os.Mkdir(*outPath, os.ModePerm)
	}

	wg := sync.WaitGroup{}
	wg.Add(1)

	go func(wg *sync.WaitGroup, outPath string, count int) {
		defer wg.Done()
		path := path.Join(outPath, "md5.csv")
		genCSV(path, count, []string{"hash"}, genMD5)
	}(&wg, *outPath, *count)

	go func(wg *sync.WaitGroup, outPath string, count int) {
		defer wg.Done()
		path := path.Join(outPath, "sha1.csv")
		genCSV(path, count, []string{"hash", "salt"}, genSHA1)
	}(&wg, *outPath, *count)

	go func(wg *sync.WaitGroup, outPath string, count int) {
		defer wg.Done()
		path := path.Join(outPath, "bcrypt.csv")
		genCSV(path, count, []string{"hash"}, genBcrypt)
	}(&wg, *outPath, *count)

	wg.Wait()
}
