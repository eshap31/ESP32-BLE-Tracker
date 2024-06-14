import json

class Protocol:

    @staticmethod
    def create_msg(data):
        """
        Create a valid protocol message
        """
        return (str(data)).encode()

    @staticmethod
    def create_serialized_data(dictionary):
        """
        serializes the dictionary into json format, then calls the Protocol.create_message() func to format the data
        for sending
        """
        return Protocol.create_msg(json.dumps(dictionary))

    @staticmethod
    def get_msg(data):
        if len(data) == 0:
            return False, 'empty'
        elif len(data) > 0:
            data = data.decode()
            return True, data
        else:
            return False, 'error'

    @staticmethod
    def get_serialized_data(recvd_data):
        data = Protocol.get_msg(recvd_data)
        if data[0]:
            try:
                data = json.loads(data[1])
                return True, data
            except json.JSONDecodeError as e:
                print("JSON decode error:", e, data)
        elif data[1] == 'empty':  # data is empty
            return False, 'empty'
        else:
            return False, 'Error'


