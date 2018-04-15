
## Reliable Communication

In this project, a reliable communication over an unreliable link is implemented,
just like TCP.

The code simulates an unreliable link between sender
and receiver.  This link has a very constrained buffer (only two packets can
be 'in flight' at a time), and can have arbitrary delay and loss rates. 
A protocol over this connection that correctly transfers data, in a reasonable amount of time
is implemented.


### Writing Your Solution

This repo contains several tools that will help you simulate and test your
solution.  **You should not make changes to any file other than `hw5.py`.**
All other files contain code used to either simulate the unreliable connection,
or code to help you test your your solution.

Your solution / `hw5.py` file will be tested against stock versions of all the
other files in the repo, so any changes you make will not be present at
grading time.

Your solution must be contained in the `send` and `recv` functions in `hw5.py`.
You should not change the signatures of these functions, only their bodies.
These functions will be called by the grading script, with parameters
controlled by the grading script.  Your solution must be general, and should
work for any file.

Your task is to modify the bodies of these functions so that they communicate
using a protocol that ensures that the data sent by the `send` function
can be reliably and quickly reconstructed by the `recv` function.  You should
do so through a combination of setting timeouts on socket reads (e.x.
`socket.timeout(float)`) and developing a system through which each side can
acknowledge if / when they receive a packet.

Remember that the connection is bandwidth constrained.  No more than two
packets can be "on the wire" at a time. If you send a third packet while
there are already two packets traveling to their destination (in either
direction), the third packet will be dropped, so it is important that you get
your timeouts and your acknowledgments right.


### Testing the implementation

You can use the provided `tester.py` script when testing your solution.  This
script uses the `receiver.py`, `sender.py`, and `server.py` scripts to
simulate an unreliable connection, and to test your solution.

The `tester.py` script contains many parameters you can use to test your
solution under different conditions, and to receive different amounts
of debugging information to better understand the network.  These
parameters and options can be viewed by calling `tester.py --help`, and are
also reproduced below.


    usage: tester.py [-h] [-p PORT] [-l LOSS] [-d DELAY] [-b BUFFER] -f FILE
                    [-r RECEIVE] [-s] [-v]

    Utility script for testing HW5 solutions under user set conditions.

    optional arguments:
    -h, --help            show this help message and exit
    -p PORT, --port PORT  The port to simulate the lossy wire on (defaults to
                            9999).
    -l LOSS, --loss LOSS  The percentage of packets to drop.
    -d DELAY, --delay DELAY
                            The number of seconds, as a float, to wait before
                            forwarding a packet on.
    -b BUFFER, --buffer BUFFER
                            The size of the buffer to simulate.
    -f FILE, --file FILE  The file to send over the wire.
    -r RECEIVE, --receive RECEIVE
                            The path to write the received file to. If not
                            provided, the results will be written to a temp file.
    -s, --summary         Print a one line summary of whether the transaction
                            was successful, instead of a more verbose description
                            of the result.
    -v, --verbose         Enable extra verbose mode.


For example, to see how your solution performs when transmitting a text file,
with a 5% loss rate, and with a latency of 100ms, you could use the following:
`python3 tester.py --file test_data.txt --loss .05 --delay 0.1`.


### Key Notes

 * A key part of this project is determining how long to wait before resending
   a packet.  You should estimate this timeout value using the EWMA technique
   for estimating the RTT, and use this in determining your timeout. With
   correctly tuned timeouts, lower RTT will result in higher throughput.

 * A good way of determining the timeout to use is the "estimated RTT +
   (deviation  of RTT * 4)".  
   
 * Use the included `--verbose` option to include very detailed information
   about what your code is sending over the network, and how the network
   is handling that data.

 * Use the included `--receive` option to see the results of your file transfer.
   By default, the testing script will store the results of your code to a
   temporary location.

 * Keep your packets smaller than or equal to `homework5.MAX_PACKET` (1400
   bytes).

 * Pay attention to the end of the connection. Ensure that both sides of the
   connection finish without user assistance, even if packet losses occur,
   while guaranteeing that the entire file is transferred. 
