import atexit
import logging
from multiprocessing import Lock 
import threading
import time
import socket
import struct
import json

from ledger import Ledger
    

Host = "127.0.0.1"
PORT = 9090
MULTI_CAST = ("224.0.0.1",PORT)
ISRUNNING = True
LEDGER = Ledger()
ACTIVESOCKETS = []
TIMEOUT = 0.02

def ReadDiscover(threadName):
    global ISRUNNING
    print("ReadDiscover() running")

    DiscoverListener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    DiscoverListener.bind(('',PORT))
    ACTIVESOCKETS.append(DiscoverListener)

    while ISRUNNING:
        
        try:
            data, (ip, port) = DiscoverListener.recvfrom(4096)
        except socket.timeout as e:
            continue 
        print("Receaved Discover")
        try:
            data = json.loads(data.decode())
            print("M:", data, "from", ip)
        except Exception as e:
            print("Error:", e)

        LEDGER.add(ip,ip)


        # HANDLE the HELLOW responce 


        

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


def SendDiscover(threadName):
    print("Discover() running")

    DiscoverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    DiscoverSock.settimeout(0.2)

    ttl = struct.pack('b',1)
    DiscoverSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    ACTIVESOCKETS.append(DiscoverSock)

    def repeat():
        sendMulticast(DiscoverSock)
        t = threading.Timer(10.0,repeat)
        t.start()
    
    t = threading.Timer(10.0,repeat)
    t.start()

def sendMulticast(sock):
    Jobj = json.dumps({"type":"DISCOVER","time":int(time.time()),"port":PORT})
    # Jobj = bytes(Jobj, "utf-8")
    
    sent = sock.sendto(Jobj.encode(),MULTI_CAST)
    print("Sending DISCOVER",sent)

def SendHello():

    sendIP = host
    msg = {"type":"HELLO","port":PORT,"clients":getClients()}
    msg = json.dumps(msg)
    helloSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    helloSocket.connect((sendIP, PORT))
    helloSocket.send(msg.encode())

def getClients():
    keys = LEDGER.keys()
    rtn = []
    for key in keys:
        rtn.append(key)
    return rtn

def ReadHello():
    pass



def exit_handler():
    global ISRUNNING 
    ISRUNNING = False

    for sock in ACTIVESOCKETS:
        sock.close()

    for a in threading.enumerate():
        if a != threading.currentThread():
            a.join()

        
if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    

    atexit.register(exit_handler)


    DiscoverThread = threading.Thread(target=SendDiscover,args=("1"))
    # ListenerThread = threading.Thread(target=Listener,args=("2")) #the main thread

    DiscoverThread.start()
    ReadDiscover("2")