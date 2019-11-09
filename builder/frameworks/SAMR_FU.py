##########################################################################
#
#   WizIO 2020 Georgi Angelov
#       http://www.wizio.eu/
#       https://github.com/Wiz-IO/platform-sam-lora
# 
##########################################################################
# 
# Microchip Atmel SAMR3x Flash Utility ver 1.00 PlatformIO
#
#   Copyright (C) 2019 Georgi Angelov. All rights reserved.
#   Author: Georgi Angelov <the.wizarda@gmail.com> WizIO
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name WizIO nor the names of its contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
############################################################################
# Dependency:
#      pyserial
############################################################################

from __future__ import print_function
import os, sys, struct, time
import os.path
from os.path import join
from serial import Serial
from binascii import hexlify
import inspect
############################################################################
PYTHON2 = sys.version_info[0] < 3  # True if on pre-Python 3

if PYTHON2:
    pass
else:
    def xrange(*args, **kwargs):
        return iter( range(*args, **kwargs) )
############################################################################

DEBUG = False

BLOCK_SIZE  = 64
PAGE_SIZE   = 256

ATTN        = b'#'
CONF        = b'C'

PING        = b'P'
PONG        = b'p'

ACK         = b'A'
NACK        = b'N'

DA_ERASE    = b'E'
DA_WRITE    = b'W'
DA_READ     = b'R'
DA_RESET    = b'x'

if sys.version_info >= (3, 0):
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

def ERROR(message):
    time.sleep(0.1)
    print("\n\033[31mERROR: {}\n\r".format(message))
    exit(2)

def ASSERT(flag, message):
    if flag == False:
        ERROR(message)

def PB_BEGIN():
    if DEBUG == False:
        sys.stdout.write('\033[94m<')

def PB_STEP():
    if DEBUG == False:
        sys.stdout.write('.')    

def PB_END():
    if DEBUG == False:
        sys.stdout.write("> DONE\n")

def HEX(s):
    return hexlify(s).decode("ascii").upper()

def checksum(data, c = 0): 
    for i in range( len(data) ): 
        if PYTHON2:
            c += ord( data[i] ) #py2
        else:
            c += data[i]        #py3
    return c

class SAMR:
    def __init__(self, ser):
        self.s = ser
        self.dir = os.path.dirname( os.path.realpath(__file__) )    

    def da_erase_block(self, addr):
        crc = checksum( struct.pack("I", addr) )
        self.s.write(ATTN + DA_ERASE + struct.pack("IH", addr, crc & 0xFFFF))
        r = self.s.read(2)
        ASSERT( CONF+CONF == r, "[{}] erase block[256]: {}".format(r, hex(addr)))

    def da_write_block(self, addr, data = 64 * b'\xFF'):
        crc = checksum( data, checksum( struct.pack("I", addr) ) ) 
        self.s.write(ATTN + DA_WRITE + struct.pack("I", addr))
        self.s.write(data)
        self.s.write(struct.pack("H", crc & 0xFFFF))
        r = self.s.read(2)
        ASSERT( CONF + CONF == r, "[{}] write block[64]: {}".format(r, hex(addr)))    

    def da_read_block(self, addr, size = 64):
        crc = checksum( struct.pack("IH", addr, size) )
        self.s.write(ATTN + DA_READ + struct.pack("IH", addr, size))
        self.s.write(struct.pack("H", crc & 0xFFFF))
        r = self.s.read(2)
        ASSERT( CONF + CONF == r, "[{}] read block[64]: {}".format(r, hex(addr)))   
        r = self.s.read(size)
        print(HEX(r))           

    def connect(self, timeout = 9.0):
        self.s.timeout = 0.1
        c = 0
        print('WAIT RESET')
        PB_BEGIN()
        while True:
            if c % 10 == 0: PB_STEP()
            c += 1
            self.s.write( ACK ) 
            r = self.s.read(4)   
            if b'BOOT' == r: 
                time.sleep(0.1)
                self.s.write( ATTN + PING ) 
                if PONG + PONG == self.s.read(2):
                    break       
                else: 
                    ERROR("BOOT")
            timeout -= self.s.timeout
            if timeout < 0:
                ERROR("Timeout") 
        PB_END(); 

def test_erase(m):
    print('ERASING')
    PB_BEGIN() 
    for i in xrange(0, 0x2000, 256): 
        m.da_erase_block(i + 0x2000)
        PB_STEP()
    PB_END()    

def test_write(m):
    print('PROGRAMING')   
    PB_BEGIN() 
    for i in xrange(0, 0x2000, 64): 
        m.da_write_block(i + 0x2000)
        PB_STEP()
    PB_END()      

def test_read(m):
    print('READING')   
    PB_BEGIN() 
    for i in xrange(0, 0x200, 64): 
        m.da_read_block(i+0x2000)
        PB_STEP()
    PB_END()   

def upload_app(module, file_name, com_port):  
    m = SAMR( Serial( com_port, 115200 ) )
    # FILE SIZE
    # OPEN FILE
    
    m.connect() 
    test_read(m)
    print('DONE')   
  

if __name__ == "__main__":
    upload_app('SAM34', 'file_name', 'COM19')