#!/usr/bin/env python

def get_config():
    import yaml
    config = open("buildbot.yaml")
    result = yaml.load(config.read())
    config.close()
    return result