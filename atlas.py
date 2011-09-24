#!/usr/bin/env python

from config import get_config
from work.gitConnect import GitConnect
from fogbugzConnect import FogBugzConnect
WORK_DIR=".buildbot/"
def fetch_all():
    projects = get_config()["Projects"]
    #print projects
    for project in projects:
        try:
            git = GitConnect(WORK_DIR+project["name"])
        except IOError:
            GitConnect.clone(project["url"],WORK_DIR+project["name"])
            git = GitConnect(WORK_DIR+project["name"])
            
        git.fetch()
        
def test_active_tickets():
    f = FogBugzConnect()
    print f.fbConnection.listCases(ixPersonAssignedTo=f.ixPerson)
    
        
    
    
import unittest
class TestSequence(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_fetchall(self):
        fetch_all()
    def test_test_active_tickets(self):
        test_active_tickets()
        
        
if __name__ == '__main__':
    unittest.main()