# LArS_SC
Collection of scripts and libs for running the slow control of LArS

The suite is mainly python scripts based and is thought to be run as standalone software.
The slow control is based on a plugin pattern, and each plugin is actually a device.

The structure is the following:
 - Top level directory: scripts that actually are meant to run
 - `core` directory: there is the engine class, "virtual" classes that define the interface of a SC device, and generic utils.
 - `Devs` directory: here the are the SC devices plugin classes (concrete implementations). In the source files define the concrete classes are defined and their objects are instanced (as per the real configuration) at import time. Removing or adding a SC device from the SC to represent the actual setup can simply be done by adding or removing the lines that instance the object (normally at the bottom).
 - `config` directory: contains the json config files, typically required for running the script in the top level directory, and the systemd services config files. Bothe kind of config file must be moved to a directory not git synced and edited if needed.
 - `scripts` directory: contains the shell script that run the python scripts as a service (either via crontab or better via systemd.

