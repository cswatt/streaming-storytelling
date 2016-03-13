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
import json
from sys import stdout


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
			print(json.dumps(change))
			stdout.flush()

	def on_connect(self):
		# Look only at changes to English Wikipedia.
		self.emit('subscribe', 'en.wikipedia.org')


def main():
	# then we start listening on the socket
	socketIO = socketIO_client.SocketIO('stream.wikimedia.org', 80)
	socketIO.define(WikiNamespace, '/rc')
	socketIO.wait()

if __name__ == "__main__":
	main()