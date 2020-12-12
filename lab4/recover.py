#!/usr/bin/env python
import sys
import os
import csv
import base64
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('--out', '-o', type=str, default='hashes')
ap.add_argument('--limit', '-l', type=int, default=100)
args = ap.parse_args()

if not os.path.isdir(args.out):
    os.mkdir(args.out)
with open('out/sha1.csv') as csvfile:
# with open('out/sha1.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader)
    lim = 1
    for row in csvreader:
        if lim > args.limit:
            break
        with open(f'{args.out}/{lim}.hash', 'w') as hashfile:
            hex = base64.b64decode(row[0]).hex()
            hashfile.writelines([hex + ':' + row[1]])
        lim += 1
