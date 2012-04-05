#!/usr/bin/env python

from config import get_config
from JucheLog.juchelog import juche
import subprocess

class Cronjob:

	def __init__(self):
		self.jobs = []

	def loadJobs(self):
		for project in get_config():
			self.jobs[] = project["cron-tasks"]

	def doJobs(self):
		with juche.revolution(task="cron-tasks"):
			for job in self.jobs:
				juche.info(job["name"])
				response = subprocess.call(job["cmd"])
				if response == expectedResponseFor(job["type"]):
					juche.info("Expected Response for " + job["name"])
				else
					mailErrorTo(job["failmail"])

	def expectedResponseFor(self, type):
		pass

	def mailErrorTo(self, recipient):
		pass

