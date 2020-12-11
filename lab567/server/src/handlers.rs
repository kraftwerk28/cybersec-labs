use crate::{error::Error, models::*, utils::*};
use log::error;
use warp::{
    http::{Error as HttpError, Response, StatusCode},
    reply::{self, Json, WithStatus},
    Rejection,
};

type R<T> = Result<T, warp::Rejection>;
type Rsp<T> = Result<T, HttpError>;

pub async fn login(ctx: Ctx, creds: LoginCreds) -> R<Rsp<Response<&'static str>>> {
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
}

pub async fn register(ctx: Ctx, creds: RegisterCreds) -> R<WithStatus<&'static str>> {
    ctx.db
        .execute(
            "INSERT INTO users (email, pwd_hash) VALUES ($1, $2)",
            &[&creds.email, &creds.password],
        )
        .await
        .map(|_| warp::reply::with_status("", StatusCode::CREATED))
        .map_err(|e| {
            error!("{:?}", e);
            warp::reject()
        })
}

pub async fn get_users(ctx: Ctx) -> R<Json> {
    ctx.db
        .query("SELECT * FROM users", &[])
        .await
        .map(|rows| rows.iter().map(User::from).collect::<Vec<_>>())
        .map(|c| warp::reply::json(&c))
        .map_err(|_| warp::reject())
}

pub async fn error(rej: Rejection) -> R<WithStatus<&'static str>> {
    log::error!("{:?}", rej);
    rej.find::<Error>()
        .map(|e| {
            let code = match e {
                Error::TooManyRequests(ip) => StatusCode::TOO_MANY_REQUESTS,
                Error::Unauthorized => StatusCode::UNAUTHORIZED,
            };
            reply::with_status("", code)
        })
        .ok_or(warp::reject())
    // if let Some(e) = rej.find::<Error>() {
    //     match e {

    //     }
    // } else {
    // }
}
