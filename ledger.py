from threading import Semaphore, Lock

READERS = 8
Sem = Semaphore(READERS)
Mtx = Lock()


class Ledger:

    """
            0              1                 2
    [ [IP Address] [IP Connection] [Min to Experation] ]
    [ [          ] [             ] [                 ] ]
    ...
    """

    def add(self, addy, con):
        global READERS, Sem, Mtx
        Mtx.acquire()
        for i in range(READERS):
            Sem.acquire()
        self.ledger[addy] = [con,5]
        for i in range(READERS):
            Sem.release()
        Mtx.release()

    def onMin(self):
        global READERS, Sem, Mtx
        Mtx.acquire()
        for i in range(READERS):
            Sem.acquire()


        delKeys = []

        # for every key decrement the time and delete if it runs out
        keys = self.ledger.keys()
        for key in keys:
            prev = self.ledger[key]
            prev[1] = prev[1] -1

            if prev[1 <= 0]:
                delKeys.append(key)

            self.ledger[key] = prev

        for key in delKeys:
            self.ledger.pop(key)

        for i in range(READERS):
            Sem.release()
        Mtx.release()

    def readKeys(self):

        Mtx.acquire()
        Sem.acquire()
        Mtx.release()
        rtn = self.ledger.keys()
        Sem.release()
        
        return rtn

    def __init__(self):
        self.ledger = {}