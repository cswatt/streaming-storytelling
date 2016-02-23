from sys import stdout
from google.transit import gtfs_realtime_pb2
import urllib2, contextlib
import requests
import time
import sys
feed_url = 'http://datamine.mta.info/mta_esi.php?key=244af9c1c430895a314bcd995a0ba11c&feed_id=1'
trains = dict()

while True:
	mta_data = gtfs_realtime_pb2.FeedMessage()
	with contextlib.closing(urllib2.urlopen(feed_url)) as r:
		data = r.read()
		mta_data.ParseFromString(data)

	for entity in mta_data.entity:
		if entity.HasField('trip_update'):
			trip_id = entity.trip_update.trip.trip_id
			stop_id = entity.trip_update.stop_time_update[0].stop_id

			if trip_id not in trains:
				trains[trip_id] = stop_id
				continue

			if trains[trip_id] != stop_id:
				print trip_id + " has left " + trains[trip_id]
				stdout.flush()
				trains[trip_id] = stop_id

	time.sleep(2)
