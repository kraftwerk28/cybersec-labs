use std::sync::Arc;
use tokio_postgres::Client;
use warp::http::{Error, Response, StatusCode};

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

#[derive(Clone)]
pub struct Ctx {
    pub db: Arc<Client>,
    pub public_path: String,
}

pub fn noauth401() -> Result<Response<&'static str>, Error> {
    Response::builder()
        .status(StatusCode::UNAUTHORIZED)
        .header("WWW-Authenticate", "Basic realm=")
        .body("")
}
