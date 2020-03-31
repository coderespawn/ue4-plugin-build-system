UE4 Plugin Build System
=======================

Automated Build System for UE4 Plugins


One-time Setup Instructions
---------------------------

Create an environment variable ``BUILD_UE4_PLUGIN`` and assign it to the absolute path of the `ue4_plugin_build_system.py` file in this folder (e.g. `C:\tools\build-system\ue4_plugin_build_system.py`)

Copy over the config template file ``config.template.json`` to ``config.json`` and update the values according to your engine paths in your filesystem


Project Setup Instructions
--------------------------

We're going to copy over the build invocation script (so it calls the build system) and build the plugin

For a project that hosts you C++ plugin,  navigate to the plugin's direction (GAME_PROJECT/Plugins/MyPlugin/..) and drop in the ``extras/BuildPlugin.py`` script into the plugins directory's ``Scripts/BuildSystem`` directoy

So you end up with the following path: ``GAME_PROJECT/Plugins/MyPlugin/Scripts/BuildSyste/BuildPlugin.py``

Double click this script to build your plugin (Make sure python is installed)

