#!/usr/bin/env python

import argparse
import boto
import ConfigParser
import os
import time
import re

def findPopUp(config):
    conn = boto.connect_ec2()
    # I really suck at list comprehension
    all_instances =  [ res.instances for res in conn.get_all_instances() ]
    flattened_all_instances =  [ i for i in all_instances for i in i ]
    running_instances = [ i for i in flattened_all_instances if i.state == 'running' ]
    running_popup_instances = [ i for i in running_instances if i.tags.has_key('popup-unique-id') and i.tags['popup-unique-id'] == config.get("PopUp", "id") ]
    return running_popup_instances

def updateSSHConfig(ssh_alias):
    popup_replacer = re.compile('# Begin PopUp Config.*?# End PopUp Config', re.DOTALL)
    popup_pre = "# Begin PopUp Config\n# (This stuff is automatically added and deleted by PopUp)\n"
    popup_post = "# End PopUp Config"

    try:
        ssh_config_file = open(os.path.expanduser("~/.ssh/config"), 'r')
        ssh_config = ssh_config_file.read()
        ssh_config_file.close()
        new_ssh_config = popup_replacer.sub(popup_pre + ssh_alias + popup_post, ssh_config)
    except IOError:
        new_ssh_config = popup_pre + ssh_alias + popup_post
    finally:
        ssh_config_file = open(os.path.expanduser("~/.ssh/config"), 'w')
        ssh_config_file.write(new_ssh_config)
        ssh_config_file.close()    

def startInstance(config):
    updateSSHConfig("Host %s\nHostname %s\nUser %s\n" % (config.get("PopUp", "alias"),
                                                         instance.public_dns_name,
                                                         config.get("PopUp", "username")))
    print "SSH config updated. Instance %s at %s with SSH alias %s available." % (instance.id,
                                                                                  instance.public_dns_name,
                                                                                  config.get("PopUp", "alias"))
    

class PopUp:
    """"A PopUp Instance"""
    def __init__(self, image_id, key_name, security_group,
                 instance_type, user_data, popup_id):
        self.image_id = image_id
        self.key_name = key_name
        self.security_group = security_group
        self.instance_type = instance_type
        self.user_data = user_data
        self.popup_id = popup_id
        self.ec2 = boto.connect_ec2()

    def start(self):
        reservation = self.ec2.run_instances(image_id = self.image_id,
                                             key_name = self.key_name,
                                             security_groups = [self.security_group],
                                             instance_type = self.instance_type,
                                             instance_initiated_shutdown_behavior = "terminate",
                                             user_data = self.user_data)

        instance = reservation.instances[0]
        # Find the instances hostname
        while instance.public_dns_name is '':
            time.sleep(5)
            instance.update()

        # Create some tags
        self.ec2.create_tags([instance.id],
                             {'Name': 'PopUp Ephemeral Instance',
                              'popup': 'True',
                              'popup-unique-id': self.popup_id})

        self.id = instance.id
        self.public_dns_name = instance.public_dns_name


# Read config file
config = ConfigParser.ConfigParser()
config.read(os.path.expanduser("~/.popup.conf"))

# Quit if we don't have the right options
for option in ["image_id", "instance_type", "security_group", "key_name"]:
    if config.has_option("EC2",option) is not True:
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
    # Read in the user-data file
    try:
        f = open(os.path.expanduser(config.get("PopUp", "user_data_file")))
        user_data = f.read()
        f.close()
    except:
        exit(1)
    # Create a new popup object
    popup = PopUp(image_id = config.get("EC2", "image_id"),
                  key_name = config.get("EC2", "key_name"),
                  security_group = config.get("EC2", "security_group"),
                  instance_type = config.get("EC2", "instance_type"),
                  popup_id = config.get("PopUp", "id"),
                  user_data = user_data)

    # Start the instance
    popup.start()
    print popup.id
    print popup.public_dns_name
    #popup.updateSSHConfig()
    #print "PopUp instance %s started." % popup.id

elif action == 'status':
    print 'Getting status of running instances'
    for instance in PopUp.findInstances():
        print "PopUp: %s at %s " % (instance.id, instance.public_dns_name)
elif action == 'cleanup':
    print 'Cleaning up...'
else:
    print 'Invalid action.'
    parser.print_help()
    exit(1)




