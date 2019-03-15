import json
import random
import string
import sys
import time

from NetworkCommunication import *


class Client:
    def __init__(self, protocol, name=None, ip='', port=None, next_client_ip=None,
                 next_client_port=None, has_token=False, ):
        self.has_token = int(has_token)
        self.next_client_port = next_client_port
        self.next_client_ip = next_client_ip
        self.port = int(port)
        self.name = name
        self.ip = ip
        if protocol == "tcp":
            self.networkProcessor = TCPCommunicationProcessor(ip, port)
        else:
            self.networkProcessor = UDPCommunicationProcessor(ip, port)

    def process_network(self):
        if self.has_token:
            self.sent_message()
        else:
            print("{}> Sending token ring connect".format(self.name))
            self.sent_new_client()
        while True:
            token_string = self.networkProcessor.recv_token()
            token_json = json.loads(token_string.replace("\'", "\""))
            print("{}> Debug token received print {}".format(self.name, str(token_json)))
            udp_multicast(token_string, "", 9100)
            time.sleep(1)
            if token_json["token_type"] == "msg":
                if self.is_receiver(token_json):
                    print("{}> Got message: {}".format(self.name, str(token_json["msg"])))
                    print("{}> Sending confirmation of receivement".format(self.name))
                    self.send_confirmation(token_json)
                elif self.is_sender(token_json):
                    print("{}> Message receiver not found".format(self.name))
                    print("{}> Skipping tour after receiving msg".format(self.name))
                    self.sent_empty()
                else:
                    self.networkProcessor.sent_token(str(token_json),
                                                     self.next_client_ip, int(self.next_client_port))
            if token_json["token_type"] == "confirmation":
                if self.is_receiver(token_json):
                    print("{}> Got confirmation from receiver".format(self.name))
                    print("{}> Skipping tour after receiving msg".format(self.name))
                    self.sent_empty()
                elif self.is_sender(token_json):
                    print("{}> Confirmation receiver not found".format(self.name))
                    print("{}> Skipping tour after receiving msg".format(self.name))
                    self.sent_empty()
                else:
                    self.networkProcessor.sent_token(str(token_json),
                                                     self.next_client_ip, int(self.next_client_port))
            if token_json["token_type"] == "new_client":
                if self.next_client_port == token_json["next_client_port"] \
                        and self.next_client_ip == token_json["next_client_ip"]:
                    self.next_client_port = token_json["port"]
                    self.next_client_ip = token_json["ip"]
                else:
                    self.networkProcessor.sent_token(str(token_json),
                                                     self.next_client_ip, int(self.next_client_port))
            if token_json["token_type"] == "empty":
                print("{}> Previous Client skipped a tour".format(self.name))
                self.sent_message()

    def is_sender(self, token):
        return token["sender"] == self.name

    def is_receiver(self, token):
        return token["receiver"] == self.name

    def sent_message(self):
        receiver = input("{}> Send message to: ".format(self.name))
        random_msg = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        print("{}> [With generated message: {}]".format(self.name, random_msg))
        token_json = self.create_json_msg(receiver, random_msg)
        self.networkProcessor.sent_token(str(token_json), self.next_client_ip, int(self.next_client_port))
        print("{}> Message sent".format(self.name))

    def sent_empty(self):
        self.networkProcessor.sent_token(str(self.create_json_empty()), self.next_client_ip, int(self.next_client_port))

    def send_confirmation(self, token_json):
        self.networkProcessor.sent_token(str(self.create_json_confirmation(token_json["sender"])),
                                         self.next_client_ip, int(self.next_client_port))

    def sent_new_client(self):
        self.networkProcessor.sent_token(str(self.create_json_new_client()),
                                         self.next_client_ip, int(self.next_client_port))

    def create_json_msg(self, receiver, msg):
        return {"token_type": "msg", "sender": self.name, "receiver": receiver, "msg": msg}

    def create_json_confirmation(self, receiver):
        return {"token_type": "confirmation", "sender": self.name, "receiver": receiver}

    def create_json_empty(self):
        return {"token_type": "empty"}

    def create_json_new_client(self):
        return {"token_type": "new_client", "ip": self.ip, "port": self.port,
                "next_client_port": self.next_client_port, "next_client_ip": self.next_client_ip}


def main():
    args = [arg for arg in sys.argv[1:]]
    client = Client(*args)
    client.process_network()


if __name__ == '__main__':
    main()
