import socket
import select
from protocol import Protocol

"""
ESP32 mac addresses:
- 30:30:F9:77:0E:42
"""


class Manager:
    def __init__(self):
        print('hello world')


class ServerCommunication:
    def __init__(self, peripheral_count):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create the server socket
        self.ip_addr = '172.16.1.118'
        self.port = 4500

        self.peripheral_device_count = peripheral_count  # amount of peripheral devices required
        self.peripheral_devices = []  # list that holds all the peripheral sockets
        self.sockets_dict = {self.server_socket: self.ip_addr}  # list of all the sockets, for the select
        self.verification_list = []  # list of sockets that need to be verified
        self.start_list = []
        self.connected_peripherals = 0

        self.central_device_mac = '1C:9D:C2:35:A8:52'

    def receive_error(self, sock, error):  # if response[0] is false, handle it here
        if error == 'empty':  # socket disconnected
            print(f'{self.sockets_dict[sock]} has disconnected gracefully')
            # handle disconnection ...
        else:  # error with data formatting
            print('error with data formatting, or exception')
            # handle error

    def new_connection(self):
        c_s, addr = self.server_socket.accept()  # accept connection

        # add to appropriate lists/dictionaries
        self.sockets_dict[c_s] = addr
        self.verification_list.append(c_s)

        # start verification process
        query = Protocol.create_msg('what is your job')
        c_s.send(query)

    def verify_connected_sockets(self, sock):
        response = Protocol.get_msg(sock)
        if response[0]:
            if response[1] == 'peripheral device':  # if socket is a peripheral device
                print(f'authenticated {self.sockets_dict[sock]}')
                # handle lists and dictionaries
                self.verification_list.remove(sock)
                self.peripheral_devices.append(sock)
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
            else:
                print('not doing anything with data')
        else:
            self.receive_error(sock, response[1])

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


def main():
    # ServerCommunication

    peripheral_device_count = 1  # amount of peripheral devices required
    server_object = ServerCommunication(peripheral_device_count)
    server_object.start()


if __name__ == '__main__':
    main()
