import logging
import threading
import time
import socket
import struct
import json
import signal

from ledger import Ledger
    

HOST = "127.0.0.1"
PORT = 9090
MULTI_CAST = ("224.0.0.1",PORT)
ISRUNNING = True
LEDGER = Ledger()
ACTIVESOCKETS = []
TIMEOUT = 0.02

def ReadDiscover(threadName):
    global ISRUNNING, LEDGER, ACTIVESOCKETS

    # Set up UDP Discover Socket for Reading Discovers
    DiscoverListener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    DiscoverListener.bind(('',PORT))
    ACTIVESOCKETS.append(DiscoverListener)

    # run in a while loop so it can happen again
    while ISRUNNING:
        
        try:
            # wait for someone to send a discover
            data, (ip, port) = DiscoverListener.recvfrom(4096)
            data = json.loads(data.decode())
            # print("M(D):", data, "from", ip)
            LEDGER.add(ip,ip,5)

            # send a hello message back to discover sender in a new thread
            HelloThread = threading.Thread(target=SendHello,args=[ip])
            HelloThread.start()
        except socket.timeout as e:
            continue 
        except Exception as e:
            pass



def SendDiscover(threadName):
    global ACTIVESOCKETS

    # Set up a socket to send discover messages
    DiscoverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    DiscoverSock.settimeout(0.2)

    # set up destination to be a multicast
    ttl = struct.pack('b',1)
    DiscoverSock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    ACTIVESOCKETS.append(DiscoverSock)

    # repeat ever minute
    def repeat():
        # send multicast
        sendMulticast(DiscoverSock) 
        # update the ledger times
        LEDGER.onMin()

        # repeat in a minute
        t = threading.Timer(60.0,repeat)
        t.start()
    
    repeat()


def sendMulticast(sock):
    Jobj = json.dumps({"type":"DISCOVER","time":int(time.time()),"port":PORT})
    try:
        sock.sendto(Jobj.encode(),MULTI_CAST)
    except socket.error as e:
        pass
    except Exception as e:
        pass


def SendHello(targetIP):
    global ACTIVESOCKETS
    sendIP = targetIP
    
    # create the message
    msg = {"type":"HELLO","port":PORT,"clients":getClients()}
    msg = json.dumps(msg)

    # create the TCP socket
    helloSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect socket and send message
        helloSocket.connect((sendIP, PORT))
        helloSocket.send(msg.encode())
    except socket.error as e:
        pass
    except Exception as e:
        pass
    helloSocket.close()


def getClients():
    global LEDGER
    # get the clients in Ledger
    keys = LEDGER.readKeys()
    rtn = []
    for key in keys:
        rtn.append(key)
    return rtn


def ReadHello():
    global ISRUNNING, ACTIVESOCKETS

    # Set up Hello listener socket
    HelloListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HelloListener.bind(('',PORT))
    HelloListener.listen(10)
    ACTIVESOCKETS.append(HelloListener)

    while ISRUNNING:
        
        try:         
            # accept a conection and handle the connected socket to a new thread
            sock, (ip, port) = HelloListener.accept()
            addClientThread = threading.Thread(target=addClients,args=(sock,ip))
            addClientThread.start()
        except socket.timeout as e:
            continue 
        except Exception as e:
            pass

    HelloListener.close()


def addClients(sock,ip):
    global LEDGER

    # handle hello socket connection

    try:
        data = sock.recv(4096)
        sock.close()
        data = json.loads(data.decode())
        # add clients to ledger
        cls = data['clients']
        for cl in cls:
            LEDGER.add(cl,ip)

        # print("M(H):", data, "from", ip)
    except Exception as e:
        pass



def exit_handler(num=0,num2=0):
    print(" Exit_Handler() Running Give it a Sec")
    global ISRUNNING, ACTIVESOCKETS
    ISRUNNING = False


    # Send an empty UDP packet to myself to close the UDP socket
    msg = ""
    blankDiscover = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    blankDiscover.connect((HOST, PORT))
    blankDiscover.send(msg.encode())
    blankDiscover.close()

    for sock in ACTIVESOCKETS:
        try:
            # handle windows/LINUX
            sock.shutdown(1)
        except socket.error as e:
            pass
        # close all sockets
        sock.close()

    for a in threading.enumerate():
        # merge all threads into current
        if a != threading.currentThread():
            if isinstance(a,threading.Timer):
                a.cancel()
            a.join()

def handleInput():
    global ISRUNNING

    while ISRUNNING:
        inp = input()

        # take an input display ledger if "ledger"
        # quit program if "quit"
        if inp == "ledger":
            print(LEDGER.print())
        if str.lower(inp) == "quit":
            exit_handler()
            quit()

        
if __name__ == "__main__":

    signal.signal(signal.SIGINT,exit_handler)

    # set up main threads
    DiscoverThread = threading.Thread(target=SendDiscover,args=("1"))
    HelloThread = threading.Thread(target=ReadHello)
    InputThread = threading.Thread(target=handleInput)

    # start main threads
    DiscoverThread.start()
    HelloThread.start()
    InputThread.start()
    ReadDiscover("2")