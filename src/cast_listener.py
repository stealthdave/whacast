from __future__ import print_function
import pychromecast
import requests
import time
from subprocess import call

class CastListener:
    def __init__(self, chromecast, device_config, global_config):
        self.device = chromecast
        self.device_config = device_config
        self.global_config = global_config
        self.name = device_config["friendly_name"]

        # attempt to connect to device
        try:
            self.device.register_status_listener(self)
            self.log("Now listening to device '{}'".format(self.name))
            # set inital amp state
            self.new_cast_status(self.device.status)
        except Exception as error:
            self.log("ERROR: Device \"{0}\" failed to load: {1}"\
                .format(self.name, error))

    '''
    Write to log file if set; otherwise standard print
    '''
    def log(self, statement, initialize = False):
        write_mode = "a"
        if initialize:
            write_mode = "w"
        if "log_file" in self.global_config.keys():
            log_file = self.global_config["log_file"]
            with open(log_file, write_mode) as log_file:
                timestamp = time.strftime("%b %d %Y %H:%M:%S")
                log_file.write("{} - {}\n".format(timestamp, statement))
        else:
            print(statement)

    '''
    Listen for changes in Chromecast Device connection status
    '''
    def new_cast_status(self, status):
        self.log("Chromecast {0} status: {1}".format(self.name,
                                                     status.app_id))
        # Turn on amplifier
        if status.app_id is not None:
            self.log('{}: Amp ON!'.format(self.name))
            self.exec_device_commands(self.device_config["on"]["commands"])
        # Turn off amplifier
        else:
            self.log('{}: Amp OFF!'.format(self.name))
            self.exec_device_commands(self.device_config["off"]["commands"])

    '''
    Execute amplifier commands
    '''
    def exec_device_commands(self, commands):
        for command in commands:
            if command["control"] == "ifttt":
                self.call_ifttt(command)
            if command["control"] == "lirc":
                self.call_ir_device(command)
            # if a delay is set, wait before sending the next command
            if "delay" in command.keys():
                time.sleep(command["delay"])

    '''
    Call an IFTTT recipe
    '''
    def call_ifttt(self, command):
        key = self.global_config["control_services"]["ifttt"]["key"]
        url = "https://maker.ifttt.com/trigger/{0}/with/key/{1}"\
            .format(command["event"], key)
        self.log('ifttt command: {}'.format(url))
        self.log(requests.post(url))

    '''
    Control an IR device
    '''
    def call_ir_device(self, ir_command):
        # default count of 1
        count = ir_command["count"] if "count" in ir_command.keys() else 1
        lirc_cmd = [
            self.global_config["control_services"]["lirc"]["cmd"],
            "--count={}".format(count),
            "SEND_ONCE",
            ir_command["device"],
            ir_command["command"]
        ]
        # send the lirc command
        self.log("Send IR command: {}".format(" ".join(lirc_cmd)))
        self.log(call(lirc_cmd))

