use crate::{crypto, models::User, ratelimiter::RateLimiter};
use log::{error, info};
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
    time::Duration,
};
use tokio_postgres::{Client, Config, NoTls, Row};

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

pub type UserID = i32;
type TokenStorage = Arc<Mutex<HashMap<String, UserID>>>;
#[derive(Clone)]
pub struct Ctx {
    pub db: Arc<Client>,
    pub public_path: String,
    pub rate_limiter: Arc<Mutex<RateLimiter>>,
    pub argon_config: argon2::Config<'static>,
    pub tokens: TokenStorage,
    pub aead_secred: String,
}

impl Ctx {
    pub fn new(
        public_path: String,
        db: Client,
        rate_limiter: RateLimiter,
    ) -> Self {
        let mut argon_config = argon2::Config::default();
        argon_config.variant = argon2::Variant::Argon2id;
        argon_config.thread_mode = argon2::ThreadMode::Sequential;

        Self {
            public_path,
            db: Arc::new(db),
            rate_limiter: Arc::new(Mutex::new(rate_limiter)),
            argon_config,
            tokens: TokenStorage::default(),
            aead_secred: rtenv!("AEAD_KEY" as String),
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

    pub fn decrypt_user(&self, row: &Row) -> User {
        let mut user = User::from(row);
        if let Some(num) = user.phone_number {
            user.phone_number = Some(crypto::aead_decrypt(&num));
        }
        user
    }
}
