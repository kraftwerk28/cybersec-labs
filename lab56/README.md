# Password storage. Hashing. Sensitive information storage. TLS

In this lab, server is written in Rust,
client is written in Svelte

For preventing long payloads given to hash function, the password is prehashed
with sha3 on __client__ using `js-sha3` library.

For password storage, argon2 is used (Argon2id variant) with 1 lane (sequential)

For preventing the brute-force attacks, rate limiting is implemented. It is a
simple HashMap with users emails & IP addresses and counters. Counters are
decremented with a timer and if counter reaches specific number, client
starts receiving 429 code.

For sensitive storage, AES 
