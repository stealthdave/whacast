Whole House Audio Cast Control
===========================

This script will automatically turn on IFTTT and infrared remote controlled devices, such as audio amplifiers or televisions, whenever content is streamed to a Google Cast-enabled device, such as Google's Chromecast Audio devices.  The purpose of this script is to automate the process of turning on audio for a whole house audio system without needing to leave amplifiers turned on all the time, wasting electricity and unnecessarily wearing down your equipment, while making the system as convenient as possible.


Requirements
----------------------

**whacast** is developed for Linux installations, but it should run on most network-connected devices running Python 2.7+, including the Raspberry Pi.  **whacast** uses [PyChromecast](https://github.com/balloob/pychromecast "PyChromecast") to track the status of your Cast devices, and turns equipment on or off depending on whether content is currently being streamed.  A Python virtual environment (venv) is recommended.


Installation
----------------
Create your virtual environment with the following command:

    $ ./install.sh

This creates a Python virtual environment named `castenv`.  You can now start **whacast** with the following command:

    $ ./castenv/bin/python -m whacast settings.json

If you wish to create a startup service for `systemd`, you can use the included `whacast.service` file as a template.


Settings
-----------
Configuration of **whacast** is done through a `json` formatted settings file that is passed as an argument at the time of execution.  (See the example above in _Installation_.)  The settings file consists of (3) sections:

 - **global** - Settings for timing and logging
 - **chromecasts** - Chromecast devices to watch and how to turn on/off devices attached to them
 - **control_services** - Shared settings for external services, currently _IFTTT_ and `lirc`

**GLOBAL**

These settings determine wait times for the various functions involved in tracking the status of various Chromecast devices.

    "global": {
      "log_file": "/var/log/whacast.log"  // location of the log file
      "control_services": {               // see the CONTROL SERVICES section below
        ...
      }
    }

**CONTROL SERVICES**

Common data needed for control services IFTTT and LIRC that are not specific to the Chromecast devices.  These commands

    "control_services": {
      "ifttt": {
        "key": "__super_secret_ifttt_key_goes_here__"
      },
      "lirc": {
        "cmd": "/usr/bin/irsend"    // send IR commands to LIRC device; requires
                                    // hardware setup
      }
    }

**CHROMECASTS**

The list of Cast-enabled devices that you wish to monitor identified by their "friendly names".  e.g., the text name that you set that shows up in the Cast button in your apps.  See the sample `settings.json` file for examples of an `lirc` and `ifttt` device.
