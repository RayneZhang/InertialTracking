# This is a simple multi-threaded OSC server to retrieve accelerometer data from
# the GyrOSC iPhone App.
#
# Andrew Vande Guchte - Feb 2019

# For those unfamiliar, the flow of this program is a little different from programs you may have
# produced up to this point. There is effectively two processes co-occuring:
#
# 1. The server that listens endlessly for information on a certain IP address
# 2. The modified_output process that responds to specific activation inputs
#
# In order to make this code work, find out your local IP address. Put that in the default IP
# argument on line 95. Then, put that same IP into the GyrOSC application. Be sure the port number
# (line 97) is also identical between this application and GyrOSC.

import argparse
import multiprocessing
import queue
import time
import datetime
import sys
from pythonosc import dispatcher
from pythonosc import osc_server
import requests

class modified_output(multiprocessing.Process):

    def __init__(self,bq):
        # Call the superclass constructor, so that this class's constructor
        # doesn't completely supercede it.
        multiprocessing.Process.__init__(self)

        # Make queue an instance variable.
        self._bq = bq

        # Set up local variables.
        self.playing = True

        # Set up token.
        self.token = ''

    def run(self):
        '''This method is what is invoked when calling a Process class's .start() method.'''

        # Initialize the while loop here:
        running = True
        # We don't have any incoming commands yet, so this is False.
        waiting_command = False
        # How many seconds do you want between each action of a specific class?
        # The reason we have this is so that each shake doesn't accidentally trigger
        # a ton of prints.
        self.delay = 0.4
        # Initialize the events that could happen.
        self.commands = {
            'xshake':{
                's':'Shook in the X direction!',
                't':0
            },
            'playpause':{
                's':'playpause',
                't':0
            },
            'zshake':{
                's':'zshake',
                't':0
            },
            'pitch':{
                's':'Pitch!',
                't':0
            },
            'prev':{
                's':'prev',
                't':0
            },
            'next':{
                's':'next',
                't':0
            },
            'yaw':{
                's':'Yaw!',
                't':0
            }
        }

        while running:

            if waiting_command:

                # Find the number of seconds since epoch.
                now = datetime.datetime.now().timestamp()

                # Prevent duplicate prints for the same shake event:
                if now > self.commands[event]['t']+self.delay:
                    # Reset time.
                    self.commands[event]['t'] = now

                    headers = {'Authorization': self.token}

                    if self.commands[event]['s'] == 'playpause':
                        print('Shook in the Y direction!')
                        if self.playing == False:
                            play = requests.put('https://api.spotify.com/v1/me/player/play', headers=headers)
                            self.playing = True
                        else:
                            pause = requests.put('https://api.spotify.com/v1/me/player/pause', headers=headers)
                            self.playing = False
                        
                    if self.commands[event]['s'] == 'prev':
                        print('Skip to previous track!')
                        prev = requests.post('https://api.spotify.com/v1/me/player/previous', headers=headers)

                    if self.commands[event]['s'] == 'next':
                        print('Skip to next track!')
                        nxt = requests.post('https://api.spotify.com/v1/me/player/next', headers=headers)

                # Reset and wait for the next event command.
                waiting_command = False

            try:
                # Grab the next event in queue. The True parameter refers to the 'block' argument,
                # which will block until next item is available. Otherwise, would return
                # an Empty exception as soon as nothing is availableself.
                # Docs: https://docs.python.org/3/library/queue.html
                event = self._bq.get(True)
                waiting_command = True
            except:
                running = False


if __name__ == "__main__":
    # Set up the server details, as described in the documentation:
    # https://pypi.org/project/python-osc/
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
      default="35.2.150.153", help="The ip to listen on")
    parser.add_argument("--port",
      type=int, default=2222, help="The port to listen on")
    args = parser.parse_args()

    # Start multiprocess queue...information goes in here and leaves the
    # queue in the same order that it goes in.
    bq = multiprocessing.Queue()

    # Create instance of event handler class:
    mo = modified_output(bq)

    def put_accel_in_queue(args0, args1, args2, args3):
        """Put a string into the queue, to process sequentially. The things you put_in_queue
        doesn't have to be a string...you could put any python object."""
        if args1 < -1.0 or args1 > 1.0: # Y-Horizontal shake.
            bq.put('xshake')
        if args2 < -1.0 or args2 > 1.0: # Y-Horizontal shake.
            bq.put('playpause')
        if args3 < -1.0 or args3 > 1.0: # Vertical shake.
            bq.put('zshake')
    
    def put_gyro_in_queue(args0, args1, args2, args3):
        """Put a string into the queue, to process sequentially. The things you put_in_queue
        doesn't have to be a string...you could put any python object."""
        if args1 < -1.0 or args1 > 1.0: # Rotation around x axis.
            bq.put('pitch')
        if args2 < -0.9: # Rotation around y axis.
            bq.put('prev')
        if args2 > 0.9: # Rotation around y axis.
            bq.put('next')
        if args3 < -1.0 or args3 > 1.0: # Rotation around z axis.
            bq.put('yaw')

    # Initialize the dispatcher. This class essentially directs the data stream
    # to where it should go based off of that data's identifier.
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/gyrosc/myphone/accel",put_accel_in_queue)
    dispatcher.map("/gyrosc/myphone/gyro",put_gyro_in_queue)

    # Set up the server thread.
    server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    print("To quit, press Ctrl+C")

    # Start handler:
    mo.start()

    # Start the server, to listen on the IP channel for OSC-protocol signals forever.
    server.serve_forever()
