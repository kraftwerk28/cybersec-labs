use crypto::{
    aead::{AeadDecryptor, AeadEncryptor},
    aes::KeySize,
    aes_gcm::AesGcm,
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

pub fn aead_encrypt(data: &str) -> String {
    let dummy_aad = vec![0x42; 16];
    let nonce = thread_rng().gen::<[u8; 12]>();
    let env_key = rtenv!("AEAD_KEY" as String);
    let mut aes = AesGcm::new(KeySize::KeySize128, env_key.as_bytes(), &nonce, &dummy_aad);
    let mut tag = vec![0; 16];
    let mut result_raw = vec![0; data.len()];
    aes.encrypt(data.as_bytes(), &mut result_raw, &mut tag);
    result_raw.extend(&nonce);
    result_raw.extend(tag);
    base64::encode(result_raw)
}

pub fn aead_decrypt(data: &str) -> String {
    let dummy_aad = vec![0x42; 16];
    let raw_data = base64::decode(data).unwrap();
    let (body, tag) = raw_data.split_at(raw_data.len() - 16);
    let (body, nonce) = body.split_at(body.len() - 12);
    let env_key = rtenv!("AEAD_KEY" as String);
    let mut aes = AesGcm::new(KeySize::KeySize128, env_key.as_bytes(), &nonce, &dummy_aad);
    let mut result_raw = vec![0; body.len()];
    aes.decrypt(&body, &mut result_raw, &tag);
    String::from_utf8(result_raw).unwrap()
}

#[cfg(test)]
mod test {
    #[test]
    fn check_aead() {
        use crate::crypto::*;
        let data = "Hello, world";
        let enc = aead_encrypt(data);
        println!("input: {}; encrypted: {}", data, enc);
        let dec = aead_decrypt(&enc);
        println!("decrypted: {}", dec);
        // assert_eq!(data.len(), dec.len());
        assert_eq!(data, dec);
    }
}
