import socket
import threading
from unittest import TestCase


from server import create_server
from client2 import create_drone


class Test(TestCase):
    """ testing the server against the client"""

    def test_server_client_sockets(self):
        # run the server in the background to mimic two different platforms
        gcs = create_server('127.0.0.1', 9999, 1)
        gcs_thread = threading.Thread(target=gcs.create_socket())
        gcs_thread.start()

        # this is from the client
        client = create_drone('127.0.0.1', 9999)
        client.socket_conn()
        client.s.close()

        self.assertRaises(socket.error)
        gcs_thread.join()
        gcs.s.close()
