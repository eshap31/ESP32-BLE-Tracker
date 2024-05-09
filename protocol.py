import json
import os


class Protocol:
    LENGTH_FIELD_SIZE = 5

    @staticmethod
    def create_msg(data):
        """
        Create a valid protocol message, with length field
        """
        length = str(len(str(data)))
        zfill_length = length.zfill(Protocol.LENGTH_FIELD_SIZE)
        message = zfill_length + str(data)
        return message.encode()

    @staticmethod
    def create_serialized_data(dictionary):
        """
        serializes the dictionary into json format, then calls the Protocol.create_message() func to format the data
        for sending
        """
        return Protocol.create_msg(json.dumps(dictionary))

    @staticmethod
    def get_msg(my_client):
        """
        Extract message from protocol, without the length field
        If length field does not include a number, returns False, "Error"
        :rtype: (bool, str)
        """
        print('in get_msg')
        len_word = ''
        for i in range(0, Protocol.LENGTH_FIELD_SIZE):
            print('before receiving 1 byte')
            len_word += my_client.recv(1).decode()
            print('received 1 byte from socket')
            if len_word is None:
                return False, 'Error'
            print(f"in length: {len_word}")

        if len_word.isnumeric():
            read_length = int(len_word)
            message = my_client.recv(read_length).decode()
            print(f"in data: {message}")
            print(f'length received: {len(message)}')
            while len(message) < read_length:
                message += (my_client.recv(read_length - len(message)).decode())
                print(f"in data: {message}")

            print(len(message) == read_length)
            return True, message
        else:
            return False, "Error"

    @staticmethod
    def get_serialized_data(my_client):
        print('getting serialized data')
        data = Protocol.get_msg(my_client)
        print('checking serialized data in get_serialized_data')
        if data[0]:
            try:
                print('getting data in serialized data')
                data = json.loads(data[1])
                return True, data
            except json.JSONDecodeError as e:
                print("JSON decode error:", e, data)
        else:
            return False, 'Error'
