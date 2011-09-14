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
def autoboss():
    from work.work import complain
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    people = f.annoyableIxPeople()
    map(complain,people)
    
def create_tests():
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    #we only create test cases for:
    #1.  Bugs and features
    #2.  Open cases
    #3.  Cases with an estimate (otherwise, the person assigned might just be a placeholder person...)
    cases = f.fbConnection.search(q='(category:"bug" OR category:"feature") status:"open" estimatecurrent:"1m.."')
    cases = map(lambda x: int(x["ixbug"]),cases.cases)
    print cases
    from work.work import autoTestMake
    autoTestMake(cases[1])
    
    
def still_alive():
    logging.info("still alive")
    
import unittest
class TestSequence(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_create_tests(self):
        import cProfile
        cProfile.runctx('create_tests()',globals(),locals()) #http://stackoverflow.com/questions/1819448/cannot-make-cprofile-work-in-ipython/3305654#3305654

if __name__=="__main__":
    q = TaskQueue()
    q.insert(still_alive,every=60)
    q.insert(autoboss,every=HOURLY,now=False) #probably don't want to complain every time we fix a buildbot bug...
    
    
    while True:
        q.execTop()
        sleep(2)