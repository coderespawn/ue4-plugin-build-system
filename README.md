UE4 Plugin Build System
=======================

Automated Build System for UE4 Plugins


One-time Setup Instructions
---------------------------

Create an environment variable ``BUILD_UE4_PLUGIN`` and assign it to the absolute path of the `ue4_plugin_build_system.py` file in this repository (e.g. `C:\tools\build-system\ue4_plugin_build_system.py`)

Copy over the config template file ``config.template.json`` to ``config.json`` and update the values according to your engine paths in your filesystem

### engine_paths
List of engine verions and their base path in the file system. Add more versions to the list as needed

### staging_directory
This creates a staging directory for each engine version.   All you plugins for this version go under this. Add more versions to this list as needed

### log_dir
The directory to save the build log files

### uat_path
The relative path to the RunUAT script that comes with the engine. This path is usually fixed in the engine and you won't need to change it.  However, the template has a reference to the batch file (RunUAT.bat) which is used in windows.  If you are on Mac or Linux, you'll want to change this to **RunUAT.sh**

Project Setup Instructions
--------------------------

We're going to copy over the build invocation script to the plugin folders so it can build the plugin

For a project that hosts your C++ plugin,  navigate to the plugin's direction (GAME_PROJECT/Plugins/MyPlugin/..) and drop in the ``extras/BuildPlugin.py`` script into the plugins directory's ``Scripts/BuildSystem`` directoy

So you end up with the following path: ``GAME_PROJECT/Plugins/MyPlugin/Scripts/BuildSyste/BuildPlugin.py``

Double click this script to build your plugin (Make sure python is installed)

This file doesn't require any modifications and you can drop it in any plugin and it will just work
