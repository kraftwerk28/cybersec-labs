use crate::ratelimiter::RateLimiter;
use log::{error, info};
use rand::{thread_rng, Rng};
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
    time::Duration,
};
use tokio_postgres::{Client, Config, NoTls};
use warp::http::{Error, Response, StatusCode};

macro_rules! rpl {
    () => (rpl!(impl Reply));
    ($t:ty) => (rpl!($t, Rejection));
    ($ex:ty, $er: ty) => (impl Filter<Extract = $ex, Error = $er> + Clone);
}

macro_rules! rtenv {
    ($name:literal) => {
        ::std::env::var($name)
            .expect(format!("Env variable {} is not set", $name).as_str())
            .as_str()
    };
    ($name:literal as $t:ty) => {
        ::std::env::var($name)
            .expect(format!("Env variable {} is not set", $name).as_str())
            .parse::<$t>()
            .unwrap()
    };
    ($name:literal or $fb:literal) => {
        ::std::env::var($name).unwrap_or($fb.to_string()).as_str()
    };
    ($name:literal or $fb:literal as $t:ty) => {
        ::std::env::var($name)
            .unwrap_or($fb.to_string())
            .parse::<$t>()
            .unwrap()
    };
}

pub async fn connect() -> Client {
    let (client, conn) = Config::new()
        .user(rtenv!("DBUSER"))
        .password(rtenv!("DBPASS"))
        .dbname(rtenv!("DBNAME"))
        .host(rtenv!("DBHOST" or "localhost"))
        .port(rtenv!("DBPORT" or "5432" as u16))
        .connect_timeout(Duration::from_secs(2))
        .connect(NoTls)
        .await
        .unwrap();

    tokio::spawn(async move {
        if let Err(err) = conn.await {
            error!("{:?}", err);
        } else {
            info!("Db connected");
        }
    });

    client
}

type UserID = i32;
type TokenStorage = Arc<Mutex<HashMap<String, UserID>>>;
#[derive(Clone)]
pub struct Ctx {
    pub db: Arc<Client>,
    pub public_path: String,
    pub rate_limiter: Arc<Mutex<RateLimiter>>,
    pub argon_config: argon2::Config<'static>,
    pub tokens: TokenStorage,
}

impl Ctx {
    pub fn new(public_path: String, db: Client, rate_limiter: RateLimiter) -> Self {
        let mut argon_config = argon2::Config::default();
        argon_config.variant = argon2::Variant::Argon2id;
        Self {
            public_path,
            db: Arc::new(db),
            rate_limiter: Arc::new(Mutex::new(rate_limiter)),
            argon_config,
            tokens: TokenStorage::default(),
        }
    }

    pub fn add_token(&mut self, user_id: i32, token: String) {
        let mut lck = self.tokens.lock().unwrap();
        lck.insert(token, user_id);
    }

    pub fn check_token(&mut self, token: String) -> Option<UserID> {
        let lck = self.tokens.lock().unwrap();
        lck.get(&token).map(|u| *u)
    }
}

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
