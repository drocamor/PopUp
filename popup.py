#!/usr/bin/env python

import argparse
import boto
import ConfigParser
import os
import time
import re

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
    
    


def cloudConfig(config):
    output = ["#cloud-config",
              "apt_update: true",
              "#apt_upgrade: true"]
    if config.get("PopUp", "packages"):
        output.append("packages:")
        for package in config.get("PopUp", "packages").split(' '):
            output.append(" - %s" % package)
  
    output.append("runcmd:")
    # If there are any commands in the config file, insert them here
    
    try:
        for script in Config.items('Scripts'):
             output.append(" - %s" % script[1])
    except ConfigParser.NoSectionError:
        pass
        
    try:
        run_time = config.getint("PopUp", "run_time") * 60
    except ConfigParser.NoOptionError:
        run_time = 240 * 60 
     
    output.append(" - echo \* \* \* \* \* [ \$\(cut -d. -f1 /proc/uptime\) -gt %i ] \&\& /sbin/shutdown -h now | /usr/bin/crontab " % run_time)
    output.append("# Thanks for using PopUp!")
    return "\n".join(output)

def startInstance(config):
    conn = boto.connect_ec2()
    reservation = conn.run_instances(image_id = config.get("EC2", "ami"),
                                     key_name = config.get("EC2", "keypair"),
                                     security_groups = [config.get("EC2", "security_group")],
                                     instance_type = config.get("EC2", "instance_type"),
                                     instance_initiated_shutdown_behavior = "terminate",
                                     user_data = cloudConfig(config))

    instance = reservation.instances[0]
    # Find the instances hostname
    while instance.public_dns_name is '':
        time.sleep(5)
        instance.update()
    # Create some tags
    conn.create_tags([instance.id],
                     {'Name': 'PopUp Ephemeral Instance',
                      'popup': 'True'})
    
    updateSSHConfig("Host %s\nHostname %s\nUser %s\n" % (config.get("PopUp", "alias"),
                                                         instance.public_dns_name,
                                                         config.get("PopUp", "username")))
    print "SSH config updated. Instance %s at %s with SSH alias %s available." % (instance.id,
                                                                                  instance.public_dns_name,
                                                                                  config.get("PopUp", "alias"))
    

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




