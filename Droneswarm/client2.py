#!/usr/bin/python
#  Python Imports
# -------------------------------------------------
#from dronekit import connect, VehicleMode, LocationGlobalRelative
import socket
import time
import json
import tqdm
#from gpiozero import RGBLED
#import netifaces as ni
import threading


class ClientInit:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket()
        #self.vehicle = connect('192.168.255.29:14550', wait_ready=None)
        #self.id = (int((ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr'])[-1])) - 1
        #self.led = RGBLED(21, 20, 22)

    def socket_conn(self):
        # connect to socket opened on host and port
        self.s.connect((self.host, self.port))
        # self.led.color = (1, 1, 1)
        print("connection successful, ready for takeoff")


class RunDrone(ClientInit):

    def path(self):
        with open("/downs/paths.json", 'r') as f:
            data = json.loads(f.read())
            loop_number = 1
            while loop_number < len(data):
                cord = data[str(loop_number)]
                coord_dict = cord[self.id]
                x, y, z, r, g, b = coord_dict['lat'], coord_dict['lon'], coord_dict['alt'], float(
                    coord_dict['r']), float(coord_dict['g']), float(coord_dict['b'])

                self.led.color = (r, g, b)
                destination = LocationGlobalRelative(x, y, z)
                self.vehicle.simple_goto(destination)
                print(x, y, z, r, g, b)
                time.sleep(0.25)
                loop_number += 1

    def arm_and_takeoff(self, target_altitude):
        while not self.vehicle.is_armable:
            print("WAITING FOR VEHICLE TO BECOME ARMABLE")
            time.sleep(1)
            break

        # SWITCHING VEHICLE MODE TO "GUIDED"
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True
        time.sleep(3)
        # confirm vehicle armed before attempting to takeoff

        while not self.vehicle.armed:
            print("waiting for arming...")
            time.sleep(1)

        # COMMAND FOR ACTUAL TAKEOFF
        self.vehicle.simple_takeoff(target_altitude)

        while True:
            # print("CURRENT ALTITUDE IS : %s" % vehicle.location.global_relative_frame.alt)
            if self.vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
                break

    def receive_command(self):

        while True:
            try:
                #t1 = threading.Thread(target=self.telemetry_data())
                #t1.start()
                data = self.s.recv(8192)
                if data[:3].decode("utf-8") == 'arm':
                    alt = int(data[-2:].decode("utf-8"))
                    self.arm_and_takeoff(alt)
                    self.led.color = (0, 1, 0)

                    while True:
                        data = self.s.recv(8192)
                        coord = data.decode('utf-8')
                        if coord == 'abort':
                            self.vehicle.mode = VehicleMode('RTL')
                        elif coord == 'land':
                            self.vehicle.mode = VehicleMode('LAND')
                        elif coord == 'disarm':
                            self.vehicle.mode = VehicleMode('DISARM')
                        elif coord == 'start':
                            t2 = threading.Thread(target=self.path())
                            t2.start()
                        else:
                            pass

                elif data[:4].decode("utf-8") == 'test':
                    self.led.color = (1, 1, 1)
                else:
                    pass

            except socket.error as msg:
                print(msg, 'Error, GCS disconnected')
                break

    def download(self):
        SEPARATOR = "<SEPARATOR>"
        BUFFER_SIZE = 1048576  # 1MB
        data = self.s.recv(BUFFER_SIZE).decode()
        file, size = data.split(SEPARATOR)
        filesize = int(size)
        progress = tqdm.tqdm(range(filesize), f"Receiving {file}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(file, "wb") as f:
            while True:
                # read 1024 bytes from the socket (receive)

                bytes_read = self.s.recv(BUFFER_SIZE)
                if not bytes_read:
                    #     # nothing is receive
                    #     # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

        f.close()
        s.close()

    # def telemetry_data(self):
    #     url = "http://127.0.0.1:5003/recv"
    #     while True:
    #         telemetry_dict = {
    #             "id": self.id,
    #             "GPS": self.vehicle.gps_0,
    #             "Battery": self.vehicle.battery,
    #             "Attitude": self.vehicle.attitude,
    #             "System-status": self.vehicle.system_status.state,
    #             "Vehicle-mode": self.vehicle.mode.name,
    #             "EKF ok?": self.vehicle.ekf_ok
    #         }
    #         packet_str = json.dumps(telemetry_dict)
    #         send_telemetry = requests.post(url, json=packet_str)
    #         time.sleep(5)


def create_drone(host, port):
    drone = RunDrone(host, port)
    return drone

# drone = create_drone('127.0.0.1', 9999)
# drone.socket_conn()
# drone.receive_command()
