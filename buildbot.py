#!/usr/bin/env python

from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep


if __name__=="__main__":
    q = TaskQueue()
    q.insert(lambda : nofunc(),every=20)
    q.insert(lambda : nofunc2(),every=10)
    
    
    while True:
        q.execTop()
        sleep(2)