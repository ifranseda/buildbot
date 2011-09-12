#!/usr/bin/env python

from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep
from fogbugzConnect import FogBugzConnect

HOURLY=60*60

import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
import magic
magic.BUILDBOT_USERNAME = "GLaDOS"
def autoboss():
    from work.work import complain
    complain()
    
def still_alive():
    logging.info("still alive")

if __name__=="__main__":
    q = TaskQueue()
    q.insert(still_alive,every=60)
    q.insert(autoboss,every=HOURLY,now=False) #probably don't want to complain every time we fix a buildbot bug...
    
    
    while True:
        q.execTop()
        sleep(2)