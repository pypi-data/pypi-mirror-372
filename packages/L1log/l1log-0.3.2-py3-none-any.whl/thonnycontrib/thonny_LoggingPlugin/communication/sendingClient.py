import requests

class SendingClient():
    """
    This class is used to send data to the LRS API
    For the moment the only thing that can be send is statements, wich are converted by this class from data dicts
    """

    def __init__(self,server_addr):
        self.server_addr = server_addr

    def send(self,data,server_path):
        """
        Try to send the data to the LRS and catch the exceptions

        Args : 
            data (object: dict()): the data in the xAPI format
            server_path (str) the server address with the right folder

        Return :
            The API's response
        """
        response = requests.post(self.server_addr+server_path,json = data, timeout=0.25)
        return response


    def change_server_addr(self,server_addr):
        """
        Change the class attribute server_addr

        Args :
            server_addr (str) the server address
        """
        self.server_addr = server_addr