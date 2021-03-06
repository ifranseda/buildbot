#!/usr/bin/env python
if __name__=="__main__":
    __builtins__.LOGGLY_KEY="f4204229-5e30-475c-a0b6-e85cb4d48367"
from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep
from work.fogbugzConnect import FogBugzConnect
import logbuddy
from JucheLog.juchelog import juche
HOURLY=60*60
MINUTELY = 60
import magic
def autoboss():
    from work.work import complain
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    people = f.annoyableIxPeople()
    from config import get_config
    projects = get_config()["Projects"]
    map(lambda person: complain(person,projects.keys()),people)

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
    from config import project_with_name
    f = FogBugzConnect()
    #we create test cases if and only if all the following conditions are met:
    #1.  Bugs and features
    #2.  Open cases
    #3.  Cases with an estimate (otherwise, the person assigned might just be a placeholder person...)
    #4.  Cases that are decided (not Undecided)
    #5.  Cases that are in projects for which we have review-workflow: yes
    cases = f.fbConnection.search(q='(category:"bug" OR category:"feature") status:"open" estimatecurrent:"1m.." -milestone:"Undecided"', cols="sProject")
    cache = buildbot_cache_get()
    CACHE_KEY = "autoTestMake-cache"
    if not cache.has_key(CACHE_KEY):
        cache[CACHE_KEY] = []
    casesList = map(lambda x: int(x["ixbug"]),cases.cases)
    casesList = filter(lambda x: x not in cache[CACHE_KEY],casesList)
    juche.info(casesList)
    from work.work import autoTestMake
    for case in cases.cases.contents:
        project = project_with_name(case.sproject.contents[0])
        if not project: 
            juche.info("No project named %s in buildbot.yaml" % case.sproject.contents[0])
            continue
        if not ("review-workflow" in project.keys() and project["review-workflow"] == "yes"):
            continue
        result = autoTestMake(int(case["ixbug"]))
        if not result: cache[CACHE_KEY].append(case["ixbug"])

    buildbot_cache_set(cache)

def atlas():
    from atlas import Atlas
    a = Atlas()
    a.fetch_all()
    a.test_active_tickets()

def fixup():
    from work.work import fixUp
    fixUp()

"""Make the test cases match the priority of their parent cases"""
def priority_fix():
    from work.fogbugzConnect import FogBugzConnect
    f = FogBugzConnect()
    for case in f.listTestCases().cases:
        ixBug = case["ixbug"]
        (parent,child) = f.getCaseTuple(ixBug)
        parent_priority = f.fbConnection.search(q=parent,cols="ixPriority").ixpriority.contents[0]
        child_priority = f.fbConnection.search(q=child,cols="ixPriority").ixpriority.contents[0]
        if parent_priority != child_priority:
            juche.info("Fixing priority of case %s to %s" % (child,parent_priority))
            f.setPriority(child,parent_priority)

def still_alive():
    juche.info("still alive")

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
    q.insert(autoboss,every=HOURLY*4)
    q.insert(create_tests,every=MINUTELY)


    while True:
        try:
            q.execTop()
        except Exception as e:
            juche.error("That's funny, I don't feel corrupt.  In fact, I feel pretty good.")
            juche.exception(e)
        sleep(2)
