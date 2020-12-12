use crate::{error::Error, models::*, utils::*};
use log::error;
use tokio_postgres::Row;
use warp::{http::StatusCode, reject, reply, Rejection, Reply};

pub async fn login(mut ctx: Ctx, creds: LoginCreds) -> Result<impl Reply, Rejection> {
    ctx.db
        .query_one(
            "SELECT * FROM USERS WHERE email = $1 LIMIT 1",
            &[&creds.email],
        )
        .await
        .map_err(|_| reject::custom(Error::Unauthorized))
        .and_then(|row: Row| {
            let expected_hash: String = row.get(2);
            if verify(&expected_hash, &creds.password) {
                Ok(row)
            } else {
                Err(reject::custom(Error::Unauthorized))
            }
        })
        .and_then(|row: Row| {
            let rs = reply::with_status("", StatusCode::OK);
            let token = make_token();
            ctx.add_token(row.get(0), token.clone());
            let cookie = format!("token={}", token);
            let rs = reply::with_header(rs, "Set-Cookie", cookie);
            Ok(rs)
        })
}

pub async fn register(ctx: Ctx, creds: RegisterCreds) -> Result<impl Reply, Rejection> {
    let exists = ctx
        .db
        .query(
            "SELECT count(*) FROM users WHERE email = $1",
            &[&creds.email],
        )
        .await
        .map(|rows| rows.is_empty())
        .unwrap_or(false);

    if exists {
        return Err(reject::custom(Error::AlreadyExists));
    }

    let hash = hash(&creds.password, &ctx.argon_config);
    ctx.db
        .execute(
            "INSERT INTO users (email, pwd_hash) VALUES ($1, $2)",
            &[&creds.email, &hash],
        )
        .await
        .map(|_| warp::reply::with_status("", StatusCode::CREATED))
        .map_err(|e| {
            error!("{:?}", e);
            reject::custom(Error::DBErr)
        })
}

pub async fn get_users(ctx: Ctx) -> Result<impl Reply, Rejection> {
    ctx.db
        .query("SELECT * FROM users", &[])
        .await
        .map(|rows| rows.iter().map(User::from).collect::<Vec<_>>())
        .map(|c| warp::reply::json(&c))
        .map_err(|_| warp::reject())
}

pub async fn error(rej: Rejection) -> Result<impl Reply, Rejection> {
    log::error!("{:?}", rej);
    rej.find::<Error>()
        .map(|e| {
            let code = match e {
                Error::TooManyRequests(_) => StatusCode::TOO_MANY_REQUESTS,
                Error::Unauthorized => StatusCode::UNAUTHORIZED,
                _ => StatusCode::SERVICE_UNAVAILABLE,
            };
            reply::with_status("", code)
        })
        .ok_or(warp::reject())
}
