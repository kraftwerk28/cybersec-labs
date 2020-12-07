#[macro_use]
mod utils;
mod db;
mod models;
mod routes;

#[tokio::main]
async fn main() {
    dotenv::dotenv().unwrap();
    pretty_env_logger::init();
    let db = db::connect().await;
    let public_path = std::env::args().skip(1).next().unwrap();
    let ctx = utils::Ctx { public_path, db };
    let root = routes::root_route(ctx);

    warp::serve(root).run(([127, 0, 0, 1], 3000)).await
}
