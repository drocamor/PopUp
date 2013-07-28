#!/usr/bin/env python

import boto
import time

# parse arguments:
# - Volume Tag
popup_volume_id = 'DrocamorHomeDirectory'

ec2 = boto.connect_ec2()

# Get our AZ and instance ID
instance_az = 'us-east-1b'
instance_id = 'asdfasdf'
device_id = '/dev/sdf'


# Find volumes that have the Volume Tag, pick the most recently created one.
volumes = ec2.get_all_volumes(filters={'tag:popup-volume-id': popup_volume_id,'status': 'available'})
volume = sorted(volumes, key=lambda v: v.create_time)[-1]

# Get the volume AZ
# 

# If the volume is in our AZ, attach it and exit
if volume.zone == instance_az:
    print "The volume is in our AZ, attaching to the instance"
    volume.attach(instance_id, device_id)
else:
    print "The volume is in another AZ."
    # If the volume is not in our AZ:
    # - Take a snapshot
    print "Creating snapshot..."
    snapshot = volume.create_snapshot(description='Temporary PopUp snapshot')
    print "Snapshot id is %s" % snapshot.id
    while snapshot.status != 'completed':
        print "Sleeping for 5 seconds for snapshot creation..."
        time.sleep(5)
        snapshot.update()
    # - Create a volume from the snapshot in our AZ
    print "Creating volume..."
    new_volume = snapshot.create_volume(instance_az)
    new_volume.add_tag('popup-volume-id', value=popup_volume_id)
    print "Volume ID is %s" % new_volume.id
    while new_volume.status != 'available':
        print "Sleeping for 5 seconds for volume creation..."
        time.sleep(5)
        new_volume.update()
    # - Attach the volume to our instance
    print "Attaching new volume..."
    new_volume.attach(instance_id, device_id)
    # - Delete the old volume and snapshot
    print "Deleting old volume and snapshot"
    volume.delete()
    snapshot.delete()

