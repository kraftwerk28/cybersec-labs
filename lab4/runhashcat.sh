#!/usr/bin/env sh
wordlistdir="$HOME/wpa2-wordlists/Wordlists/Ultimate2016"

for hashfile in $(find ${2:-"hashes"}); do
  hashcat -m 110 -a 0 $hashfile $wordlistdir
done
