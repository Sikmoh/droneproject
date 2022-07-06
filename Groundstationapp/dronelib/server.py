#  Python Imports
# -------------------------------------------------
import socket
import tqdm
import os


#  Module Imports
# -------------------------------------------------

class ServerInit:

    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.s = socket.socket()
        self.all_connections = []
        self.all_addresses = []

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port

    def create_socket(self):
        """socket connection for main server"""
        try:
            print("Binding the port : " + " " + str(self.__port))
            self.s.bind((self.__host, self.__port))
            self.s.listen(5)

        except socket.error as msg:
            print("Socket creation error:" + str(msg))

    def accept_conn(self, drone_number: int):
        """this method creates a connection object for
        each drone that connects to the socket """
        while True:
            try:
                conn, address = self.s.accept()
                self.s.setblocking(True)  # prevents timeout

                self.all_connections.append(conn)
                self.all_addresses.append(address)

                print("Connection has been established :" + address[0])
                if len(self.all_addresses) == drone_number:
                    break

            except socket.error as msg:
                print("Error accepting connections" + str(msg))


class RunServer(ServerInit):
    """These methods are used to run the server"""

    def send_commands(self, cmd):
        # You can only send a command to a connection
        print(cmd)
        while True:
            if cmd == 'quit':
                self.s.close()
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
            else:
                pass
            break

    def get_target(self, number, cmd):
        # use this to select a target drone
        # Welcome to ALAB firefly show.Start show here: select 0 or 1...
        # Press enter to exit from target command section
        try:
            drone_id = int(number)
            conn = self.all_connections[drone_id]
            print("You are now connected to :" + str(self.all_addresses[drone_id][0]))
            # print(str(self.all_addresses[drone_id][0]) + ">", end="")
            conn.send(str.encode(cmd))
            print('sent')
            print(cmd)

        except cmd != 'land' or 'disarm' or 'return':
            print("Selection not valid")

    def upload_path(self):
        BUFFER_SIZE = 5048576  # 5MB
        filename = "C:/Users/SIKIRU/Desktop/Droneproject/Groundstationapp/uploads/paths.json"
        filesize = os.path.getsize(filename)
        for i in self.all_connections:
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "rb") as f:
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transmission in
                    # busy networks
                    i.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))

            f.close()


def create_server(host, port):
    gcs_server = RunServer(host, port)
    return gcs_server

# code below is executed in a different script, its just here for reference
# gcs_server = create_server('127.0.0.1', 9999, 1)
# gcs_server.create_socket()
# gcs_server.accept_conn()
# gcs_server.send_commands()
