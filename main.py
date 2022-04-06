import logging
from multiprocessing import Lock
import threading
import time
import socket
import struct
import json
import sched



if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    Host = "127.0.0.1"
    Port = 9090
    multiCast = ("224.0.0.1",Port)

    activeSockets = []

    

    def Listener(name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((Host,Port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print("Working", data)
                    
                    # conn.sendall(data)


    def Discover():

        s = sched.scheduler(time.time, time.sleep)
        def repeat(sc):
            sendMulticast()
            sc.enter(60,1,repeat, (sc,))
        
        s.enter(60,1,repeat, (s,))
        s.run()

    def tester(name):

        s = sched.scheduler(time.time, time.sleep)
        def repeat(sc):
            print("Working")
            sc.enter(10,1,repeat, (sc,))
        
        s.enter(60,1,repeat, (s,))
        s.run()

    def sendMulticast(message, group):
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.2)

        ttl = struct.pack('b',1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        Jobj = json.dumps({"type":"DISCOVER","time":time.time(),"port":Port})
        sent = sock.sendto(Jobj,multiCast)

            
    DiscoverThread = threading.Thread(target=tester,args=("1"))
    # ListenerThread = threading.Thread(target=Listener,args=("2"))

    DiscoverThread.start()
    Listener("2")