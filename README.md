Whole House Audio Cast Control
===========================

This script will automatically turn on IFTTT and infrared remote controlled devices, such as audio amplifiers or televisions, whenever content is streamed to a Google Cast-enabled device, such as Google's Chromecast Audio devices.  The purpose of this script is to automate the process of turning on audio for a whole house audio system without needing to leave amplifiers turned on all the time, wasting electricity and unnecessarily wearing down your equipment, while making the system as convenient as possible.


Requirements
----------------------

**whacast** is developed for Linux installations, but it should run on most network-connected devices running Python 2.7+, including the Raspberry Pi.  **whacast** uses [PyChromecast](https://github.com/balloob/pychromecast "PyChromecast") to track the status of your Cast devices, and turns equipment on or off depending on whether content is currently being streamed.  A Python virtual environment (venv) is recommended.


Installation
----------------
Create your virtual environment with the following command:

    $ ./castenv.sh

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
      "poll_delay": 0.25,           // number of seconds between each 
                                    // check of a Chromecast's status
      "reconnect_delay": 60,        // number of seconds between attempts
                                    // to reconnect to a Chromecast
      "reload_device_delay": 14400, // number of seconds to wait before retrying
                                    // an unresponsive Chromecast
      "max_retries": 15,            // number of times to attempt to connect to a
                                     // Chromecast before considering it unresponsive
      "log_file": "/var/log/whacast.log" 
                                    // location of the log file
    }
**CHROMECASTS**

The list of Cast-enabled devices that you wish to monitor identified by their "friendly names".  e.g., the text name that you set that shows up in the Cast button in your apps.

    "chromecasts": [ // begin list
      { // Example IFTTT Device
        "friendly_name": "WHA Back Yard", 
                                  // your device's "friendly name"
        "control": "ifttt",       // the type of device to control remotely;
                                  // currently only "ifttt" and "lirc" are supported
        "on": {                   // command to turn device on
          "event": "backyard_on"  // IFTTT event to run
        },
        "off": {                  // command to turn device off
          "event": "backyard_off" // IFTTT event to run
        }
      },
      { // Example LIRC Device
        "friendly_name": "WHA Living Room",
        "control": "lirc",        // Control an LIRC device
        "on": {
          "ir_commands": [        // list of IR commands to send
            { // first command
              "device": "htc",      // LIRC device name
              "command": "POWER_ON",// command to send
              "count": 3            // number of times to send this command
            },
            { // next command
              "device": "htc",
              "command": "AUX_INPUT"
            }
          ],
          "delay": 0              // number of seconds (or fraction) to delay between
                                  // sending LIRC commands
        }, // END ON
        "off": {
          "ir_commands": [
            {
              "device": "htc",
              "command": "POWER_OFF"
            }
          ],
          "delay": 0
        } // END OFF
      }
    ] // END DEVICE LIST
**CONTROL SERVICES**

Common data needed for control services IFTTT and LIRC that are not specific to the Chromecast devices.

    "control_services": {
      "ifttt": {
        "key": "__super_secret_ifttt_key_goes_here__"
      },
      "lirc": {
        "cmd": "/usr/bin/irsend"    // send IR commands to LIRC device; requires
                                    // hardware setup
      }
    }

