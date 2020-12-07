use crate::{
    models::*,
    utils::{noauth401, Ctx},
};
use log::error;
use std::convert::Infallible;
use warp::{
    http::{Response, StatusCode},
    reject, Filter, Rejection, Reply,
};

macro_rules! Rpl {
    () => (Rpl!(impl Reply));
    ($t:ty) => (Rpl!($t, Rejection));
    ($ex:ty, $er: ty) => (impl Filter<Extract = $ex, Error = $er> + Clone);
}

/// Example
fn with_ctx(ctx: Ctx) -> Rpl!((Ctx,), Infallible) {
    warp::any().map(move || ctx.clone())
}

fn login_nocreds() -> Rpl!() {
    warp::path("login").map(|| noauth401())
}

pub fn login(ctx: Ctx) -> Rpl!() {
    warp::path("login")
        .and(with_ctx(ctx))
        .and(warp::post())
        .and(warp::body::json())
        .and_then(|ctx: Ctx, creds: LoginCreds| async move {
            ctx.db
                .query(
                    "SELECT * FROM USERS WHERE email = $1 AND pwd_hash = $2",
                    &[&creds.email, &creds.password],
                )
                .await
                .map(|rows| {
                    if rows.is_empty() {
                        noauth401()
                    } else {
                        Response::builder()
                            .status(StatusCode::OK)
                            .body("Authorized")
                    }
                })
                .map_err(|_| warp::reject())
        })
}

pub fn register(ctx: Ctx) -> Rpl!() {
    warp::path("register")
        .and(with_ctx(ctx))
        .and(warp::post())
        .and(warp::body::json())
        .and_then(|ctx: Ctx, creds: RegisterCreds| async move {
            ctx.db
                .execute(
                    "INSERT INTO users (email, pwd_hash) VALUES ($1, $2)",
                    &[&creds.email, &creds.password],
                )
                .await
                .map_err(|e| {
                    error!("{:?}", e);
                    reject::reject()
                })
                .map(|_| warp::reply::with_status("", StatusCode::NO_CONTENT))
        })
}

pub fn get_users(ctx: Ctx) -> Rpl!() {
    warp::path("users").and(with_ctx(ctx)).and_then(
        move |ctx: Ctx| async move {
            ctx.db
                .query("SELECT * FROM users", &[])
                .await
                .map(|rows| rows.iter().map(User::from).collect::<Vec<_>>())
                .map(|c| warp::reply::json(&c))
                .map_err(|_| reject::reject())
        },
    )
}

pub fn static_srv(ctx: Ctx) -> Rpl!() {
    warp::get().and(warp::fs::dir(ctx.public_path))
}

pub fn root_route(ctx: Ctx) -> Rpl!() {
    get_users(ctx.clone())
        .or(login(ctx.clone()))
        .or(login_nocreds())
        .or(register(ctx.clone()))
        .or(static_srv(ctx.clone()))
}
