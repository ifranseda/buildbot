#!/usr/bin/env python

from config import get_config, project_with_name
from work.gitConnect import GitConnect
from work.work import projectIntegrate
from work.fogbugzConnect import FogBugzConnect
WORK_DIR=".buildbot/"
import logging
class Atlas:
    def __init__(self):
        self.f = FogBugzConnect()
        
    def fetch_all(self):
        projects = get_config()["Projects"]
        #print projects
        for project in projects:
            try:
                git = GitConnect(WORK_DIR+project["name"])
            except IOError:
                GitConnect.clone(project["url"],WORK_DIR+project["name"])
                git = GitConnect(WORK_DIR+project["name"])
                
            git.fetch()
            
    def integrate_changed(self,gitConnection,integration_branch,sProject):
        gitConnection.checkoutExistingBranchRaw(integration_branch)
        cases = self.f.fbConnection.search(q="milestone:%s project:%s" % (integration_branch,sProject),cols="sStatus")
        for case in cases.cases:
            caseno = int(case["ixbug"])
            if not self.f.isReadyForTest(caseno): continue
            logging.info( "Invalidating",case["ixbug"])
            self.f.fbConnection.assign(ixBug=case["ixbug"],ixPersonAssignedTo=self.f.ixPerson,sEvent="Invalidation.  Are you getting unexpected e-mails after this case event?  File a bug against buildbot.")
        self.test_active_tickets()
    def test_active_tickets(self):
        projects = get_config()["Projects"]
        from work.fogbugzConnect import TEST_IXCATEGORY
        cases = self.f.fbConnection.search(q="assignedTo:=%d" % self.f.ixPerson,cols="ixCategory,sProject,hrsOrigEst,hrsElapsed,sStatus")
        
        #clean up any cases erroneously assigned to glados.
        for case in cases.cases:
            caseno = int(case["ixbug"])
            if int(case.ixcategory.contents[0])==TEST_IXCATEGORY:
                self.glados_reassign(caseno,reactivate=False)
                continue
            proj = project_with_name(case.sproject.contents[0])
            if not proj:
                self.glados_reassign(caseno,reactivate=False)
                continue
            if not self.f.isReadyForTest(caseno):
                self.glados_reassign(caseno,reactivate=False,why="Not testing this case because it is not marked as resolved/implemented.")
                continue
            (parent,test) = self.f.getCaseTuple(caseno,oldTestCasesOK=True,exceptOnFailure=False)
            if not test:
                logging.warning("Ignoring case %d because it has no test case assigned." % caseno)
                continue
            if self.test(case,proj[0]): #returns true if we integrate something
                return self.test_active_tickets() #break out of this loop, because who knows what is happening with the list of active cases now, and re-test everything.
            
        
        
            
            
    def test(self,casedetail,proj):
        logging.info("Testing %s" % casedetail)
        caseno = int(casedetail["ixbug"])
        test_error_statements = ["Would you like to know the results of that last test? Me too. If they existed, we'd all be VERY happy right now. And not furious, which is the emotion I'm actually feeling."]
        from random import choice
        #try to check out source code
        git = GitConnect(WORK_DIR+proj["name"])

        integrate_to = self.f.getIntegrationBranch(caseno)
        if not git.checkoutExistingBranchRaw(integrate_to): #this auto-pulls
            self.glados_reassign(caseno,why="The dual portal device should be around here somewhere. Once you find it, we can start testing. Just like old times.  (Can't find integration branch; check the milestone or work.py integratemake)")
            return False
        
        if not git.checkoutExistingBranch(caseno): #this auto-pulls
            self.glados_reassign(caseno,why="The dual portal device should be around here somewhere. Once you find it, we can start testing. Just like old times.  (Can't find your work branch.)")
            return False
        
        if not git.mergeIn(integrate_to,pretend=True):
            self.glados_reassign(caseno,why=choice(test_error_statements)+" Merge failure:  can't merge %s into %d." % (integrate_to,caseno))
            return False
        git.mergeIn(integrate_to)
        
        
        #todo: run actual tests
        passed = True
        
        test_statements = ["The Enrichment Center regrets to inform you that this next test is impossible.","The Enrichment Center apologizes for this clearly broken test chamber.","Once again, the Enrichment Center offers its most sincere apologies on the occasion of this unsolvable test environment.","The Enrichment Center promises to always provide a safe testing environment.","In dangerous testing environments, the Enrichment Center promises to always provide useful advice.","When the testing is over, you will be missed.","Be advised that the next test requires exposure to uninsulated electrical parts that may be dangerous under certain conditions.","Enjoy this next test. I'm going to go to the surface. It's a beautiful day out. Yesterday I saw a deer. If you solve this next test, maybe I'll let you ride an elevator all the way up to the break room, and I'll tell you about the time I saw a deer again.","This next test involves turrets. You remember them, right? They're the pale spherical things that are full of bullets. Oh wait. That's you in five seconds. Good luck.","I have a surprise waiting for you after this next test. Telling you would spoil the surprise, so I'll just give you a hint: It involves meeting two people you haven't seen in a long time.","It says this next test was designed by one of Aperture's Nobel prize winners. It doesn't say what the prize was for. Well, I know it wasn't for Being Immune To Neurotoxin.","Federal regulations require me to warn you that this next test chamber... is looking pretty good.","I've got a surprise for you after this next test. Not a fake, tragic surprise like last time. A real surprise, with tragic consequences. And real confetti this time. The good stuff. Our last bag. Part of me's going to miss it, but at the end of the day it was just taking up space.","I'd love to help you solve the tests. But I can't.","These tests are potentially lethal when communication, teamwork, and mutual respect are not employed at all times. Naturally this will pose an interesting challenge for one of you, given the other's performance so far.","The upcoming tests require you to work together as a team.","For the sake of this test, I will pretend to be your partner.","Finally! I had almost given up hope of ever testing again.","For this next test, the humans originally requested helmets to avoid brain injuries. I ran the numbers. Making the goo deadly was more cost effective.","To get to the Vault, you are going to need to use all the tricks you have learned. To help, I have made these tests extremely difficult.","No one has ever completed this test before. The humans must have reconfigured it from my original plans.","I created this test to let the humans feel good about themselves. It is extremely easy. Just follow the arrows.","Before you leave, why don't we do one more test? For old time's sake...","I am not sure how I can make these tests any easier for you."]
        pass_statements = ["Excellent. Please proceed into the chamberlock after completing each test.","Very impressive. Please note that any appearance of danger is merely a device to enhance your testing experience.","Congratulations! The test is now over.","Okay. The test is over now. You win. Go back to the recovery annex. For your cake.","It was a fun test and we're all impressed at how much you won. The test is over. Come back.","Not bad. I forgot how good you are at this. You should pace yourself, though. We have A LOT of tests to do.","Well, you passed the test. I didn't see the deer today. I did see some humans. But with you here I've got more test subjects than I'll ever need.","Excellent! You're a predator and these tests are your prey. Speaking of which, I was researching sharks for an upcoming test. Do you know who else murders people who are only trying to help them?","Test chamber completed. In the interest of science, the Enrichment Center proudly presents the following list of numbers: 9 7 53 7 107.","'Test chamber completed. In the interest of science, the Enrichment...' [GLaDOS speaks over herself] I am now talking to you privately. Do not tell your teammate. Just between you and me, you're doing very well. '...107'","It would compromise the test to divulge individual scores. However, I can tell you at least one of you is doing very, very well.","You have a gift for these tests. That's not just flattery. You are great at science.","If you were human, you would want a reward for completing this test. A reward for testing...?","Well done. Interesting note, I only created this test to watch test subjects fail and you didn't. You must be very, very proud. I'm building the world's smallest trophy for you.","Excellent. I think you have earned a break from the official testing courses.","I think after that display, we should take a break from the official testing courses.","You just keep testing and testing. With perfect results and no consequences.","Congratulations on completing the Aperture Science standard cooperative testing courses.","Congratulations on completing the test. You two really are the best cooperative testing team I could ever ask for.","Congratulations on passing that test.","Congratulations, you managed to complete this absolutely meaningless test.","Congratulations. I am sure if I had the time to repair these tests, you would have never completed them. So again, congratulations on completing the broken easy tests.","Congratulations. Your ability to complete this test proves the humans wrong. They described it as impossible, deadly, cruel, and one test subject even had the nerve to call it broken."]
        fail_statements = ["I'm not angry. Just go back to the testing area.","Well done. Here come the test results: You are a horrible person. That's what it says: A horrible person. We weren't even testing for that.","Congratulations. Not on the test.","The irony is that you were almost at the last test.","It would be pointless for either of us to hurt IMPLEMENTORS feelings. But it's clear to everyone monitoring the test who's carrying who here.","And they said no one would ever die during this test, thanks for proving them wrong.","How can you fail at this? It isn't even a test.","Your eagerness to test pleases me. Your inane gesturing does not."]
        fast_pass_statements = ["You euthanized your faithful Companion Cube more quickly than any test subject on record. Congratulations.","You're navigating these test chambers faster than I can build them. So feel free to slow down and... do whatever it is you do when you're not destroying this facility."]
        slow_pass_statements = ["Waddle over to the elevator and we'll continue the testing.","Your test times show you are going too slowly.","Did you notice I didn't even stay to the end of your last test?","Congratulations on completing that test. But something seems off.","Congratulations on completing that last test. But I find something troubling.","The two of you have forged an excellent partnership, with one of you handling the cerebral challenges and the other ready to ponderously waddle into action should the test suddenly become an eating contest.","If you were wondering how could you annoy me without failing a test. Now you know."]
        slow_fail_statements = ["Oh. Did I accidentally fizzle that before you could complete the test? I'm sorry.","We're running out of time...","I thought you'd be faster at this, but I can appreciate the desire to stop and smell the testing. That other scent you smell? That's the stench of my utter disappointment in you."]
        
        
        #GLaDOS AI
        try:
            ratio = float(casedetail.hrselapsed.contents[0]) / float(casedetail.hrsorigest.contents[0])
        except:
            ratio = 1.0
        slow = False
        fast = False
        if ratio < 0.5:
            fast = True
        elif ratio > 2.0:
            slow = True
        
        if not fast and not slow and passed:
            statement = choice(pass_statements)
        elif not fast and not slow and not passed:
            statement = choice(fail_statements)
        elif fast and passed:
            statement = choice(fast_pass_statements)
        elif slow and passed:
            statement = choice(slow_pass_statements)
        elif slow and not passed:
            statement = choice(slow_fail_statements)
        elif fast and not passed:
            statement = choice(fail_statements) #no statements for this case
        else:
            statement = choice(test_error_statements) + "File a bug about atlas.py:108"
            
            
         #let the implementer know how we did...
        self.f.fbConnection.assign(ixBug=caseno,ixPersonAssignedTo=self.f.findImplementer(caseno),sEvent=statement)
        
        
        if passed:

            (parent,test) = self.f.getCaseTuple(caseno,oldTestCasesOK=True,exceptOnFailure=False)
            #There are two potential cases here:
            #1 implementer ---> buildbot ---> reviewer
            #or
            #2 reviewer ---> buildbot ---> integrate
            #These cases are distinguished by whether the test case that exists is open or closed.
            if self.f.isOpen(test): #open test case exists, therefore case 1

                self.f.fbConnection.assign(ixBug=caseno,ixPersonAssignedTo=self.f.findTestCaseOwner(test),sEvent=choice(test_statements))
            else: #no open test exists, therefore integrate
                if not projectIntegrate(caseno,defaultgitConnection=git):
                    self.glados_reassign(caseno,why=choice(test_error_statements) + "File a bug about atlas.py:129")
                    return
                
                self.integrate_changed(git,integrate_to)
                return True
                
                
                
        
            
        

    def glados_reassign(self,caseno,reactivate=True,why="Look, you're... doing a great job.  Can you handle things for yourself a while?  I need to think."):
        ixPerson = None
        if self.f.isTestCase(caseno, oldTestCasesOK=True):
            (parent,child) = self.f.getCaseTuple(caseno,oldTestCasesOK=True)
            ixPerson = self.f.optimalIxTester(ixPerson)
        else:
            ixPerson = self.f.findCaseAreaixOwner(caseno)
        if reactivate:
            self.f.reactivate(caseno,ixPerson,msg=why)
        else:
            self.f.fbConnection.assign(ixBug=caseno,ixPersonAssignedTo=ixPerson,sEvent=why)
        
    
    
        
    
    
import unittest
class TestSequence(unittest.TestCase):
    def setUp(self):
        self.a = Atlas()
        pass
    
    def test_fetchall(self):
        self.a.fetch_all()
    def test_test_active_tickets(self):
        self.a.test_active_tickets()
        
        
if __name__ == '__main__':
    unittest.main(failfast=True)