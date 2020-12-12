#[macro_use]
mod utils;
mod error;
mod handlers;
mod models;
mod ratelimiter;
mod routes;

use crate::{ratelimiter::RateLimiter, routes::root_route, utils::*};
use std::env;

#[tokio::main]
async fn main() {
    dotenv::dotenv().unwrap();
    pretty_env_logger::init();

    let db = utils::connect().await;
    let public_path = env::args().skip(1).next().unwrap();
    let rate_limiter = RateLimiter::from_env();
    let ctx = Ctx::new(public_path, db, rate_limiter);
    let root = root_route(ctx);

    warp::serve(root).run(([127, 0, 0, 1], 3000)).await
}
