# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-sam-lora

import os, json, tempfile, shutil
from os.path import join, normpath, basename
from shutil import copyfile
from subprocess import check_output, CalledProcessError, call, Popen, PIPE
from time import sleep
from colorama import Fore

def execute(cmd):
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    out += err
    lines = out.decode().split("\r\n")
    if proc.returncode == 0: 
        COLOR = Fore.GREEN
    else: 
        COLOR = Fore.RED
    for i in range( len(lines) ):
        print( COLOR + lines[i] )
        sleep(0.02)
    if proc.returncode != 0:
        sleep(0.02)
        exit(1)
    return 0

def atprogram(target, source, env):
    arg = env.BoardConfig().get("upload.args")
    cmd = []
    cmd.append( join(env.tool_dir, "atbackend", "atprogram") ) 
    for a in arg: cmd.append(a)

    exe = cmd
    exe.append('-v')
    exe.append('erase')
    print('EXECUTE', exe)
    execute(exe)
    
    exe = cmd
    exe.append('program')
    exe.append('-f')
    exe.append(join(env.get("BUILD_DIR"), "program.hex"))
    print('EXECUTE', exe)
    execute(exe)