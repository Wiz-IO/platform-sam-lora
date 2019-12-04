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
    env.Append(UPLOAD_PORT='atprogram') 
    env.cortex = ["-mcpu=cortex-m0plus", "-mfloat-abi=soft", "-mthumb"]

def dev_init(env, platform):
    env.framework_dir = env.PioPlatform().get_package_dir("framework-sam-lora")
    env.tool_dir = join(env.PioPlatform().get_package_dir("tool-sam-lora"))
    create_template(env, [ 'main.c', 'startup_samr34.c' ])
    dev_compiler(env)
    env.app = env.BoardConfig().get('build.app', '0x0')  
    env.asf = env.BoardConfig().get('build.asf', '0') 
    env.Append(
        ASFLAGS=[
            env.cortex,
            "-x", "assembler-with-cpp"
        ],
        CPPDEFINES = [             
            "__{}__".format(env.BoardConfig().get("build.mcu")), 
         ],        
        CPPPATH = [       
            join(env.framework_dir, 'samr3'),
            join(env.framework_dir, 'baremetal', 'include'),
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")         
        ],        
        CFLAGS = [ 
            "-O0", 
            "-Wall", 
            "-Wfatal-errors",
            "-fno-omit-frame-pointer", 
            "-fno-strict-aliasing",                 
            "-fno-exceptions",                                                                                   
        ],  
        CXXFLAGS = [    
            "-O0",      
            "-Wall",   
            "-Wfatal-errors",                   
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
        ],  
        CCFLAGS = [ 
            env.cortex,
            "-fdata-sections",      
            "-ffunction-sections",
            "-fsingle-precision-constant",  
        ], 
        LINKFLAGS = [ 
            env.cortex, 
            "-nostartfiles", 
            "-Wall",
            "-Wfatal-errors",            
            "-Wl,--no-undefined", 
            "--entry=Reset_Handler",
            "-Xlinker", "--defsym=APP_BASE=" + env.app,
            "-Xlinker", "--gc-sections",              
            "-Wl,--gc-sections",            
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
    if env.asf != '0':
        env.Append(
            CPPPATH = [       
                join(env.framework_dir, 'asf', 'include'),
                join(env.framework_dir, 'asf', format(env.BoardConfig().get("build.core"))), # samr34
            ],
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
     # ASF
    if env.asf != '0':

        libs.append(
            env.BuildLibrary(
                join("$BUILD_DIR", "_asf"),
                join(env.framework_dir, "asf", "src"), 
        ))    
        libs.append(
            env.BuildLibrary(
                join("$BUILD_DIR", "_asf_samr3"),
                join(env.framework_dir, "asf", format(env.BoardConfig().get("build.core"))), # samr34
        ))    

    env.Append(LIBS = libs)  
