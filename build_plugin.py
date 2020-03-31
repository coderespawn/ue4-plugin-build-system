import json
import argparse
import sys
import os
import subprocess


def ParseArgs():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("uplugin", help="Path to the .uplugin Plugin descriptor. Or directory containting the uplugin file (if --find_descriptor is specified)", type=str)
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

def ExtractEngineVersion(uplugin):
    with open(uplugin, "r") as f:
        plugin_desc = json.load(f)
        full_ver = plugin_desc["EngineVersion"]
        dot_idx = full_ver.rfind('.')
        return full_ver[:dot_idx]

def GetOutputFilename(uplugin, engine_ver):
    if not "log_dir" in config.keys():
        print ("ERROR: Log directory not specified in configuration (log_dir): ")
        sys.exit()
    
    basename = os.path.basename(uplugin)
    plugin_name = os.path.splitext(basename)[0]
    log_filename = "%s/BuildLog.%s.%s.log" % (config["log_dir"], plugin_name, engine_ver)
    log_filename = os.path.abspath(log_filename)
    return log_filename

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

if not engine_ver in config["engine_paths"].keys():
    print ("ERROR: Unregistered engine path: ", engine_ver)
    sys.exit()

if not engine_ver in config["staging_paths"].keys():
    print ("ERROR: Unregistered staging path for engine: ", engine_ver)
    sys.exit()

if not "uat_path" in config.keys():
    print ("ERROR: uat_path not defined. This should be set to a value relative to the base engine directory")
    sys.exit()


staging = config["staging_paths"][engine_ver]
engine_path = config["engine_paths"][engine_ver]
run_uat = os.path.join(engine_path, config["uat_path"])

if not os.path.exists(run_uat):
    print ("ERROR: Invalid UAT file path:", run_uat)
    sys.exit()


print ("------------------------------------")
print ("Engine:", engine_ver)
print ("Plugin:", uplugin)
print ("Staging:", staging)
#print ("UAT:", run_uat)
print ("------------------------------------")


process = subprocess.Popen([
    run_uat,
    'BuildPlugin',
    '-Plugin=%s' % uplugin, 
    '-Package=%s' % staging,
    '-Rocket'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT)
    
log_filename = GetOutputFilename(uplugin, engine_ver)
with open(log_filename, 'w', newline=os.linesep) as logfile:
    for line in process.stdout:
        line_string = line.decode('utf-8')
        sys.stdout.write(line_string)
        logfile.write(line_string)

process.wait()

print ("Compilation complete")
