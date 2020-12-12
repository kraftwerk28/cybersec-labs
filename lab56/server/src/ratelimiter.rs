use std::{
    cmp::Eq,
    collections::HashMap,
    hash::Hash,
    net::IpAddr,
    sync::{Arc, Mutex},
    time::Duration,
};
use tokio::{task::JoinHandle, time::delay_for};

#[derive(Hash, Eq, PartialEq, Debug, Clone)]
pub enum Record {
    Email(String),
    Ip(IpAddr),
}

type Records = Arc<Mutex<HashMap<Record, usize>>>;

pub struct RateLimiter {
    records: Records,
    rate_limit: usize,
    #[allow(dead_code)]
    tick_handle: JoinHandle<()>,
}

impl RateLimiter {
    pub fn from_env() -> Self {
        let rate_limit = rtenv!("RATELIMIT" or "5" as usize);
        let time_frame =
            Duration::from_secs(rtenv!("RL_TIMEFRAME" or "60" as u64));
        Self::new(rate_limit, time_frame)
    }

    pub fn new(rate_limit: usize, tick_duration: Duration) -> Self {
        let records = Records::default();
        let tick_handle = tokio::spawn({
            let records = records.clone();
            async move {
                loop {
                    delay_for(tick_duration).await;
                    let mut lck = records.lock().unwrap();
                    lck.retain(|_, c| {
                        *c -= 1;
                        *c > 0
                    });
                }
            }
        });
        RateLimiter {
            records,
            rate_limit,
            tick_handle,
        }
    }

    fn check_record(&mut self, rec: Record) -> bool {
        let mut lck = self.records.lock().unwrap();
        let counter = lck.entry(rec.clone()).or_insert(0);
        if *counter < self.rate_limit {
            *counter += 1;
        }
        log::info!("{:?}: {}", rec, *counter);
        *counter >= self.rate_limit
    }

    pub fn check_ip(&mut self, addr: IpAddr) -> bool {
        let rec = Record::Ip(addr);
        self.check_record(rec)
    }

    pub fn check_email(&mut self, email: String) -> bool {
        let rec = Record::Email(email);
        self.check_record(rec)
    }
}
