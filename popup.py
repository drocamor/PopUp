#!/usr/bin/env python

import argparse
import boto
import ConfigParser
import os

def startInstance(config):
    conn = boto.connect_ec2()
    conn.run_instances(image_id = config.get("EC2", "ami"),
                       key_name = config.get("EC2", "keypair"),
                       security_groups = [config.get("EC2", "security_group")],
                       instance_type = config.get("EC2", "instance_type"))

# Read config file
Config = ConfigParser.ConfigParser()
Config.read(os.path.expanduser("~/.popup.conf"))

# Quit if we don't have the right options
for option in ["ami", "instance_type", "security_group", "keypair"]:
    if Config.has_option("EC2",option) is not True:
        print "Config file missing %s in EC2 section. Exiting..." % option
        exit(1)

# Let the user pick an action
parser = argparse.ArgumentParser(
    description='PopUp an ephemeral EC2 instance',
    epilog='Actions are: start, status, cleanup')
parser.add_argument('action', nargs=1, help='PopUp Action to run')
args = parser.parse_args()
action = args.action[0]

if action == 'start':
    print 'Starting an instance...'
    startInstance(Config)
elif action == 'status':
    print 'Instance status...'
elif action == 'cleanup':
    print 'Cleaning up...'
else:
    print 'Invalid action.'
    parser.print_help()
    exit(1)

## Start instance
# Build a config (user, key, packages, cron job to update/shutdown)
# Start an instance
# Add the instance details to SimpleDB
# Update the .ssh/config file ?
 
## Status
# Get some instance status from EC2

## Clean
# Warn if the instance isn't terminated




