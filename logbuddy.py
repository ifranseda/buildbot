#!/usr/bin/env python
import urllib
import urllib2
import traceback
import logging
import hashlib
DEBUG_MODE = True
def report(exception):

    logging.exception(exception)
    if DEBUG_MODE:
        logging.fatal("Debug mode is on.")
        return
    if str(exception).find("HTTP Error 500: Internal Server Error") != -1 or str(exception).find("FogBugzConnectionError") != -1:
        logging.exception("Not reporting this.  You're on your own, sorry.")
        return
    url = "https://drewcrawfordapps.fogbugz.com/ScoutSubmit.asp"
    args = {
        "ScoutUserName": "LogBuddy",
        "ScoutProject": "buildbot",
        "ScoutArea": "Misc",
        "Description": hashlib.md5(str(exception) +  traceback.format_exc()).hexdigest(),
        "ForceNewBug": "0",
        "Extra": traceback.format_exc(),
        "Email": "GLaDOS@drewcrawfordapps.com",
        "ScoutDefaultMessage": "html Default Message",
        "FriendlyResponse": "1",
    }
    request = urllib2.Request(url, data=urllib.urlencode(args))
    response = urllib2.urlopen(request).read()
    print response
