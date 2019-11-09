##########################################################################
#
#   WizIO 2020 Georgi Angelov
#       http://www.wizio.eu/
#       https://github.com/Wiz-IO/platform-sam-lora
# 
##########################################################################

from os.path import join
from SCons.Script import Builder
from common import *

def dev_upload(target, source, env):
    if 'atprogram' == env.BoardConfig().get("upload.tool"):
        atprogram(target, source, env)
        return
    print('[ERROR] Upload - not supported tool')

def dev_compiler(env):
    set_compiler(env)
    env.Append(UPLOAD_PORT='sam') # upload_port = "must exist"
    env.cortex = ["-mcpu=cortex-m0plus", "-mfloat-abi=soft", "-mthumb"]

def dev_init(env, platform):
    framework_dir = env.PioPlatform().get_package_dir("framework-sam-lora")
    env.tool_dir = join(env.PioPlatform().get_package_dir("tool-sam-lora"))
    create_template(env, [ 'main.c', 'startup_samr34.c' ])
    dev_compiler(env)
    env.framework_dir = env.PioPlatform().get_package_dir("framework-sam-lora")
    env.Append(
        CPPDEFINES = [ "__ATSAMR34J18B__", ],        
        CPPPATH = [       
            join(framework_dir, 'samr3'),
            join(framework_dir, 'baremetal', 'include'),
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
        LDSCRIPT_PATH = join(env.framework_dir, 'samr3', env.BoardConfig().get('build.' + platform + '-ld')),            
        LIBPATH = [], 
        LIBSOURCE_DIRS = [],       
        LIBS = [ 'gcc', 'm' ],               
        BUILDERS = dict( 
            CreateHex = Builder( 
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "ihex",
                    "$SOURCES",
                    "$TARGET",
                ]), "Building $TARGET"),
                suffix = ".hex"
            ),
            CreateBin = Builder( 
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET",
                ]), "Building $TARGET"),
                suffix = ".bin"
            )              
        ), 
        UPLOADCMD = dev_upload
    )
    libs = []   
    # BAREMETAL
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_baremetal"),
            join(env.framework_dir, "baremetal", "src"), 
    ))       
    # PROJECT
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))             
    env.Append(LIBS = libs)  