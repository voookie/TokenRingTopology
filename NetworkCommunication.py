import socket


class UDPCommunicationProcessor:

    def __init__(self, ip, port, encoding="utf-8"):
        self.encoding = encoding
        self.in_socket = self.set_in_socket(ip, port)
        self.out_socket = self.set_out_socket()

    @staticmethod
    def set_in_socket(ip, port):
        in_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        in_socket.bind((ip, int(port)))
        return in_socket

    @staticmethod
    def set_out_socket():
        out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return out_socket

    def sent_token(self, msg, next_client_ip, next_client_port):
        token = bytes(msg, self.encoding)
        ip_port = (next_client_ip, next_client_port)
        self.out_socket.sendto(token, ip_port)

    def recv_token(self):
        return str(self.in_socket.recvfrom(1024)[0], self.encoding)


class TCPCommunicationProcessor:

    def __init__(self, ip, port, encoding="utf-8"):
        self.encoding = encoding
        self.in_socket = self.set_in_socket(ip, port)
        self.out_socket = self.set_out_socket()

    @staticmethod
    def set_in_socket(ip, port):
        in_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        in_socket.bind((ip, int(port)))
        in_socket.listen(5)
        return in_socket

    @staticmethod
    def set_out_socket():
        out_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return out_socket

    def sent_token(self, msg, next_client_ip, next_client_port):
        token = bytes(msg, self.encoding)
        ip_port = (next_client_ip, next_client_port)
        self.out_socket = self.set_out_socket()
        self.out_socket.connect(ip_port)
        self.out_socket.send(token)
        self.out_socket.close()

    def recv_token(self):
        connection, client_address = self.in_socket.accept()
        return str(connection.recv(1024), self.encoding)


def udp_multicast(msg, logger_ip, logger_port, encoding="utf-8"):
    out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    token = bytes(msg, encoding)
    ip_port = (logger_ip, logger_port)
    out_socket.sendto(token, ip_port)
