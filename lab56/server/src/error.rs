use std::net::IpAddr;
use tokio_postgres::Error as PgError;

#[derive(Debug)]
pub enum Error {
    TooManyRequests(IpAddr),
    Unauthorized,
    DBErr(PgError),
    AlreadyExists,
    InvalidHash,
}

impl warp::reject::Reject for Error {}
