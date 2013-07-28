#!/usr/bin/env python

import boto

# parse arguments:
# - Volume Tag
popup_volume_id = 'DrocamorHomeDirectory'

ec2 = boto.connect_ec2()

# Get the volume
volumes = ec2.get_all_volumes(filters={'tag:popup-volume-id': popup_volume_id})
volume = sorted(volumes, key=lambda v: v.create_time)[-1]
print "Got volume %s" % volume.id

# Create a snapshot
snapshot = volume.create_snapshot(description="PopUp Snapshot for %s" % popup_volume_id)
snapshot.add_tag('popup-volume-id', value=popup_volume_id)
snapshot.add_tag("PopUp Snapshot for %s" % popup_volume_id)
print "Created snapshot %s" % snapshot.id


# Get the snapshots
existing_snaps = ec2.get_all_snapshots(filters={'tag:popup-volume-id': popup_volume_id})
snapshots = sorted(existing_snaps, key=lambda s: s.start_time)

# Delete all but the 5 latest snapshots
del snapshots[-5:] # <- shame on me and my mutable variables :(

for s in snapshots:
    print "Deleting old snapshot %s" % s.id
    s.delete()
