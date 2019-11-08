# WizIO 2019 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-sam-lora

from os.path import join
from common import atprogram
from SCons.Script import Builder

def dev_create_template(env, files):
    pass

def dev_upload(target, source, env):
    if 'atprogram' == env.BoardConfig().get("upload.tool"):
        atprogram(target, source, env)
        return
    print('[ERROR] Upload - not supported tool')

def dev_pack(target, source, env):
    pass

def dev_compiler(env):
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
        SIZEPROGREGEXP=r"^(?:/.text|/.data|/.bootloader)/s+(/d+).*",
        SIZEDATAREGEXP=r"^(?:/.data|/.bss|/.noinit)/s+(/d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        #PROGNAME="app",
        PROGSUFFIX=".elf",  
    )
    env.Append(UPLOAD_PORT='sam') # upload_port = "must exist variable"
    env.cortex = ["-mcpu=cortex-m0plus", "-mfloat-abi=soft", "-mthumb"]

def dev_init(env, platform):
    framework_dir = env.PioPlatform().get_package_dir("framework-sam-lora")
    env.tool_dir = join(env.PioPlatform().get_package_dir("tool-sam-lora"))
    dev_create_template(env, [])
    dev_compiler(env)
    env.framework_dir = env.PioPlatform().get_package_dir("framework-sam-lora")
    env.Append(
        CPPDEFINES = [ "__ATSAMR34J18B__", ],        
        CPPPATH = [       
            join(framework_dir, 'samr3'),
            join(framework_dir, 'samr3'),
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")         
        ],        
        CFLAGS = [ 
            "-O0", 
            "-fno-omit-frame-pointer", 
            "-fno-strict-aliasing",  
            "-fno-exceptions",
            "-Wall",                                                                                   
        ],  
        CXXFLAGS = [    
            "-O0",                            
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
        ],  
        CCFLAGS = [ env.cortex ], 
        LINKFLAGS = [ 
            env.cortex, 
            "-nostartfiles", 
            "-Wl,--no-undefined", 
            "-Wl,-n",
        ],  
        LDSCRIPT_PATH = join(env.framework_dir, 'samr3', 'samr34j18b_flash.ld'),            
        LIBPATH = [], 
        LIBSOURCE_DIRS=[ ],       
        LIBS = [ "gcc" ],               
        BUILDERS = dict( 
            PackImage = Builder( 
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "ihex",
                    "$SOURCES",
                    "$TARGET",
                ]), "Building $TARGET"),
                suffix = ".hex"
            ) 
        ), 
        UPLOADCMD = dev_upload
    )
    libs = []    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))         
    env.Append(LIBS = libs)  





    #print('PROGNAME', env['PROGNAME'])