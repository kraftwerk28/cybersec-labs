use crate::{crypto, error::Error, models::*, utils::*};
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
            if creds.password.len() != 64 {
                Err(reject::custom(Error::InvalidHash))
            } else {
                Ok(row)
            }
        })
        .and_then(|row: Row| {
            let expected_hash: String = row.get(2);
            if crypto::verify(&expected_hash, &creds.password) {
                Ok(row)
            } else {
                Err(reject::custom(Error::Unauthorized))
            }
        })
        .and_then(|row: Row| {
            let rs = reply::with_status("", StatusCode::OK);
            let token = crypto::make_token();
            ctx.add_token(row.get(0), token.clone());
            let cookie = format!("token={}", token);
            let rs = reply::with_header(rs, "Set-Cookie", cookie);
            Ok(rs)
        })
}

pub async fn register(ctx: Ctx, creds: RegisterCreds) -> Result<impl Reply, Rejection> {
    if creds.password.len() != 64 {
        return Err(reject::custom(Error::InvalidHash));
    }

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

    let hash = crypto::hash(&creds.password, &ctx.argon_config);

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

pub async fn get_users(ctx: Ctx, user_id: UserID) -> Result<impl Reply, Rejection> {
    ctx.db
        .query("SELECT * FROM users", &[])
        .await
        .map(|rows| rows.iter().map(User::from).collect::<Vec<_>>())
        .map(|c| warp::reply::json(&c))
        .map_err(|_| warp::reject())
}

pub async fn register_phone(
    ctx: Ctx,
    user_id: UserID,
    data: PhoneReg,
) -> Result<impl Reply, Rejection> {
    let enc_phone = crypto::aead_encrypt(&data.phone);
    ctx.db
        .query(
            "UPDATE users SET phone_number = $1 WHERE user_id = $2",
            &[&enc_phone, &user_id],
        )
        .await
        .map(|_| reply::with_status("", StatusCode::CREATED))
        .map_err(|_| reject::custom(Error::DBErr))
}

pub async fn error(rej: Rejection) -> Result<impl Reply, Rejection> {
    if let Some(e) = rej.find::<Error>() {
        use Error::*;
        let code = match e {
            TooManyRequests(_) => StatusCode::TOO_MANY_REQUESTS,
            Unauthorized => StatusCode::UNAUTHORIZED,
            InvalidHash => StatusCode::BAD_REQUEST,
            _ => StatusCode::INTERNAL_SERVER_ERROR,
        };
        Ok(reply::with_status("", code))
    } else if rej.is_not_found() {
        Ok(reply::with_status("Not found", StatusCode::NOT_FOUND))
    } else {
        log::error!("{:?}", rej);
        Ok(reply::with_status("", StatusCode::INTERNAL_SERVER_ERROR))
    }
}
