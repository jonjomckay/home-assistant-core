import socket
import threading
from lakeside import device, bulb, switch, lakeside_pb2


class LakesideDevice(device):
    def connect(self):
        """Override the Lakeside connect method, so we don't call update, which can infinite loop"""
        print("connecting")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.address, 55556))
        print("connected")

        if self.keepalive is None:
            self.keepalive = threading.Thread(target=self.ping, args=())
            self.keepalive.daemon = True
            self.keepalive.start()


class LakesideVacuum(LakesideDevice, device):
    def get_status(self):
        packet = lakeside_pb2.T1201Packet()
        packet.sequence = self.get_sequence()
        packet.code = self.code
        packet.switchinfo.type = 1

        return self.send_packet(packet, True)


class LakesideBulb(LakesideDevice, bulb):
    pass


class LakesideSwitch(LakesideDevice, switch):
    pass
