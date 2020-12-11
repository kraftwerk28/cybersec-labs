use crate::ratelimiter::RateLimiter;
use log::{error, info};
use std::{
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

#[derive(Clone)]
pub struct Ctx {
    pub db: Arc<Client>,
    pub public_path: String,
    pub rate_limiter: Arc<Mutex<RateLimiter>>,
}

impl Ctx {
    pub fn new(public_path: String, db: Client, rate_limiter: RateLimiter) -> Self {
        Self {
            public_path,
            db: Arc::new(db),
            rate_limiter: Arc::new(Mutex::new(rate_limiter)),
        }
    }
}

pub fn noauth401() -> Result<Response<&'static str>, Error> {
    Response::builder()
        .status(StatusCode::UNAUTHORIZED)
        .header("WWW-Authenticate", "Basic realm=")
        .body("")
}
