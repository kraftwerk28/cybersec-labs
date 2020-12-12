# Human-like password generator

## Part1
### Random passwords are generated in 4 ways:
1. By picking random password from list of 100k common passwords
2. By picking random password from list of top 100 common passwords
3. By generating absolutely random password with PRNG which consists of
  3.1 Uppercase ascii
  3.2 Lowercase ascii
  3.3 Punctuation
4. By generating human-like password using list of common words, characters
   from #3 and random digits. This is done by choosing type of part by weight
   and concatenating it to result, then trimming result to required length

In total, MD5, SHA1+salt and Bcrypt hashes were generated

## Part2
For cracking passwords, a wordlist [wpa2-wordlists](https://github.com/kennyn510/wpa2-wordlists)
was used.
1. With MD5 dictionary search, [these](crackedmd5.potfile) passwords are recovered.
2. With SHA1+salt dictionary search, [these](crackedsha1.potfile)
