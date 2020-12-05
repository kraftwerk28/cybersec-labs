import json
import requests as r
from entities import *

BASE = 'http://95.217.177.249/casino'


def create_account(player_id: int):
    url = f'{BASE}/createacc'
    params = {'id': player_id}
    res = r.get(url, params=params)
    with open('account_dump.json', 'w') as f:
        f.write(res.text)
    if res.status_code // 100 == 2:
        acc = Account.parse(res.json())
        print('New account:', acc)
        return acc


def play(mode: PlayMode, player_id: int, bet: int, number: int):
    url = f'{BASE}/play{mode}'
    params = {'id': player_id, 'bet': bet, 'number': number}
    res = r.get(url, params)
    if res.status_code // 100 == 2:
        return PlayResult.parse(res.json())
    else:
        print(res.json())
