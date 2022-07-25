#!/usr/bin/python
#  Python Imports
# -------------------------------------------------
# from dronekit import connect, VehicleMode, LocationGlobalRelative
import socket
import time
import json
import tqdm
# from gpiozero import RGBLED
# import netifaces as ni
import threading
import requests


class ClientInit:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket()
        # self.vehicle = connect('192.168.255.29:14550', wait_ready=None)
        # self.ip = (ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']).partition('192.168.32.')[-1]
        # self.id = (int((ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr'])[-1])) - 1
        # self.led = RGBLED(21, 20, 22)

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
                t1 = threading.Thread(target=self.telemetry_data())
                t1.start()
                data = self.s.recv(5048576)
                if data[:3].decode('utf-8') == 'arm':
                    alt = int(data[-2:].decode('utf-8'))
                    #t1.start()
                    #self.telemetry_data()
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

                elif data[:4] == 'test':
                    self.led.color = (1, 1, 1)
                else:
                    # self.download(data)
                    t3 = threading.Thread(target=self.download(data))
                    t3.start()
                    time.sleep(5)
                    t3.join()

            except socket.error as msg:

                print(msg, 'Error, GCS disconnected')
                break

    @staticmethod
    def download(data):
        with open('C:/Users/SIKIRU/Desktop/Droneproject/Droneswarm/paths.json', "wb") as f:
            while True:
                bytes_read = data
                if not bytes_read:
                    # nothing is receive
                    #     # file transmitting is done
                    break
                # write to the file the data we just received
                f.write(bytes_read)
            print('success')
        f.close()

    def telemetry_data(self):
        url = "http://192.168.247.223:5003/recv"
        while True:
            GPS = 4  # str(self.vehicle.gps_0)
            battery = "none"  # str(self.vehicle.battery)
            altitude = 5  # str(self.vehicle.location.global_relative_frame.alt)
            system = "standby"  # str(self.vehicle.system_status.state)
            mode = "stabilized"  # str(self.vehicle.mode.name)
            EKF = "false"  # str(self.vehicle.ekf_ok)
            ip = 2  # str(self.ip)
            telemetry_dict = {
                    "id": ip,
                    "GPS": GPS,
                    "Battery": battery,
                    "Altitude": altitude,
                    "System-status": system,
                    "Vehicle-mode": mode,
                    "EKF ok?": EKF
                }
            print(telemetry_dict)
            # packet_str = json.dumps(telemetry_dict)
            send_telemetry = requests.post(url, json=telemetry_dict)
            time.sleep(10)


def create_drone(host, port):
    drone = RunDrone(host, port)
    return drone

# drone = create_drone('127.0.0.1', 9999)
# drone.socket_conn()
# drone.receive_command()
