use aes_gcm::{
    aead::{generic_array::GenericArray, Aead, NewAead},
    Aes256Gcm,
};
use rand::{thread_rng, Rng};

pub fn hash(password: &str, config: &argon2::Config) -> String {
    let salt = thread_rng().gen::<[u8; 16]>();
    argon2::hash_encoded(password.as_bytes(), &salt, config).unwrap()
}

pub fn verify(hash: &str, password: &str) -> bool {
    argon2::verify_encoded(hash, password.as_bytes()).unwrap()
}

pub fn make_token() -> String {
    let raw = thread_rng().gen::<[u8; 16]>();
    base64::encode(raw)
}

fn create_cipher() -> Aes256Gcm {
    let env_key = rtenv!("AEAD_KEY" as String);
    let key = GenericArray::from_slice(env_key.as_bytes());
    Aes256Gcm::new(key)
}

pub fn aead_encrypt(data: &str) -> String {
    let salt = thread_rng().gen::<[u8; 16]>();
    let nonce = GenericArray::from_slice(&salt);

    let aes = create_cipher();
    let mut enc = aes
        .encrypt(nonce, data.as_bytes())
        .expect("Failed to encrypt");
    enc.extend(&salt);
    base64::encode(enc)
}

pub fn aead_decrypt(data: &str) -> String {
    let raw = base64::decode(data).expect("Failed to decode data");
    let (body, salt) = raw.split_at(raw.len() - 16);
    dbg!(salt.len());
    let nonce = GenericArray::from_slice(&salt);
    let aes = create_cipher();

    let enc = aes.decrypt(nonce, body).unwrap();
    String::from_utf8(enc).unwrap().to_string()
}

#[test]
fn check_aead() {
    let data = "Hello, world";
    let enc = aead_encrypt(data);
    println!("input: {}; encrypted: {}", data, enc);
    let dec = aead_decrypt(&enc);
    println!("decrypted: {}", dec);
    assert_eq!(data, dec);
}
