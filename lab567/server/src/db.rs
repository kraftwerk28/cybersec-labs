use log::{error, info};
use std::{sync::Arc, time::Duration};
use tokio_postgres::{Client, Config, NoTls};

pub async fn connect() -> Arc<Client> {
    let (client, conn) = Config::new()
        .user(rtenv!("DBUSER"))
        .password(rtenv!("DBPASS"))
        .dbname(rtenv!("DBNAME"))
        .host(rtenv!("DBHOST" or "localhost"))
        .port(rtenv!("DBPORT" or "5432" as u16))
        .connect_timeout(Duration::from_secs(2))
        .connect(NoTls)
        .await
        .unwrap();

    tokio::spawn(async move {
        if let Err(err) = conn.await {
            error!("{:?}", err);
        } else {
            info!("Db connected");
        }
    });

    Arc::new(client)
}
