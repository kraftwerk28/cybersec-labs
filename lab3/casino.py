import sys
import time
import json
import random

from datetime import datetime, timezone, timedelta
from dateutil import parser

from api import create_account, play
from entities import PlayMode, Account, PlayResult
from mtimpl import MT19937Gen
from mtcrack import MTCrack


M = (2 ** 32) // 2
ACC_LASTID = 1068


def try_createacc(last_id):
    if last_id is None:
        last_id = 0
    acc: Account = None
    while acc is None:
        acc = create_account(last_id)
        if acc is None:
            print(f'id {last_id} exists, skipping...')
        last_id += 1
    return acc


def solve_lcg(account_id: int) -> int:
    from sympy import mod_inverse
    # _last = (a * _last + c) % m; // m is 2^32
    inp = [play(PlayMode.LCG, account_id, 1, 42).real_number for _ in range(3)]
    print(inp)
    x1, x2, x3 = inp
    mi = mod_inverse(x2 - x1, M)
    a = ((x3 - x2) * mi) % M
    c = (x2 - x1 * a) % M
    print(f'a = {a}; c = {c}')
    return x3


def LCG_crack():
    acc = try_createacc(ACC_LASTID)
    account_id = acc.id
    a = 1664525
    c = 1013904223
    x = play(PlayMode.LCG, account_id, 1, 42).real_number

    def next():
        return (x * a + c) % M

    while acc.money <= 1000_000:
        x = next()
        print(f'Playing {x}')
        result = play(PlayMode.LCG, account_id, 900, x)
        print(result)
        acc = result.account


def MT_crack():
    acc = try_createacc(ACC_LASTID)

    # Here we don't recover because need to initialize seed
    account_id = acc.id

    dt = acc.get_creation_time() - datetime.fromtimestamp(0, timezone.utc)
    seed = int(dt.total_seconds())
    print(f'Seed: {seed}')

    local_rng = MT19937Gen(seed)

    while acc.money <= 1000_000:
        expected = local_rng.next()
        result: PlayResult = play(PlayMode.MT, account_id, 900, expected)
        print(result)
        acc = result.account


def MT_BETTER_crack():
    acc = try_createacc(ACC_LASTID)
    account_id = acc.id

    inputs = []
    for i in range(624):
        res = play(PlayMode.BETTER_MT, account_id, 1, 42)
        acc = res.account
        inputs.append(res.real_number)
        print(f'Playing {i + 1}/624; money left: {acc.money}...')

    cracked_rng = MTCrack(inputs).make_rng()

    while acc.money <= 1000_000:
        expected = cracked_rng.next()
        bet = acc.money - 1
        result: PlayResult = play(PlayMode.BETTER_MT,
                                  account_id, bet, expected)
        print(result)
        acc = result.account


if __name__ == '__main__':
    # NB: account time-to-live = 1 hour
    # And we calculate initial seed for MT_crack
    # by substracting 1h from deletion_time

    # LCG_crack()
    """
    Result:
    Yay! https://docs.google.com/document/d/1E_ltXUqvmmWeb3Dl3Qsyexsy5V7M6Lb1kvkXiXz9sks/edit?usp=sharing https://docs.google.com/document/d/1qsNXIqxQEs4Xbz5ye6z0ttrct1qn7zos4Vwl7PzcEK0/edit?usp=sharing
    """

    MT_crack()
    """
    Result
    Yay! It's different from the first one: https://docs.google.com/document/d/19vgZtvDN4_StEgVEM9MjfxnqfayByLNMD7PFJgvZv7c/edit?usp=sharing
    """

    MT_BETTER_crack()
    """
    Result:
    Yay!
    """
