#!/usr/bin/env python

__builtins__.LOGGLY_KEY="f4204229-5e30-475c-a0b6-e85cb4d48367"

from config import get_config
from JucheLog.juchelog import juche
import subprocess

class Cronjob:

	def __init__(self):
		self.jobs = []

	def loadJobs(self):
		for project in get_config()["Projects"]:
			if "cron-tasks" in project:
				for job in project["cron-tasks"]:
					self.jobs.append(job)

	def doJobs(self):
		with juche.revolution(task="cron-tasks"):
			for job in self.jobs:
				juche.info(job["name"])
				response = subprocess.check_output(job["cmd"],shell=True)
				if self.isExpectedResponse(job["type"], response):
					juche.info("Expected Response for " + job["name"])
				else:
					self.mailErrorTo(job["failmail"])

	def isExpectedResponse(self, type, response):
		if type == "http-status-code":
			codes = response.split("\n")
			status = codes[len(codes) - 2].split(" ")[1]
			if status == "200":
				return True
		else:
			return False

	def mailErrorTo(self, recipient):
		juche.info("Fail-mail to : " + recipient)

if __name__ == "__main__":
	c = Cronjob()
	c.loadJobs()
	c.doJobs()