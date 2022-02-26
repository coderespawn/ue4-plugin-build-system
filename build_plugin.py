import json
import argparse
import sys
import os
import subprocess
import shutil
import datetime

def ParseArgs():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("uplugin", help="Path to the .uplugin Plugin descriptor. Or directory containting the uplugin file (if --find_descriptor is specified)", type=str)
    argparser.add_argument("--platform", "-p", help="Platform to compile on, Separate multiple platforms with a + symbol", type=str, default="Win64")
    argparser.add_argument("--find_descriptor", help="Finds the descriptor in the given path.  uplugin will contain the directory to search the *.uplugin file", action="store_true")
    return argparser.parse_args()


def LoadConfig():
    script_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(script_path)
    config_path = dir_path + "/config.json"
    with open(config_path) as f:
        return json.load(f)

args = ParseArgs()
config = LoadConfig()

def FilterVersionNumber(version):
    dot_idx = version.rfind('.')
    if dot_idx < 0:
        return version
    if version.rfind('.', 0, dot_idx) < 0:
        # Only one dot in this version
        return version
    
    return version[:dot_idx]

def ExtractEngineVersion(uplugin):
    with open(uplugin, "r") as f:
        plugin_desc = json.load(f)
        full_ver = plugin_desc["EngineVersion"]
        return FilterVersionNumber(full_ver)

def ExtractPluginVersion(uplugin):
    with open(uplugin, "r") as f:
        plugin_desc = json.load(f)
        return plugin_desc["VersionName"]

def GetPluginName(uplugin):
    basename = os.path.basename(uplugin)
    return os.path.splitext(basename)[0]

def GetLogFilename(uplugin, engine_ver):
    if not "log_dir" in config.keys():
        print ("ERROR: Log directory not specified in configuration (log_dir): ")
        sys.exit()
    
    log_dir = config["log_dir"]
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    else:
        # Make sure this is not a file
        if os.path.isfile(log_dir):
            print ("ERROR: config log_dir points to an existing file. It should point to a directory: ", log_dir)
            sys.exit()
    
    plugin_name = GetPluginName(uplugin)
    log_filename = "%s/BuildLog.%s.%s.log" % (config["log_dir"], plugin_name, engine_ver)
    log_filename = os.path.abspath(log_filename)
    
    time = str(datetime.datetime.now()).replace(' ', '_').replace(':', '-')
    timestamped_log_filename = "%s/BuildLog.%s.%s_%s.log" % (config["log_dir"], plugin_name, engine_ver, time)
    timestamped_log_filename = os.path.abspath(timestamped_log_filename)

    return log_filename, timestamped_log_filename



def GetStagingDir(engine_ver, uplugin):
    plugin_name = GetPluginName(uplugin)
    staging = config["staging_paths"][engine_ver]
    staging_path = os.path.join(staging, plugin_name)
    staging_path = os.path.abspath(staging_path)
    return staging_path
    

if args.find_descriptor:
    search_dir = args.uplugin
    for file in os.listdir(search_dir):
        if file.endswith(".uplugin"):
            uplugin = os.path.join(search_dir, file)
            break
else:
    uplugin = args.uplugin

if not uplugin.endswith(".uplugin") or not os.path.exists(uplugin):
    print ("ERROR: Invalid uplugin file path", uplugin)
    sys.exit()

uplugin = os.path.abspath(uplugin)
engine_ver = ExtractEngineVersion(uplugin)
plugin_ver = ExtractPluginVersion(uplugin)

if not engine_ver in config["engine_paths"].keys():
    print ("ERROR: Unregistered engine path: ", engine_ver)
    sys.exit()

if not engine_ver in config["staging_paths"].keys():
    print ("ERROR: Unregistered staging path for engine: ", engine_ver)
    sys.exit()

if not "uat_path" in config.keys():
    print ("ERROR: uat_path not defined. This should be set to a value relative to the base engine directory")
    sys.exit()


staging = GetStagingDir(engine_ver, uplugin)
engine_path = config["engine_paths"][engine_ver]
run_uat = os.path.abspath(os.path.join(engine_path, config["uat_path"]))
target_platforms = args.platform or config["target_platforms"]

if not os.path.exists(run_uat):
    print ("ERROR: Invalid UAT file path:", run_uat)
    sys.exit()


print ("------------------------------------")
print ("Engine ver: ", engine_ver)
print ("Plugin ver: ", plugin_ver)
print ("Plugin:     ", uplugin)
print ("Staging:    ", staging)
print ("UAT:        ", run_uat)
print ("Platform:   ", target_platforms)
print ("------------------------------------")

log_filename, timestamped_log_filename = GetLogFilename(uplugin, engine_ver)

process = subprocess.Popen([
    run_uat,
    'BuildPlugin',
    '-Plugin=%s' % uplugin, 
    '-Package=%s' % staging,
    '-Rocket',
    '-TargetPlatforms=%s' % target_platforms
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT)
    
with open(log_filename, 'w', newline="\n") as logfile:
    for line in process.stdout:
        line_string = line.decode('utf-8')
        sys.stdout.write(line_string)
        logfile.write(line_string)

process.wait()

# Copy over the log file to a timestamped filename
shutil.copyfile(log_filename, timestamped_log_filename)

print ("Compilation complete")
