use std::net::IpAddr;

#[derive(Debug)]
pub enum Error {
    TooManyRequests(IpAddr),
    Unauthorized,
    DBErr,
    AlreadyExists,
    InvalidHash
}

impl warp::reject::Reject for Error {}
