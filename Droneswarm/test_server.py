import threading
from unittest import TestCase
from server import create_server
from client2 import create_drone


class Test(TestCase):
    """ testing the server against the client"""

    def test_server_host(self):
        gcs = create_server('127.0.0.1', 9999, 1)
        gcs.create_socket()
        self.assertEqual(gcs.host, '127.0.0.1')
        gcs.s.close()

    def test_server_port(self):
        gcs = create_server('127.0.0.1', 9999, 1)
        gcs.create_socket()
        self.assertEqual(gcs.port, 9999)
        gcs.s.close()

    def test_server_client_sockets(self):
        gcs = create_server('127.0.0.1', 9999, 1)
        gcs_thread = threading.Thread(target=gcs.create_socket())
        gcs_thread.start()

        # this is from the client
        client = create_drone('127.0.0.1', 9999)
        client.socket_conn()
        assert gcs.number_of_drones == 1
        assert len(gcs.all_connections) == 0
        client.s.close()
        gcs_thread.join()
        gcs.s.close()
