import json
import socket
import time

from protocol import Protocol
import select


class ServerCommunication:
    def __init__(self, peripheral_count, gui_object, rssi_data_obj):
        # socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create the server socket

        # open config file
        with open('config.json', 'r') as f:
            file_content = f.read()
            config = json.loads(file_content)

        self.ip_addr = config['server_ip']
        self.port = config['server_port']
        self.recv_size = 1000

        # Data structures
        self.peripheral_devices = {}  # dictionary that holds all the peripheral ip addresses and their mac addresses
        self.verification_list = []  # list of ip addresses that represent sockets that need to be verified
        self.connected_peripherals = 0

        self.min_peripherals = peripheral_count  # amount of peripheral devices required

        self.central_device_mac = '1C:9D:C2:35:A8:52'

        # GuiManager
        self.gui_object = gui_object

        # RssiData
        self.rssi_data_obj = rssi_data_obj

    def receive_error(self, ip_addr, error):  # if response[0] is false, handle it here
        if error == 'empty':  # socket disconnected
            print(f'{ip_addr} has disconnected gracefully')
            # handle disconnection ...
            del self.peripheral_devices[ip_addr]  # remove from dictionary
            self.connected_peripherals -= 1
            # TODO handle the rest
        else:  # error with data formatting
            print('error with data formatting, or exception')
            # handle error

    def verify_connected_sockets(self, data, ip_addr):
        response = Protocol.get_serialized_data(data)
        if response[0]:
            print(response[1][0])
            if response[1][0] in self.gui_object.mac_list:
                # TODO Make sure that the same mac address isn't already connected, and add the mac address to peripheral devices list/dictionary
                print(f'authenticated {ip_addr}, mac address is {response[1][0]}')
                self.gui_object.one_meter_rssi_dict[response[1][0]] = response[1][1]
                print(f'one meter rssi is: {response[1][1]}')
                # handle lists and dictionaries
                self.connected_peripherals += 1
                self.verification_list.remove(ip_addr)
                self.peripheral_devices[ip_addr] = response[1][0]
                # send start message
                self.server_socket.sendto(Protocol.create_msg('start'), ip_addr)
            else:  # if socket is not a peripheral device
                print(f'{ip_addr} is not a peripheral device.')
                self.verification_list.remove(ip_addr)
        else:
            self.receive_error(ip_addr, response[1])

    def handle_peripheral_communication(self, data, ip_addr):
        print(f'getting data from peripheral device, {ip_addr} and checking')

        response = Protocol.get_serialized_data(data)  # receive data from socket
        if response[0]:
            #print(f'got data from {ip_addr}\n{response[1]}\n')
            if self.connected_peripherals >= self.min_peripherals:  # minimum of three peripherals do trilaterate
                print('doing things with data')
                self.get_central_device_data(response[1], ip_addr)
            else:
                print('not doing anything with data, not enough peripherals')
        else:
            self.receive_error(ip_addr, response[1])

    def get_central_device_data(self, data_dictionary, ip_addr):  # Gets central device rssi
        if self.central_device_mac in data_dictionary.keys():  # check if central device was picked up in scan
            central_rssi = data_dictionary[self.central_device_mac][0]
            print(central_rssi)

            # add data to self.rssi_data_obj.device_whereabouts[self.rssi_data_obj.curr] dictionary
            self.rssi_data_obj.device_whereabouts[self.rssi_data_obj.curr][
                self.peripheral_devices[ip_addr]] = central_rssi
            self.gui_object.coordinate_calculator_ready = True  # start the function that calculates the central device coordinates
        else:  # central device not picked up in list
            return

    def communication(self):  # handles communication
        """
                         - network related code will be running in a separate thread/process
                         - gui related code will be running in a separate thread/process
                         - interactions between the network thread and the gui thread should be done using thread-safe mechanisms
        """
        try:
            while True:
                rlist, [], xlist = select.select([self.server_socket], [], [self.server_socket], 0.01)

                if self.server_socket in rlist:
                    # get the ip address of socket who sent me data
                    data, ip_addr = self.server_socket.recvfrom(self.recv_size)  # receive data

                    if ip_addr not in self.peripheral_devices:  # verify the ip address
                        self.verification_list.append(ip_addr)
                        self.verify_connected_sockets(data, ip_addr)

                    elif ip_addr in self.peripheral_devices:  # incoming message from peripheral device
                        self.handle_peripheral_communication(data, ip_addr)

        except KeyboardInterrupt:  # in case server was stopped manually
            print('server manually stopped')

        except Exception as e:
            print(f'exception: {e}')

        finally:  # cleanup - close sockets
            print('ending communication, closing sockets...')

    def start(self):
        while not self.gui_object.server_ready:
            time.sleep(0.01)
        # initialize server socket
        self.server_socket.bind((self.ip_addr, self.port))
        print('server is ready to receive packets')
        self.communication()