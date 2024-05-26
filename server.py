import socket
import select
from protocol import Protocol
import json
from customtkinter import *

"""
Central device bluetooth mac address:
- 1C:9D:C2:35:A8:52
"""


class Manager:
    def __init__(self):
        # ServerCommunication
        self.peripheral_device_count = None
        self.server_object = None

        # ModelPlugNPlay
        self.model_address = None
        self.Model = None

    def start(self):
        # Model
        self.model_address = 'Models/test_model.json'
        self.Model = ModelPlugNPlay(self.model_address)
        self.Model.start()

        # ServerCommunication
        self.peripheral_device_count = 1  # amount of peripheral devices required
        self.server_object = ServerCommunication(self.peripheral_device_count, self.Model.mac_list)
        self.server_object.start()


class ServerCommunication:
    def __init__(self, peripheral_count, model):
        # socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create the server socket
        self.ip_addr = '10.100.102.31'
        self.port = 4500

        # Data structures
        self.peripheral_device_count = peripheral_count  # amount of peripheral devices required
        #self.peripheral_devices = []  # list that holds all the peripheral sockets
        self.peripheral_devices = {}  # list that holds all the peripheral sockets and their mac addresses
        self.sockets_dict = {self.server_socket: self.ip_addr}  # holds all the sockets, for the select
        self.verification_list = []  # list of sockets that need to be verified
        self.start_list = []
        self.connected_peripherals = 0

        self.central_device_mac = '1C:9D:C2:35:A8:52'

        # Model
        self.model = model

    def receive_error(self, sock, error):  # if response[0] is false, handle it here
        if error == 'empty':  # socket disconnected
            print(f'{self.sockets_dict[sock]} has disconnected gracefully')
            # handle disconnection ...
            del self.sockets_dict[sock]  # remove from dictionary
            del self.peripheral_devices[sock]  # remove from dictionary
            #TODO handle the rest
        else:  # error with data formatting
            print('error with data formatting, or exception')
            # handle error

    def new_connection(self):
        c_s, addr = self.server_socket.accept()  # accept connection

        # add to appropriate lists/dictionaries
        self.sockets_dict[c_s] = addr
        self.verification_list.append(c_s)

        # start verification process
        query = Protocol.create_msg('what is your mac address')
        c_s.send(query)

    def verify_connected_sockets(self, sock):
        response = Protocol.get_msg(sock)
        if response[0]:
            if response[1] in self.model:  # if mac address is in peripheral_device mac addresses list, allow connection
                #TODO Make sure that the same mac address isn't already connected, and add the mac address to peripheral devices list/dictionary
                print(f'authenticated {self.sockets_dict[sock]}')
                # handle lists and dictionaries
                self.verification_list.remove(sock)
                self.peripheral_devices[sock] = response[1]
                self.connected_peripherals += 1
                # send start message
                sock.send(Protocol.create_msg('start'))
            else:  # if socket is not a peripheral device
                print(f'{self.sockets_dict[sock]} is not a peripheral device')
                self.verification_list.remove(sock)
                del self.sockets_dict[sock]
        else:
            self.receive_error(sock, response[1])

    def handle_peripheral_communication(self, sock):
        print('getting data from peripheral device and checking')
        response = Protocol.get_serialized_data(sock)  # receive data from socket
        if response[0]:
            print(f'got data from {self.sockets_dict[sock]}\n{response[1]}\n')
            if self.connected_peripherals >= 3:
                print('doing things with data')
                self.get_central_device_data(response[1], sock)
            else:
                print('not doing anything with data, not enough peripherals')
        else:
            self.receive_error(sock, response[1])

    def get_central_device_data(self, data_dictionary, sock):  # Gets central device rssi
        if self.central_device_mac in data_dictionary.keys():  # check if central device was picked up in scan
            central_rssi = data_dictionary[self.central_device_mac]
            print(f'most recent rssi recorded by {self.peripheral_devices[sock]}: {central_rssi[0]} dbm')
            #TODO create database that will store each peripheral device mac address, and the most recent rssi captured
            #TODO add data to the database created
        else:
            print('central device not picked up')  # move on

    def socket_in_xlist(self, sock):
        print(f'error with peripheral device: {self.sockets_dict[sock]}')
        # handle disconnected socket

    def communication(self):  # handles communication
        """
                        IMPORTANT!!!
                         - timeout set to none
                         - network related code will be running in a separate thread/process
                         - gui related code will be running in a separate thread/process
                         - interactions between the network thread and the gui thread should be done using thread-safe mechanisms
        """
        try:
            while True:
                rlist, [], xlist = select.select(self.sockets_dict.keys(), [], self.sockets_dict.keys(), 0.01)

                for sock in rlist:
                    if sock == self.server_socket:  # new connection
                        self.new_connection()

                    elif sock in self.verification_list:  # verify connected sockets
                        self.verify_connected_sockets(sock)

                    else:  # incoming message from peripheral device
                        self.handle_peripheral_communication(sock)

                for sock in xlist:
                    self.socket_in_xlist(sock)

        except KeyboardInterrupt:  # in case server was stopped manually
            print('server manually stopped')

        finally:  # cleanup - close sockets
            print('ending communication, closing sockets...')

    def start(self):
        # initialize server socket
        self.server_socket.bind((self.ip_addr, self.port))
        self.server_socket.listen()
        print('server is listening for connections...')

        self.communication()


