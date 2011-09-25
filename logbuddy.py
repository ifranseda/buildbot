#!/usr/bin/env python
import urllib
import urllib2
import traceback
import logging
def report(exception):

    logging.exception(exception)
    url = "https://drewcrawfordapps.fogbugz.com/ScoutSubmit.asp"
    args = {
        "ScoutUserName": "LogBuddy",
        "ScoutProject": "buildbot",
        "ScoutArea": "Misc",
        "Description": exception,
        "ForceNewBug": "0",
        "Extra": traceback.format_exc(),
        "Email": "GLaDOS@drewcrawfordapps.com",
        "ScoutDefaultMessage": "html Default Message",
        "FriendlyResponse": "1",
    }
    request = urllib2.Request(url, data=urllib.urlencode(args))
    response = urllib2.urlopen(request).read()
    print response