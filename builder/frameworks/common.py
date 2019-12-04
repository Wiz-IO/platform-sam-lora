##########################################################################
#
#   WizIO 2020 Georgi Angelov
#       http://www.wizio.eu/
#       https://github.com/Wiz-IO/platform-sam-lora
# 
##########################################################################

import os, json, tempfile, shutil, time
from os.path import join, normpath, basename
from shutil import copyfile
from subprocess import check_output, CalledProcessError, call, Popen, PIPE
from time import sleep, time
from colorama import Fore

def set_compiler(env):
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("//", "/"),
        AR="arm-none-eabi-ar",
        AS="arm-none-eabi-as",
        CC="arm-none-eabi-gcc",
        GDB="arm-none-eabi-gdb",
        CXX="arm-none-eabi-g++",
        OBJCOPY="arm-none-eabi-objcopy",
        RANLIB="arm-none-eabi-ranlib",
        SIZETOOL="arm-none-eabi-size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.rodata|\.text.align|\.ARM.exidx)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL -B -d $SOURCES',
        #PROGNAME="app",
        PROGSUFFIX=".elf",  
    )

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
    start_time = time()
    arg = env.BoardConfig().get("upload.args")
    cmd = []
    cmd.append( join(env.tool_dir, "atbackend", "atprogram") ) 
    for a in arg: cmd.append(a)
    exe = cmd    
    #exe.append('-v')
    exe.append('chiperase') 
    exe.append('program') 
    exe.append('-f')
    exe.append(join(env.get("BUILD_DIR"), env['PROGNAME'] + ".hex"))
    #print('PROGRAMING', exe)
    execute(exe)
    print( "Elapsed time: {0:.2f} s".format(time() - start_time) )

def create_template(env, files):
    for src in files:
        src = join(env.PioPlatform().get_package_dir("framework-sam-lora"), "templates", src)
        head, fname = os.path.split(src)
        dst = join( env.subst("$PROJECT_DIR"), "src", fname)        
        if False == os.path.isfile( dst ):
            copyfile(src, dst)
