# Human-like password generator

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
