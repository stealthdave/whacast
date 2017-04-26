#/usr/bin/python
from __future__ import print_function
import json
import pychromecast
import time
from sys import argv
from cast_listener import CastListener
from app_log import app_log

def usage(message):
    if message:
        print(message)
    print("Usage: python -m {0} <config file>".format(argv[0]))
    exit(-1)


if __name__ == "__main__":
    try:
        json_file = argv[1]
    except Exception as error:
        usage("Required parameter, Config file, is missing.")

    with open(json_file) as json_file:
        try:
            config = json.load(json_file)
        except Exception as error:
            usage("Could not open configuration file '{}'".format(json_file))

        log_file = config["global"]["log_file"]
        app_log(log_file, "=== START WHACAST ===")

        # Load Devices
        devices = {}
        chromecasts = pychromecast.get_chromecasts()

        for device_config in config["devices"]:
            friendly_name = device_config["friendly_name"]
            app_log(log_file, "Loading Chromecast '{}'".format(friendly_name))
            cast_device = next(cc for cc in chromecasts \
                                    if cc.device.friendly_name == friendly_name)
            cast_device.wait()
            if cast_device:
                devices[friendly_name] = CastListener(cast_device,
                                                      device_config,
                                                      config["global"])

        app_log(log_file, "=== All Chromecasts Loaded ===")

        # halt the script if any of devices lose connection
        device_check = True
        while device_check:
            for device_name in devices.keys():
                # no need to check every possible moment
                time.sleep(10)
                try:
                    device_check = devices[device_name].status is not None
                except Exception as error:
                    error_msg = "DEVICE ERROR '{0}'\nError: {1}"
                    app_log(log_file, error_msg.format(device_name, error))
                    device_check = False
                if not device_check:
                    app_log(log_file, "DEVICE '{}' DISCONNECTED"\
                        .format(device_name))

        app_log(log_file, "=== EXIT WHACAST ===")
