from threading import Semaphore, Lock

READERS = 8
Sem = Semaphore(READERS)
Mtx = Lock()

class Ledger:

    """
         Key              0                 1
    [ [IP Address] [IP Connection] [Min to Experation] ]
    [ [          ] [             ] [                 ] ]
    ...
    """

    def add(self, addy, con, num=0):
        global READERS, Sem, Mtx
        # grab all the semifors before editing
        Mtx.acquire()
        for i in range(READERS):
            Sem.acquire()

        # handle different condiitons to adjust time of death
        if self.ledger.__contains__(addy) and num==0:
            num = self.ledger[addy][1]
        else:
            num = 5

        # add or update the addy
        self.ledger[addy] = [con,num]


        # release the semifors and mutex
        for i in range(READERS):
            Sem.release()
        Mtx.release()

    def onMin(self):
        global READERS, Sem, Mtx
        # grab the sems to edit
        Mtx.acquire()
        for i in range(READERS):
            Sem.acquire()

        delKeys = []
        # for every key decrement the time and delete if it runs out
        keys = self.ledger.keys()
        for key in keys:
            prev = self.ledger[key]
            prev[1] = prev[1] -1

            if prev[1] <= 0:
                delKeys.append(key)

            self.ledger[key] = prev

        for key in delKeys:
            self.ledger.pop(key)

        # release the sems
        for i in range(READERS):
            Sem.release()
        Mtx.release()

    def readKeys(self):
        # read the keys
        Mtx.acquire()
        Sem.acquire()
        Mtx.release()
        rtn = self.ledger.keys()
        Sem.release()
        
        return rtn

    def print(self):
        rtn = "=============LEDGER================"

        # get a semifore because I'm reading
        Mtx.acquire()
        Sem.acquire()
        Mtx.release()

        keys = self.ledger.keys()

        # format ledger to return string
        for key in keys:
            line = "\n  "
            line += key + (15-len(key))*" " + "      "
            Fip = self.ledger.get(key)[0]
            tm = self.ledger.get(key)[1]
            line += (15-len(Fip))*" " + Fip + "   "
            line += str(tm)
            rtn += line

        # release sem
        Sem.release()
        
        return rtn

    def __init__(self):
        self.ledger = {}