#!/usr/bin/env python
if __name__=="__main__":
    __builtins__.LOGGLY_KEY="f4204229-5e30-475c-a0b6-e85cb4d48367"
from TaskQueue import TaskQueue

def nofunc(): print "test"
def nofunc2(): print "other"

from time import sleep
from fogbugzConnect import FogBugzConnect
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
    juche.info(cases)
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
            juche.info("Fixing priority of case %s to %s" % (child,parent_priority))
            f.setPriority(child,parent_priority)
    
def still_alive():
    juche.info("still alive")


#####################################################################################
                        ### You are entering the... ###
                        ###### UNIT TEST ZONE #########
#####################################################################################


import unittest
import os
import tempfile
import shutil
import zipfile
from work.work import *
from work.fogbugzConnect import FogBugzConnect
from work.gitHubConnect import GitHubConnect
from work.MockRepo import MockRepo
class TestSequence(unittest.TestCase):

    # MARK: Class Setup/Destroy Functions
    def setUp(self):
        """
        Set up unittests for creating sane unit tests
        This includes making available the following resources:
        - A Collection of Zip Files with project types
        - Setting the CWD so that work.py functions can be called directly
        - The work.py functions callable directly. (just call 'projectStart()' etc)
        - The work.py libraries: FogBugzConnect, GitHubConnect, MockRepo
        """

        # Create a mock repo for unit tests in a temp directory.
        self.mockRepoDir = "%s/SampleProject/" % tempfile.gettempdir()
        if not os.path.exists(self.mockRepoDir):
            os.makedirs(self.mockRepoDir)
        # Set python CWD to SampleProject temp dir to enable full usability of work.py functions
        # NOTE: stores starting CWD in self.baseWorkingDir
        self.baseWorkingDir = os.getcwd()

        # Create a class attribute: a Dict of Available project zip files by project name.
        self.testProjectsDir = os.path.join(self.baseWorkingDir, "test_projects")
        self.availableProjectNames = ["xcode-unittests", "SampleProjects"]
        self.availableProjects = {}
        for availableProject in self.availableProjectNames:
            self.availableProjects[availableProject] = os.path.join(self.testProjectsDir, availableProject)
        # NOTE: Available Project Zip files in self.availableProjects[<projectName>]
        # NOTE: These are available to copy into SampleProject temp dir with self.copyProject()

    def tearDown(self):
        shutil.rmtree(self.mockRepoDir)
    
    # MARK: Test Cases

    def test_true(self):
        self.assertTrue(True)

    def _test_changed_cwd(self):
        self.assertTrue(os.getcwd() == os.path.realpath(self.mockRepoDir)) 

    def _test_copyProject(self):
        project = "SampleProjects"
        self.copyProject(project)
        self.assertTrue(os.listdir(self.mockRepoDir) == zipfile.ZipFile(self.availableProjects[project] + ".zip").namelist())

    def test_passing_xcode_case(self):
        # 1) create a case in sample project
        f = FogBugzConnect()
        case = f.fbConnection.new(sProject="Sample Project", sPersonAssignedTo="Jonathan Mason", sTitle="BUILDBOT-passing-xcode-case-test", sFixFor="SampleMilestone-test", hrsCurrEst="10 minutes")
        create_tests()
        # 2) Setup Project and choose commit
        mockRepo = MockRepo(self.mockRepoDir)
        self.copyProject("SampleProjects")
        # --Note: using HEAD
        # 3) Push the commit. ...using force.
        #mockRepo.gitPush(forceful=True)
        # 4) Run Atlas loop
        #atlas()
        # 5) Test for case should pass review and be passed to review
        (parent, testCase) = f.getCaseTuple(case)
        # 6) Close review case
        fbConnection.resolveCase(testCase)
        fbConnection.closeCase(testCase)
        fbConnection.fbConnection.assign(ixBug=parent,ixPersonAssignedTo=7)
        # 7) Rerun atlas loop to assign/merge
        #atlas()
        # 8) Glados closes and merges
        caseStatus = f.getStatuses(case)
        self.assertTrue("closed" in caseStatus)
        # 9) clean up
        #mockRepo.wipeRepo__INCREDIBLY__DESTRUCTIVE_COMMAND()



    # MARK: Unit Test Convenience Functions

    def copyProject(self, projectName):
        if projectName is None or projectName not in self.availableProjectNames:
            raise Exception("ERROR: Illegal Project Name. Do you need to add it to availableProjectNames?")
        with zipfile.ZipFile(self.availableProjects[projectName]+".zip") as projectArchive:
            projectArchive.extractall(self.mockRepoDir)
        return

    ''' 
    DEPRECATED: Using zip files

    def _rCopyDirContents(self, dir, dest):
        contents = os.listdir(dir)
        for id in contents:
            if os.path.isdir(id):
                newDest = os.path.join(dest, id)
                newDir = os.path.join(dir, id)
                os.makdir(newDir)
                self._rCopyDirContents(newDir, newDest)
            else:
                shutil.copy(os.path.join(dir, id), dest)
    '''



#####################################################################################
                        #### You are leaving the... ###
                        ###### UNIT TEST ZONE #########
#####################################################################################


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