#!/usr/bin/env python

from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep
from fogbugzConnect import FogBugzConnect
import logbuddy

HOURLY=60*60
MINUTELY = 60
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
import magic
def autoboss():
    from work.work import complain
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    people = f.annoyableIxPeople()
    map(complain,people)
    
def buildbot_cache_get():
    import os
    import pickle
    try:
        myfile = open(os.path.expanduser("~/.buildbot-cache"))
        result =  pickle.load(myfile)
        myfile.close()
        return result
    except:
        buildbot_cache_set({})
        return buildbot_cache_get()
        
def buildbot_cache_set(obj):
    import os
    import pickle
    myfile = open(os.path.expanduser("~/.buildbot-cache"),"w")
    pickle.dump(obj,myfile)
    myfile.close()
    
        
    
    
def create_tests():
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    #we only create test cases for:
    #1.  Bugs and features
    #2.  Open cases
    #3.  Cases with an estimate (otherwise, the person assigned might just be a placeholder person...)
    #4.  Cases that are decided (not Undecided)
    cases = f.fbConnection.search(q='(category:"bug" OR category:"feature") status:"open" estimatecurrent:"1m.." -milestone:"Undecided"')
    cache = buildbot_cache_get()
    CACHE_KEY = "autoTestMake-cache"
    if not cache.has_key(CACHE_KEY):
        cache[CACHE_KEY] = []
    cases = map(lambda x: int(x["ixbug"]),cases.cases)
    cases = filter(lambda x: x not in cache[CACHE_KEY],cases)
    logging.info(cases)
    from work.work import autoTestMake
    for case in cases:
        result = autoTestMake(case)
        if not result: cache[CACHE_KEY].append(case)
    
    buildbot_cache_set(cache)
    
def atlas():
    from atlas import Atlas
    a = Atlas()
    a.fetch_all()
    a.test_active_tickets()
    
def fixup():
    from work.work import fixUp
    fixUp()

def priority_fix():
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    for case in f.listTestCases().cases:
        ixBug = case["ixbug"]
        (parent,child) = f.getCaseTuple(ixBug)
        parent_priority = f.fbConnection.search(q=parent,cols="ixPriority").ixpriority.contents[0]
        child_priority = f.fbConnection.search(q=child,cols="ixPriority").ixpriority.contents[0]
        if parent_priority != child_priority:
            logging.info("Fixing priority of case %s to %s" % (child,parent_priority))
            f.setPriority(child,parent_priority)
    
def still_alive():
    logging.info("still alive")
    
import unittest
class TestSequence(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_create_tests(self):
        create_tests()
        #import cProfile
        #cProfile.runctx('create_tests()',globals(),locals()) #http://stackoverflow.com/questions/1819448/cannot-make-cprofile-work-in-ipython/3305654#3305654

if __name__=="__main__":
    q = TaskQueue()
    q.insert(priority_fix,every=HOURLY*6,now=False)
    q.insert(atlas,every=MINUTELY,now=True)
    q.insert(fixup,every=HOURLY*4,now=False)
    q.insert(still_alive,every=60)
    q.insert(autoboss,every=HOURLY)
    q.insert(create_tests,every=MINUTELY)
    
    
    while True:
        try:
            q.execTop()
        except Exception as e:
            logging.error("That's funny, I don't feel corrupt.  In fact, I feel pretty good.")
            logbuddy.report(e)
        sleep(2)