#!/usr/bin/env python

from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep
from fogbugzConnect import FogBugzConnect
import logbuddy

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
    #4.  Cases that are decided (not Undecided)
    cases = f.fbConnection.search(q='(category:"bug" OR category:"feature") status:"open" estimatecurrent:"1m.." -milestone:"Undecided"')
    cases = map(lambda x: int(x["ixbug"]),cases.cases)
    logging.info(cases)
    from work.work import autoTestMake
    map(autoTestMake,cases)
    
def atlas():
    from atlas import Atlas
    a = Atlas()
    a.fetch_all()
    a.test_active_tickets()
    
def fixup():
    from work.work import fixUp
    fixUp()
    
    
def still_alive():
    logging.info("still alive")
    
import unittest
class TestSequence(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_create_tests(self):
        import cProfile
        #temporarily disabling this test.
        #cProfile.runctx('create_tests()',globals(),locals()) #http://stackoverflow.com/questions/1819448/cannot-make-cprofile-work-in-ipython/3305654#3305654

if __name__=="__main__":
    q = TaskQueue()
    q.insert(atlas,every=3,now=True)
    q.insert(fixup,every=HOURLY*4,now=False)
    q.insert(still_alive,every=60)
    q.insert(autoboss,every=HOURLY)
    q.insert(create_tests,every=HOURLY)
    
    
    while True:
        try:
            q.execTop()
        except Exception as e:
            logging.error("That's funny, I don't feel corrupt.  In fact, I feel pretty good.")
            logbuddy.report(e)
        sleep(2)