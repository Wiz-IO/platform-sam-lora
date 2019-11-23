##########################################################################
#
#   WizIO 2020 Georgi Angelov
#       http://www.wizio.eu/
#       https://github.com/Wiz-IO/platform-sam-lora
# 
##########################################################################
from __future__ import print_function
from os.path import join
from SCons.Script import Builder
from common import *
from SAMR_FU import *

def dev_upload(target, source, env):
    if 'atprogram' not in env.get("UPLOAD_PORT"):
        fu_upload_app(int(env.app, 16), join(env.get("BUILD_DIR"), "program.bin"), env.get("UPLOAD_PORT"))
        return

    if 'atprogram' == env.get("UPLOAD_PORT") and 'atprogram' == env.BoardConfig().get("upload.tool"):
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
    dev_compiler(env)
    env.app = env.BoardConfig().get("build.app", "0") 
    print(Fore.BLUE + 'APPLICATION START ADDRESS:', env.app)
    if 'atprogram' != env.get("UPLOAD_PORT"):
        env.Replace(UPLOAD_PORT = env.get("UPLOAD_PORT").replace('atprogram', ''))

    env.Append(
        ASFLAGS=[
            env.cortex,
            "-x", "assembler-with-cpp"
        ],
        CPPDEFINES = [ 
            'SAML21',
            "__{}__".format(env.BoardConfig().get("build.mcu")), 
            "{}=200".format(platform.upper()),
        ],        
        CPPPATH = [ 
            join(env.framework_dir, 'samr3'),
            join(env.framework_dir, 'baremetal', 'include'),            
            join(env.framework_dir,  platform, platform),
            join(env.framework_dir,  platform, 'cores', env.BoardConfig().get("build.core")),
            join(env.framework_dir,  platform, "variants", env.BoardConfig().get("build.variant")),                           
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
            "-fno-use-cxa-atexit", 
            "--entry=Reset_Handler",
            "-Xlinker", "--defsym=APP_BASE=" + env.app,
        ],  
        LDSCRIPT_PATH = join(env.framework_dir, 'samr3', env.BoardConfig().get('build.' + platform + '-ld')), 
        LIBPATH = [], 
        LIBSOURCE_DIRS = [ join(env.framework_dir, platform, "libraries"), ],        
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
    # ARDUINO
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_" + platform),
            join(env.framework_dir, platform, platform),
    ))     
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_core"),
            join(env.framework_dir, platform, "cores", env.BoardConfig().get("build.core")),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_variant"),
            join(env.framework_dir, platform, "variants", env.BoardConfig().get("build.variant")),
    ))         
    # PROJECT
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))             
    env.Append(LIBS = libs)  





    
