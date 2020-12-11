use std::time::Duration;

use ratelimiter::RateLimiter;

#[macro_use]
mod utils;
mod error;
mod handlers;
mod models;
mod ratelimiter;
mod routes;

#[tokio::main]
async fn main() {
    dotenv::dotenv().unwrap();
    pretty_env_logger::init();
    let db = utils::connect().await;
    let public_path = std::env::args().skip(1).next().unwrap();
    let rate_limiter = RateLimiter::from_env();
    let ctx = utils::Ctx::new(public_path, db, rate_limiter);
    let root = routes::root_route(ctx);
    warp::serve(root).run(([127, 0, 0, 1], 3000)).await
}
