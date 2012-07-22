#!/usr/bin/env python

import boto
import ConfigParser
import os

# Read config file
Config = ConfigParser.ConfigParser()
Config.read(os.path.expanduser("~/.popup.conf"))

# Quit if we don't have the right options
for option in ["ami", "instance_type", "security_group", "keypair"]:
    if Config.has_option("EC2",option) is not True:
        print "Config file missing %s in EC2 section. Exiting..." % option
        exit(1)

# Preform an action



## Start instance
# Build a config (user, key, packages, cron job to update/shutdown)
# Start an instance
# Add the instance details to SimpleDB
# Update the .ssh/config file ?
 
## Status
# Get some instance status from EC2

## Clean
# Warn if the instance isn't terminated