class ModelPlugNPlay:
    def __init__(self, address):
        # model
        self.model_address = address
        self.edges = []
        self.beacons = []
        self.mac_list = []  # list of all the beacon's wifi mac address

        # map
        self.map_dimensions = None
        self.resized_model_address = 'resized_model.json'
        self.map_canvas = None
        self.canvas_width = None
        self.canvas_height = None

        # info screen
        self.info_screen_dimensions = []  # size of the information screen
        self.info_screen_coordinates = {}  # coordinates that represent where the information screen is located
        self.info_screen_canvas = None  # this is where I will create the information screen

        # window
        self.window_dimensions = []
        self.root = CTk()

    def get_map_size(self):
        """
        - Calculates the map dimensions
        """
        # Initialize the tkinter root window
        root = CTk()

        # Get the screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Create the size of the map
        window_width = screen_width * 0.65
        window_height = screen_height * 0.9
        self.info_screen_dimensions.append(int(screen_width * 0.3))

        return window_width, window_height

    def get_max_coords(self):
        """
        - Using all the edges, this function returns the biggest x value and the biggest y value
        - The coordinates that are returned represent the maximum coordinates of the model
        """
        max_coordinates = [0, 0]
        for e in self.edges:
            start = e['start']
            end = e['end']
            for i in range(0, 2):
                if start[i] > max_coordinates[i]:
                    max_coordinates[i] = start[i]
                if end[i] > max_coordinates[i]:
                    max_coordinates[i] = end[i]
        return max_coordinates

    def create_map_size(self, orig_coords, model_coords):
        """
        - function gets the original map coordinates, and the maximum model coordinates
        - using the model width ratio, the function resizes the original map so that it has the same width ratio as the
          model
        """
        orig_ratio = orig_coords[0] / orig_coords[1]
        model_ratio = model_coords[0] / model_coords[1]

        if orig_ratio > model_ratio:  # if the original map is wider than the model, we have to make the original ratio slimmer
            new_height = orig_coords[1]  # height stays the same
            new_width = min(new_height / model_ratio, new_height * model_ratio)
        else:  # if the model is wider than the original map
            new_width = orig_coords[0]  # width stays the same
            new_height = min(new_width / model_ratio, new_width * model_ratio)  # height gets smaller
        new_ratio = new_width / model_coords[
            0]  # multiply each edge/beacon coordinate by this number to get the new coordinates
        self.map_dimensions = (int(new_width), int(new_height))
        return new_ratio

    def model_to_map(self, ratio):
        """
        - function gets the ratio between the model and the map
        - function changes the coordinates of the edges and beacons to fit the map, using the ratio
        """
        # using the ratio, create the new coordinates
        new_edges = []
        for edge in self.edges:
            edge['start'] = [int(num * ratio) for num in edge['start']]
            edge['end'] = [int(num * ratio) for num in edge['end']]
            new_edges.append(edge)
        self.edges = new_edges

        new_beacons = []
        for beacon in self.beacons:
            beacon['coordinates'] = [int(num * ratio) for num in beacon['coordinates']]
            new_beacons.append(beacon)
        self.beacons = new_beacons

        # create resized_model.json file, using new_edges and new_beacons lists
        with open('resized_model.json', 'w') as file:
            json.dump({'edges': self.edges, 'beacons': self.beacons}, file, indent=4)

    def initialize_map(self):
        # extract edges and beacons from model
        with open(self.model_address, 'r') as model:
            data = json.load(model)
        self.edges = data['edges']
        self.beacons = data['beacons']
        self.mac_list = [beacon['mac_address'] for beacon in self.beacons]

        width, height = self.get_map_size()
        print(width, height)
        max_coordinates = self.get_max_coords()
        print(max_coordinates)
        ratio = self.create_map_size((width, height), max_coordinates)
        print(f'ratio: {ratio}')
        self.model_to_map(ratio)
        print(f'map dimensions: {self.map_dimensions}')

    def calculate_window_dimensions(self):
        """
        - calculates the dimensions of the information screen, and the total window
        - the information screen has the same height as the map screen, but a different width
        - give the window a title, and dimensions
        """
        height = self.map_dimensions[1]  # stays the same height
        self.info_screen_dimensions.append(height)
        self.window_dimensions = [self.info_screen_dimensions[0] + self.map_dimensions[0], height]
        print(f'window dimensions: {self.window_dimensions}')

    def initialize_window(self):
        """
        - set the window title, size, and theme
        - create a canvas for the map, and place it, and create a the info screen and place it
        """
        self.root.title('Main Screen')
        self.root.geometry(f'{self.window_dimensions[0]}x{self.window_dimensions[1]}')
        self.root.resizable(False, False)
        set_default_color_theme('dark-blue')

        # initialize map canvas, that will fit the maps portion of the window
        self.map_canvas = CTkCanvas(self.root, width=self.map_dimensions[0], height=self.map_dimensions[1])
        self.map_canvas.pack(side='left', fill='both', expand=True)

        # initialize info screen canvas, that will fit the info screen's portion of the window
        self.info_screen_canvas = CTkCanvas(self.root, width=self.info_screen_dimensions[0], height=self.info_screen_dimensions[1], bg='#95036d')
        self.info_screen_canvas.pack(side='right', fill='both', expand=True)

        # update both canvases
        self.map_canvas.update()
        self.info_screen_canvas.update()

        # Get the initial canvas size
        self.canvas_width = self.map_canvas.winfo_width()
        self.canvas_height = self.map_canvas.winfo_height()
        print(f'map canvas dimensions: {self.canvas_width}x{self.canvas_height}')

    def resize_model_to_canvas(self):
        """
        - according to the canvas height and width, change all the coordinates of the edges, and beacons, so that the
          scale doesn't change
        """
        new_edges = []
        for edge in self.edges:
            for i in range(0, 2):
                if i == 0:
                    word = 'start'
                else:
                    word = 'end'
                edge[word][0], edge[word][1] = (edge[word][0] / self.map_dimensions[0]) * self.canvas_width, (
                            edge[word][1] / self.map_dimensions[1]) * self.canvas_height
            new_edges.append(edge)

        self.edges = new_edges

        new_beacons = []
        for beacon in self.beacons:
            beacon['coordinates'][0], beacon['coordinates'][1] = (beacon['coordinates'][0] / self.map_dimensions[
                0]) * self.canvas_width, (beacon['coordinates'][1] / self.map_dimensions[1]) * self.canvas_height
            new_beacons.append(beacon)

        self.beacons = new_beacons

        # create resized_model.json file, using new_edges and new_beacons lists
        with open('resized_model.json', 'w') as file:
            json.dump({'edges': self.edges, 'beacons': self.beacons}, file, indent=4)

    def draw_edges(self):
        """
        - draw edges on screen
        """
        for edge in self.edges:
            x1, y1 = edge['start'][0], edge['start'][1]
            x2, y2 = edge['end'][0], edge['end'][1]
            self.map_canvas.create_line(x1, y1, x2, y2, fill='black', width=5)

    def draw_circle(self, x, y, r, fill_color):
        """
        - this function draws a circle according to the parameters given
        """
        self.map_canvas.create_oval(x - r, y - r, x + r, y + r, width=2, fill=fill_color)

    def draw_beacons(self):
        """
        - draw the beacons on the screen as circles
        - beacons are initially white, and only the 3 closest beacons to the central device will be in red
        """
        for beacon in self.beacons:
            x, y = beacon['coordinates'][0], beacon['coordinates'][1]
            r = 15  # set radius size
            self.draw_circle(x, y, r, 'white')

    def draw_info_screen(self):
        """
        - draw the initial info screen
        """
        return

    def create_window(self):
        self.calculate_window_dimensions()
        self.initialize_window()
        self.resize_model_to_canvas()
        self.draw_edges()
        self.draw_beacons()
        self.draw_info_screen()

    def start(self):
        # onboard model, and modify fit computer
        self.initialize_map()

        # create window - place beacons, edges, and add divider between map and info screens
        self.create_window()

        # test it out
        self.root.mainloop()


def main():
    # Manager
    manager = Manager()
    manager.start()


if __name__ == '__main__':
    main()
