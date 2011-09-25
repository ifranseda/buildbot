#!/usr/bin/env python

def get_config():
    import yaml
    config = open("buildbot.yaml")
    result = yaml.load(config.read())
    config.close()
    return result

def project_with_name(name):
    projects = get_config()["Projects"]
    return filter(lambda x: x["name"]==name,projects)