# Password storage. Hashing. Sensitive information storage. TLS

In this lab, server is written in Rust,
client is written in Svelte

For preventing long payloads given to hash function, the password is prehashed
with sha256

The request body is also limited

For password storage, argon2 is used (Argon2id variant)

For preventing the brute-force attacks, rate limiting is implemented. It is a
simple HashMap with users emails and IP addresses, which is cleaned up
through time

