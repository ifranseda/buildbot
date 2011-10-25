#!/usr/bin/env python

def get_config():
    import yaml
    config = open("buildbot.yaml")
    result = yaml.load(config.read())
    config.close()
    return result

def project_with_name(name):
	config = get_config()
    projects = get_config()["Projects"]
    proj_filter = filter(lambda x: x["name"]==name,projects)
    if len(proj_filter)==0:
    	return None
    return proj_filter[0]