use std::net::IpAddr;

#[derive(Debug)]
pub enum Error {
    TooManyRequests(IpAddr),
    Unauthorized,
}

impl warp::reject::Reject for Error {}
