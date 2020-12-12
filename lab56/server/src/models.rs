use serde::{Deserialize, Serialize};
use tokio_postgres::Row;

#[derive(Serialize, Deserialize)]
pub struct Count {
    pub count: u32,
}

#[derive(Serialize)]
pub struct Customer {
    customer_id: i32,
    first_name: String,
    last_name: String,
    email: Option<String>,
}

#[derive(Serialize)]
pub struct User {
    user_id: i32,
    email: String,
    pwd_hash: String,
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

impl std::convert::From<&Row> for Customer {
    fn from(row: &Row) -> Self {
        Customer {
            customer_id: row.get(0),
            first_name: row.get(1),
            last_name: row.get(2),
            email: row.get(3),
        }
    }
}

impl std::convert::From<&Row> for User {
    fn from(row: &Row) -> Self {
        User {
            user_id: row.get(0),
            email: row.get(1),
            pwd_hash: row.get(2),
        }
    }
}
