#  Python Imports
# -------------------------------------------------
import re
import socket
import sys
#  Module Imports
# -------------------------------------------------
from Drone_utils.utils import *


class DroneServer:

    def __init__(self, host: str, port: int, number_of_drones: int):
        self.__host = host
        self.__port = port
        self.__drone_number = number_of_drones
        self.s = socket.socket()
        self.all_connections = []
        self.all_addresses = []
        self.conn_dict = {}

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    @property
    def number_of_drones(self):
        return self.__drone_number

    def create_socket(self):
        """socket connection for main server"""
        try:
            print("Binding the port : " + " " + str(self.__port))
            self.s.bind((self.__host, self.__port))
            self.s.listen(5)

        except socket.error as msg:
            print("Socket creation error:" + str(msg))

    def accept_conn(self):

        while True:
            try:
                conn, address = self.s.accept()
                self.s.setblocking(True)  # prevents timeout

                self.all_connections.append(conn)
                self.all_addresses.append(address)

                print("Connection has been established :" + address[0])
                if len(self.all_addresses) == self.__drone_number:
                    n = 0
                    for i in self.all_addresses:
                        for c in self.all_connections:
                            self.conn_dict[self.all_addresses[n][0]] = self.all_connections[n]
                            n += 1
                            print(self.conn_dict)

                        break
                    break

            except socket.error as msg:
                print("Error accepting connections" + str(msg))


class RunServer(DroneServer):
    """These methods are used to run the server"""

    def send_commands(self):
        # You can only send a command to a connection
        while True:
            cmd = input('Welcome to ALAB firefly show.Start show here: ')
            if cmd == 'quit':
                self.s.close()
                sys.exit()
            elif cmd == 'arm{}'.format(cmd[-2:]):
                for i in self.all_connections:
                    i.send(str.encode(cmd))
            elif cmd == 'test':
                for i in self.all_connections:
                    i.send(str.encode(cmd))
            elif cmd == 'land':
                for i in self.all_connections:
                    i.send(str.encode(cmd))
            elif cmd == 'abort':
                for i in self.all_connections:
                    i.send(str.encode(cmd))
            elif cmd == 'start':
                for i in self.all_connections:
                    i.send(str.encode(cmd))
            elif cmd == 'disarm':
                for i in self.all_connections:
                    i.send(str.encode(cmd))
            elif cmd == 'upload':
                print('Path upload in progress')
                upload_path(self)
            elif cmd:
                self.get_target(cmd)

            else:
                pass
                print('unknown command,no action taken')

    def get_target(self, cmd):
        # use this to select a target drone
        # Welcome to ALAB firefly show.Start show here: select 0 or 1...
        # Press enter to exit from target command section
        try:
            target = cmd.replace('select ', '')  # target = id of drone

            drone_id = int(target)
            conn = self.all_connections[drone_id]
            print("You are now connected to :" + str(self.all_addresses[drone_id][0]))
            print(str(self.all_addresses[drone_id][0]) + ">", end="")
            while True:
                cmd = input('send command to drone:')
                if cmd:
                    conn.send(str.encode(cmd))
                else:
                    break
        except cmd != 'select':
            print("Selection not valid")


def create_server(host, port, number_of_drones):
    gcs_server = RunServer(host, port, number_of_drones)
    return gcs_server


gcs_server = create_server('127.0.0.1', 9999, 1)
gcs_server.create_socket()
gcs_server.accept_conn()
gcs_server.send_commands()
