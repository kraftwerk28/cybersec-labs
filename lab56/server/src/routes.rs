use crate::{error::Error, handlers, utils::Ctx, utils::UserID};
use std::{convert::Infallible, net::SocketAddr};
use warp::{http::StatusCode, reject, reply, Filter, Rejection, Reply};

/// Example
fn with_ctx(ctx: Ctx) -> rpl!((Ctx,), Infallible) {
    warp::any().map(move || ctx.clone())
}

#[allow(dead_code)]
fn login_nocreds() -> rpl!() {
    warp::path("login").map(|| reply::with_status("", StatusCode::UNAUTHORIZED))
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

fn check_auth(ctx: Ctx) -> rpl!((UserID,)) {
    warp::cookie("token")
        .and(with_ctx(ctx))
        .and_then(|cookie: String, mut ctx: Ctx| async move {
            if let Some(user_id) = ctx.check_token(cookie) {
                Ok(user_id)
            } else {
                Err(reject::custom(Error::Unauthorized))
            }
        })
}

pub fn login(ctx: Ctx) -> rpl!() {
    warp::path("login")
        .and(with_ctx(ctx.clone()))
        .and(rate_limit(ctx))
        .and(warp::post())
        .and(warp::body::json())
        .and_then(handlers::login)
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
        .and(with_ctx(ctx.clone()))
        .and(check_auth(ctx))
        .and_then(handlers::get_users)
}

pub fn register_phone(ctx: Ctx) -> rpl!() {
    warp::path("add_phone")
        .and(with_ctx(ctx.clone()))
        .and(check_auth(ctx))
        .and(warp::post())
        .and(warp::body::json())
        .and_then(handlers::register_phone)
}

pub fn static_srv(ctx: Ctx) -> rpl!() {
    warp::get().and(warp::fs::dir(ctx.public_path))
}

pub fn root_route(ctx: Ctx) -> rpl!() {
    get_users(ctx.clone())
        .or(login(ctx.clone()))
        .or(register(ctx.clone()))
        .or(register_phone(ctx.clone()))
        .or(static_srv(ctx.clone()))
        .recover(handlers::error)
}
