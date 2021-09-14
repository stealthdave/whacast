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
        self.state = None

        # attempt to connect to device
        try:
            self.device.register_status_listener(self)
            print("Now listening to device '{}'".format(self.name))
            # set inital amp state
            self.new_cast_status(self.device.status)
        except Exception as error:
            print("ERROR: Device \"{0}\" failed to load: {1}"\
                .format(self.name, error))

    '''
    Listen for changes in Chromecast Device connection status
    '''
    def new_cast_status(self, status):
        print("Chromecast {0} status: {1}".format(self.name, status.app_id))
        # Turn on amplifier
        if status.app_id is not None and self.state != "ON":
            print('{}: Amp ON!'.format(self.name))
            self.state = "ON"
            self.exec_device_commands(self.device_config["on"]["commands"])
        # Turn off amplifier
        elif status.app_id is None and self.state != "OFF":
            print('{}: Amp OFF!'.format(self.name))
            self.state = "OFF"
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
        url = f'https://maker.ifttt.com/trigger/{command["event"]}/with/key/{key}'
        print(f'ifttt command: "{url.replace(key, "{secret_key}")}"')
        response = requests.get(url)
        print(f'ifttt response: {response.status_code} - {response.text}')

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
        print("Send IR command: {}".format(" ".join(lirc_cmd)))
        print(call(lirc_cmd))
