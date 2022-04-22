import atexit
import logging
from multiprocessing import Lock 
import threading
import time
import socket
import struct
import json

from ledger import Ledger
    
def Listener(threadName):
    global ISRUNNING
    print("Listerner() running")

    DiscoverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    DiscoverSocket.bind(("127.0.0.1",Port))
    activeSockets.append(DiscoverSocket)

    while ISRUNNING:
        
        packet, (b, a) = DiscoverSocket.recvfrom(4096)
        packet = json.loads(packet.decode)
        print("Discover:", b)

        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.bind((Host,Port))
        #     s.listen()
        #     activeSockets.append(s)
        #     conn, addr = s.accept()
        #     with conn:
        #         print(f"Connected by {addr}")
        #         while True:
        #             data = conn.recv(1024)
        #             if not data:
        #                 break
        #             print("Receaving data:", data)
                    
        #             # conn.sendall(data) # why??
        # s.close()


def Discover(threadName):
    print("Discover() running")

    DiscoverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    DiscoverSock.settimeout(0.2)

    ttl = struct.pack('b',1)
    DiscoverSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    activeSockets.append(DiscoverSock)

    def repeat():
        sendMulticast(DiscoverSock)
        t = threading.Timer(10.0,repeat)
        t.start()
    
    t = threading.Timer(10.0,repeat)
    t.start()

def sendMulticast(sock):
    Jobj = json.dumps({"type":"DISCOVER","time":int(time.time()),"port":Port})
    Jobj = bytes(Jobj, "utf-8")
    sent = sock.sendto(Jobj,multiCast)
    print("Sending DISCOVER",sent)

def exit_handler():
    global ISRUNNING 
    ISRUNNING= False

    for sock in activeSockets:
        sock.close()

    for a in threading.enumerate():
        if a != threading.currentThread():
            a.join()


def on_press(key):
    try:
        k = key.char
    except:
        k = key.name
    if k == "C":
        return False
        
if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    Host = "127.0.0.1"
    Port = 9090
    multiCast = ("224.0.0.1",Port)
    ISRUNNING = True
    ledger = Ledger()
    ledger.add("killer","temp")
    activeSockets = []

    atexit.register(exit_handler)


    DiscoverThread = threading.Thread(target=Discover,args=("1"))
    # ListenerThread = threading.Thread(target=Listener,args=("2")) #the main thread

    DiscoverThread.start()
    Listener("2")