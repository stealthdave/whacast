#/usr/bin/python
from __future__ import print_function
import json
import pychromecast
import time
from sys import argv
from cast_listener import CastListener

def usage():
    print("Usage: python -m {0} <config file>".format(argv[0]))
    exit(-1)


if __name__ == "__main__":
    try:
        json_file = argv[1]
    except Exception as error:
        usage()

    with open(json_file) as json_file:
        try:
            config = json.load(json_file)
        except Exception as error:
            usage()

        devices = {}
        chromecasts = pychromecast.get_chromecasts()

        for device_config in config["devices"]:
            friendly_name = device_config["friendly_name"]
            cast_device = next(cc for cc in chromecasts \
                                    if cc.device.friendly_name == friendly_name)
            cast_device.wait()
            if cast_device:
                devices[friendly_name] = CastListener(cast_device,
                                                      device_config,
                                                      config["global"])

        # halt the script if any of devices lose connection
        device_check = True
        while devices:
            device_check = True
            for device_name in devices.keys():
                device_check = device_check and devices[device_name]
