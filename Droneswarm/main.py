#  Module Imports
from server import create_server


#  Setup
def create_connection(host, port, number):
    """
           Function to run the server

       """
    gcs_server = create_server(host, port, number)
    gcs_server.create_socket()
    gcs_server.accept_conn()
    gcs_server.send_commands()


if __name__ == '__main__':
    create_connection('192.168.255.223', 9999, 1)
