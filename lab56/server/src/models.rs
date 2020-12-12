use serde::{Deserialize, Serialize};
use tokio_postgres::Row;

#[derive(Serialize, Deserialize)]
pub struct Count {
    pub count: u32,
}

#[derive(Serialize)]
pub struct User {
    user_id: i32,
    email: String,
    pwd_hash: String,
    phone_number: Option<String>,
}

#[derive(Serialize, Deserialize)]
pub struct RegisterCreds {
    pub email: String,
    pub password: String,
}

#[derive(Serialize, Deserialize)]
pub struct LoginCreds {
    pub email: String,
    pub password: String,
}

#[derive(Serialize, Deserialize)]
pub struct PhoneReg {
    pub phone: String,
}

impl std::convert::From<&Row> for User {
    fn from(row: &Row) -> Self {
        User {
            user_id: row.get(0),
            email: row.get(1),
            pwd_hash: row.get(2),
            phone_number: row.get(3),
        }
    }
}
