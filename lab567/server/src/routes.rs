use crate::{
    error::Error,
    handlers,
    utils::{noauth401, Ctx},
};
use std::{convert::Infallible, net::SocketAddr};
use warp::{reject, Filter, Rejection, Reply};

/// Example
fn with_ctx(ctx: Ctx) -> rpl!((Ctx,), Infallible) {
    warp::any().map(move || ctx.clone())
}

fn login_nocreds() -> rpl!() {
    warp::path("login").map(|| noauth401())
}

fn rate_limit(ctx: Ctx) -> rpl!(()) {
    warp::any()
        .and(with_ctx(ctx))
        .and(warp::addr::remote())
        .and_then(|ctx: Ctx, ip: Option<SocketAddr>| async move {
            let mut rl = ctx.rate_limiter.lock().unwrap();
            match ip {
                Some(addr) => {
                    if rl.check_ip(addr.ip()) {
                        let e = Error::TooManyRequests(addr.ip());
                        Err(reject::custom(e))
                    } else {
                        Ok(())
                    }
                }
                _ => Ok(()),
            }
        })
        .untuple_one()
}

pub fn login(ctx: Ctx) -> rpl!() {
    warp::path("login")
        .and(with_ctx(ctx.clone()))
        .and(rate_limit(ctx))
        .and(warp::post())
        .and(warp::body::json())
        .and_then(handlers::login)
        .recover(handlers::error)
}

pub fn register(ctx: Ctx) -> rpl!() {
    warp::path("register")
        .and(with_ctx(ctx))
        .and(warp::post())
        .and(warp::body::json())
        .and_then(handlers::register)
}

pub fn get_users(ctx: Ctx) -> rpl!() {
    warp::path("users")
        .and(with_ctx(ctx))
        .and_then(handlers::get_users)
}

pub fn static_srv(ctx: Ctx) -> rpl!() {
    warp::get().and(warp::fs::dir(ctx.public_path))
}

pub fn root_route(ctx: Ctx) -> rpl!() {
    get_users(ctx.clone())
        .or(login(ctx.clone()))
        .or(login_nocreds())
        .or(register(ctx.clone()))
        .or(static_srv(ctx.clone()))
}
