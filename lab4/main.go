package main

import (
	"bufio"
	"crypto/md5"
	"crypto/sha1"
	"encoding/base64"
	"encoding/csv"
	"encoding/hex"
	"flag"
	"fmt"
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
	hash := sha1.Sum([]byte(password + hex.EncodeToString(salt)))
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
	progresschan chan<- struct{},
) {
	fd, err := os.Create(outpath)
	defer fd.Close()
	if err != nil {
		panic(err)
	}
	csvf, pwdgen := csv.NewWriter(fd), NewPwdGen()
	genpass := pwdgen.Gen()
	csvf.Write(header)

	wg, ch := sync.WaitGroup{}, make(chan []string)
	wg.Add(count)

	for i := 0; i < count; i++ {
		go func(ch chan<- []string) {
			defer wg.Done()
			password := genpass()
			row := password2row(password)
			ch <- row
			progresschan <- struct{}{}
		}(ch)
	}

	for i := 0; i < count; i++ {
		csvf.Write(<-ch)
	}

	csvf.Flush()
	wg.Wait()
}

func genHumanLike(
	outpath string,
	count int,
	progresschan chan<- struct{},
) {
	fd, err := os.Create(outpath)
	defer fd.Close()
	if err != nil {
		panic(err)
	}
	sc, gen := bufio.NewWriter(fd), NewPwdGen()
	for i := 0; i < count; i++ {
		password := gen.humanlike()
		fmt.Fprintln(sc, password)
		progresschan <- struct{}{}
	}
	sc.Flush()
}

func main() {
	rand.Seed(time.Now().UnixNano())
	floutPath := flag.String("o", "out", "Output dir")
	flcount := flag.Int("c", 1000, "Count of hashes to generate")
	flgenWords := flag.Bool("p", false, "Generate list of human-like passwords")
	flag.Parse()

	count, outPath := *flcount, *floutPath
	procCount := 1

	if _, err := os.Stat(outPath); os.IsNotExist(err) && !*flgenWords {
		os.Mkdir(outPath, os.ModePerm)
	}
	wg, progresschan := sync.WaitGroup{}, make(chan struct{})

	if *flgenWords {
		procCount = 1
		wg.Add(procCount)
		go func() {
			defer wg.Done()
			genHumanLike(outPath, count, progresschan)
		}()
	} else {
		wg.Add(procCount)

		go func(outPath string, count int) {
			defer wg.Done()
			path := path.Join(outPath, "md5.csv")
			genCSV(path, count, []string{"hash"}, genMD5, progresschan)
		}(outPath, count)

		go func(outPath string, count int) {
			defer wg.Done()
			path := path.Join(outPath, "sha1.csv")
			genCSV(path, count, []string{"hash", "salt"}, genSHA1, progresschan)
		}(outPath, count)

		go func(wg *sync.WaitGroup, outPath string, count int) {
			defer wg.Done()
			path := path.Join(outPath, "bcrypt.csv")
			genCSV(path, count, []string{"hash"}, genBcrypt, progresschan)
		}(&wg, outPath, count)
	}

	totalCount := procCount * count
	bar := pb.StartNew(totalCount)
	go func() {
		for range progresschan {
			bar.Increment()
		}
	}()

	wg.Wait()
	close(progresschan)
	bar.Finish()
}
