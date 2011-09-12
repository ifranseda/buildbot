#!/usr/bin/env python

from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep
import logging


if __name__=="__main__":
    q = TaskQueue()
    q.insert(lambda : logging.info("still alive"),every=60)
    
    
    while True:
        q.execTop()
        sleep(2)