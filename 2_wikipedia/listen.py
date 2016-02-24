#!/usr/bin/python
# --------------------------------------------------------
# listen.py
# written by Cecilia Saixue Watt, with some help from the
# Wikimedia Foundation (see below.)
#
# Listens to stream.wikimedia.org for any messages of the 
# 'edit' type on a main article (i.e. not a category, a 
# talk page, etc.) and prints an informative JSON messsage.
#
# Every few seconds (defined in PULSE_DURATION, below) 
# calculates the number of messages seen in the last time
# period, and prints a different JSON message with the
# recent rate of messages.
# --------------------------------------------------------
import socketIO_client
import threading
import time
import json
from sys import stdout

# A global variable counter. Global variables are not the best
# thing in the world, but there's threading going on and just...
# just let me have this
# this one global variable
changes_since_tick = 0

# A lock! For locking things! (by things I mean resources)
# Because there's threading going on.
lock = threading.Lock()

# A "final" variable, i.e. one that will not change throughout
# the lifetime of this application running. This variable
# determines how many seconds will pass before calculating the
# rate of edits we are seeing. It's set to 5 seconds right now
# because any less was giving me way too many variations in rate
# (e.g. a lot of noise), and longer time periods just didn't 
# really seem right.
PULSE_DURATION = 5.0

# --------------------------------------------------------
# Here's a class that listens to a Socket.IO channel and
# calls the count() function on every new thing it sees.
# This class is based heavily (HEAVILY) on an example from
# the Wikimedia Foundation:
#
# https://wikitech.wikimedia.org/wiki/RCStream
# --------------------------------------------------------
class WikiNamespace(socketIO_client.BaseNamespace):
	def on_change(self, change):
		# We will only process changes that fulfill the following
		# two conditions:
		# 1. They are edits, not new or log
		# 2. They affect an actual Wiki entry and not a category
		#    or something like that
		if (change.get('namespace')==0) and (change['type'] == 'edit'):
			count(change)

	def on_connect(self):
		# Look only at changes to English Wikipedia.
		self.emit('subscribe', 'en.wikipedia.org')

# --------------------------------------------------------
# And now, some helper methods.
# --------------------------------------------------------

# Prints a JSON message of an 'update' type.
# This happens whenever a change is seen.
def print_change(change):
	print(json.dumps({'type': 'update',
										'user': change['user'],
										'title': change['title']}))
	stdout.flush()

# Prints a JSON message of a 'rate' type.
# This happens every 5 seconds (or whatever is set as
# PULSE_DURATION), it recalculates the rate of messages
# and prints the rate of edits-per-second.
def print_alert(changes_since_tick):
	rate = changes_since_tick / PULSE_DURATION
	print(json.dumps({'type': 'rate','rate': rate}))
	stdout.flush()

# The count(change) function takes one argument, change,
# which is a dictionary. It calls print_change, then updates
# the counter in order to keep track of how many changes
# have appeared in this last time period.
def count(change):
	print_change(change)
	global changes_since_tick
	global PULSE_DURATION
	with lock:
		changes_since_tick = changes_since_tick + 1

# --------------------------------------------------------
# The following function runs in its own thread.
# --------------------------------------------------------

def heartbeat():
	# Run this loop always, forever.
	while 1:
		# This thread is going to sleep for 5 seconds, e.g. this loop is
		# going to run once every 5 seconds. 
		global PULSE_DURATION
		time.sleep(PULSE_DURATION)

		global changes_since_tick
		print_alert(changes_since_tick)

		# Now it's time to reset the counter back to 0. Before we do this,
		# we acquire a lock. During development, I never did manage to get
		# a race condition to occur, but it is theoretically possible (very
		# possible) that this thread and the count() method will try to access
		# global variable changes_since_tick at the same instance, cause a 
		# race condition, and destroy everything I have ever known or loved.

		# Actually, the fact that I didn't see any race conditions occur without
		# this lock suggests that I have done something terribly wrong.

		# Oh well.
		with lock:
			changes_since_tick = 0

# --------------------------------------------------------
# Main method where everything starts.
# --------------------------------------------------------
def main():
	# first we start our heartbeat thread
	pulse_thread = threading.Thread(target=heartbeat)
	pulse_thread.daemon = True
	pulse_thread.start()
	# then we start listening on the socket
	socketIO = socketIO_client.SocketIO('stream.wikimedia.org', 80)
	socketIO.define(WikiNamespace, '/rc')
	socketIO.wait()

if __name__ == "__main__":
	main()