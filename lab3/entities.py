import json
import dateutil.parser
from dataclasses import dataclass
from datetime import datetime, timedelta


class PlayMode:
    LCG = 'Lcg'
    MT = 'Mt'
    BETTER_MT = 'BetterMt'


@dataclass
class Account:
    id: int
    money: int
    deletion_time: datetime

    @staticmethod
    def recover():
        with open('account_dump.json', 'r') as f:
            return Account.parse(json.load(f))

    @staticmethod
    def parse(data):
        del_time = dateutil.parser.isoparse(data['deletionTime'])
        id = int(data['id'])
        return Account(id, data['money'], del_time)

    def get_creation_time(self) -> datetime:
        dt = timedelta(hours=1)
        return self.deletion_time - dt


@dataclass
class PlayResult:
    message: str
    account: Account
    real_number: int

    @staticmethod
    def parse(data):
        acc = Account.parse(data['account'])
        return PlayResult(data['message'], acc, data['realNumber'])
