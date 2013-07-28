#!/usr/bin/env python

import boto
import time
import urllib

class EC2Metadata:
    """Class for querying metadata from EC2"""

    def __init__(self, addr='169.254.169.254', api='latest'):
        self.addr = addr
        self.api = api

    def _get(self, uri):
        url = 'http://%s/%s/%s/' % (self.addr, self.api, uri)
        value = urllib.urlopen(url).read()
        if "404 - Not Found" in value:
            return None

        return value
    
    def instance_id(self):
        return self._get('meta-data/instance-id')

    def availability_zone(self):
        return self._get('meta-data/placement/availability-zone')


# parse arguments:
# - Volume Tag
popup_volume_id = 'DrocamorHomeDirectory'

ec2 = boto.connect_ec2()
instance_metadata = EC2Metadata()

# Get our AZ and instance ID
instance_az = instance_metadata.availability_zone()
instance_id = instance_metadata.instance_id()
device_id = '/dev/sdf'

# Find volumes that have the Volume Tag, pick the most recently created one.
volumes = ec2.get_all_volumes(filters={'tag:popup-volume-id': popup_volume_id,'status': 'available'})
volume = sorted(volumes, key=lambda v: v.create_time)[-1]

# If the volume is in our AZ, attach it and exit
if volume.zone == instance_az:
    print "The volume is in our AZ, attaching to the instance"
    volume.attach(instance_id, device_id)
else:
    print "The volume is in another AZ."
    # Find the most recent snapshot
    existing_snaps = ec2.get_all_snapshots(filters={'tag:popup-volume-id': popup_volume_id})
    sorted_snaps = sorted(existing_snaps, key=lambda s: s.start_time)
    
    snapshot = sorted_snaps[-1]

    # Create a volume from the snapshot in our AZ
    print "Creating volume..."
    new_volume = snapshot.create_volume(instance_az)
    new_volume.add_tag('popup-volume-id', value=popup_volume_id)
    print "Volume ID is %s" % new_volume.id
    while new_volume.status != 'available':
        print "Sleeping for 5 seconds for volume creation..."
        time.sleep(5)
        new_volume.update()

    # Attach the volume to our instance
    print "Attaching new volume..."
    new_volume.attach(instance_id, device_id)

    # Delete the old volume
    print "Deleting old volume..."
    volume.delete()


