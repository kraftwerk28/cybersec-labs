use std::net::IpAddr;

#[derive(Debug)]
pub enum Error {
    TooManyRequests(IpAddr),
    Unauthorized,
    DBErr,
    AlreadyExists,
}

impl warp::reject::Reject for Error {}