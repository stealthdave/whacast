#!/usr/bin/python
import pychromecast
import threading
import os
import json
import requests
import time
from sys import argv
from subprocess import call


# Globals
devices = {}
device_init_threads = {}


'''
Write to log file if set; otherwise standard print
'''
def log(statement, initialize = False):
    write_mode = "a"
    if initialize:
        write_mode = "w"
    if "log_file" in config["global"].keys():
        with open(config["global"]["log_file"], write_mode) as log_file:
            log_file.write("{} - {}\n".format(time.strftime("%b %d %Y %H:%M:%S"), statement))
    else:
        print(statement)


'''
Call an IFTTT recipe
'''
def call_ifttt(event, key):
    url = "https://maker.ifttt.com/trigger/{0}/with/key/{1}".format(event, key)
    log("Posting URL: {}".format(url))
    return requests.post(url)


'''
Control an IR device
'''
def call_ir_device(commands):
    command_template = " ".join((config["control_services"]["lirc"]["cmd"], "--count={count} SEND_ONCE {device} {command}",))

    for ir_command in commands["ir_commands"]:
        # default count of 1
        if "count" not in ir_command.keys():
            ir_command["count"] = 1
        # send ir command through lirc
        #call(command_template.format(ir_command))
        log("Send IR command: {}".format(command_template.format(**ir_command)))
        # if a delay is set, wait before sending the next command
        if "delay" in commands.keys():
            time.sleep(commands["delay"])


'''
Initialize device threads
'''
class cast_thread(threading.Thread):
    def __init__(self, device_config, delay = 0):
        threading.Thread.__init__(self)
        self.device_config = device_config
        self.delay = delay
    def run(self):
        log("Begin device thread \"{}\".".format(self.device_config["friendly_name"]))
        friendly_name = self.device_config["friendly_name"]
        if self.delay:
            time.sleep(self.delay)
        load_device = True
        while load_device:
            # clear device before loading
            if friendly_name in devices.keys():
                devices[friendly_name]["device"] = None
            # load device
            load_chromecast(self.device_config)
            # if reload_device_delay is set, reload the device on a loop
            # (pychromecast objects tend to get stale after a while)
            if config["global"]["reload_device_delay"] <= 0:
                load_device = False
            else:
                time.sleep(config["global"]["reload_device_delay"])


'''
Load Chromecast object
'''
def load_chromecast(cast_config):
    friendly_name = cast_config["friendly_name"]
    
    log("==> Load device \"{}\"".format(cast_config["friendly_name"]))
    
    # load pychromecast object
    if friendly_name not in devices:
        devices[friendly_name] = {
            'friendly_name': friendly_name,
            'device': None,
            'enabled': False,
            'status': False,
            'config': cast_config,
            'retry': 0
        }
    
    # attempt to connect to device
    try:
        devices[friendly_name]["device"] = pychromecast.get_chromecast(friendly_name = friendly_name)
    except:
        log("ERROR: Device \"{0}\" failed to load.)".format(friendly_name))

    # if object can't be loaded, try again after a specified delay
    if devices[friendly_name]["device"] is None:
        time.sleep(config["global"]["reconnect_delay"])
        devices[friendly_name]["device"]["retry"] = devices[friendly_name]["device"]["retry"] + 1
        if devices[friendly_name]["device"]["retry"] < config["global"]["max_retries"]:
            load_chromecast(friendly_name)
        else:
            log("ERROR: Maximum attempts to connect to \"{}\" has been reached.".format(friendly_name))
    else:
        devices[friendly_name]["enabled"] = True
    
    return

'''
Check for change in status
'''
def test_chromecast(friendly_name):
    cast = devices[friendly_name]
    
    # make sure chromecast is still connected
    try:
        # turn on amp 
        if cast["device"].app_id is not None and cast["status"] is False:
            # turn on via IFTTT
            if cast["config"]["control"] == "ifttt":
                log("Turning IFTTT device on...")
                call_ifttt(cast["config"]["on"]["event"], config["control_services"]["ifttt"]["key"])
                
            # turn on via LIRC
            if cast["config"]["control"] == "lirc":
                log("Turning LIRC device on...")
                call_ir_device(cast["config"]["on"])
            
            cast["status"] = True
            log("Amp for \"{}\" is ON".format(friendly_name))
            
        # turn off amp 
        if cast["device"].app_id is None and cast["status"] is True:
            # turn off via IFTTT
            if cast["config"]["control"] == "ifttt":
                log("Turning IFTTT device off...")
                call_ifttt(cast["config"]["off"]["event"], config["control_services"]["ifttt"]["key"])
            
            # turn off via LIRC
            if cast["config"]["control"] == "lirc":
                log("Turning LIRC device off... TODO")
                call_ir_device(cast["config"]["off"])
            
            cast["status"] = False
            log("Amp for \"{}\" is OFF".format(friendly_name))
    
    # set Chromecast to disabled
    except:
        cast["enabled"] = False
    
    return

def test_chromecast_recursive():
    while True:
        for friendly_name in devices.keys():
            device = devices[friendly_name]
            # if the device is available, see if its state has changed
            if device["enabled"]:
                test_chromecast(friendly_name)
            # otherwise kick off a thread to reconnect the device
            else:
                # thread to reconnect device
                if not device_init_threads[friendly_name].isAlive():
                    device_init_threads[friendly_name] = cast_thread(device, config["global"]["reconnect_delay"])
                    device_init_threads[friendly_name].start()

        # wait for a specified interval and check again
        time.sleep(config["global"]["poll_delay"])


if __name__ == "__main__":
    try:
        json_file = argv[1]
    except:
        print("Usage: python -m {0} <config file>".format(argv[0]))
        exit(-1)

    with open(json_file) as json_file:
        config = json.load(json_file)

        log("CONFIG LOADED", True)

        # test call_ir_device
        call_ir_device(config["chromecasts"][0]["on"])
        
        # Initialize Chromecast devices
        for device in config["chromecasts"]:
            device_init_threads[device["friendly_name"]] = cast_thread(device)
            device_init_threads[device["friendly_name"]].start()

        test_chromecast_recursive()
