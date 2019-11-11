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

START_ADDRESS = 0x02000
MAX_ADDRESS   = 0x40000

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

def align(size, mask):
    F = size / mask
    B = int(F)
    if F % 1 > 0: 
        B += 1  
    return B

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
        print('WAITING RESET')
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

    def update(self, start_address, path):
        ext = path.split(".")
        ASSERT( os.path.isfile(path), "Firmware not exist")
        ASSERT( 'bin' == ext[-1], "Firmware is a not bin file")        
        size = os.path.getsize(path)
        ASSERT( size > 64, "Firmware is too small")
        ASSERT( start_address + size < MAX_ADDRESS, "Firmware size is too big")

        print('ERASING')
        PB_BEGIN()  
        B = align(size, PAGE_SIZE)   
        for i in range( B ):
            address = start_address + (i * PAGE_SIZE)
            #print('erase', i, hex(address))
            self.da_erase_block(address)
            PB_STEP()
        PB_END() 

        print('PROGRAMING', os.path.basename(path), '({} bytes) '.format(size)) 
        PB_BEGIN() 
        f = open(path, 'rb')        
        B = align(size, BLOCK_SIZE)
        f.seek(64) # skip the first block
        for i in range( B - 1 ): 
            data = f.read(BLOCK_SIZE)
            m = BLOCK_SIZE - len(data) 
            if m > 0: data = data + ( m * b'\xFF' )
            address = start_address + (i * BLOCK_SIZE) + 64
            #if data: print('write', i, hex(address))            
            self.da_write_block(address, data)
            PB_STEP()
        f.seek(0) # write the first block
        self.da_write_block(start_address, f.read(BLOCK_SIZE))
        f.close()            
        PB_END()
         


def upload_app(address, path, com_port):  
    m = SAMR( Serial( com_port, 115200 ) )    
    m.connect() 
    m.update(address, path)  
    print()
  

if __name__ == "__main__":
    upload_app(START_ADDRESS, 'C:\\Users\\HP\\.platformio\\platforms\\sam-lora\\builder\\frameworks\\program.bin', 'COM19')