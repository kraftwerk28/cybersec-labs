#!/usr/bin/env python
import sys
from lab1.utils import railfence_decode

if __name__ == '__main__':
    print()
    print(railfence_decode(sys.stdin.read().strip(), 4))
