import socket
import io
import time
import typing
import struct
import random
from struct import *
import homework5
import homework5.logging
import binascii


def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.
    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """

    # Naive implementation where we chunk the data to be sent into
    # packets as large as the network will allow, and then send them
    # over the network, pausing half a second between sends to let the
    # network "rest" :)

    seqnum = 0
    acknum = 0
    ack = 0
    final = 0
    tcp_established = False
    timeout_time = 3
    estimated_rtt = 0
    dev_rtt = 0
    acknowledgement = pack("i", 0)
    total = 0 
    data_received = False
    next_ack = 1
    while not data_received:
        if(total == len(data)):
            sock.close()
            break
        else:
            first_packet = make_packet(seqnum, acknum, ack, final)
            sock.send(first_packet)
            logger = homework5.logging.get_logger("reliable-sender")
            chunk_size = homework5.MAX_PACKET
            pause = .1            
            offsets = range(0, len(data), homework5.MAX_PACKET)
            for chunk in [data[i:i + chunk_size] for i in offsets]:
                try:
                    send_time = time.time()
                    received_data = 0
                    while not received_data:
                        reply1 = packet_listening(sock)
                        total = total + len(chunk)
                        recv_time = time.time()
                        
                        if reply1[1] == next_ack:
                            sample_rtt = recv_time - send_time
                            estimated_rtt = estimated_rtt * 0.875 + sample_rtt * 0.125
                            dev_rtt = 0.75 * dev_rtt + 0.25 * abs(sample_rtt - estimated_rtt)
                            timeout_time = estimated_rtt + 4 * dev_rtt                           
                            sock.settimeout(timeout_time)                           
                            checksum = binascii.crc32(chunk)
                            checksum = struct.pack('L', checksum)
                            sock.send(chunk + checksum)                           
                            next_ack = next_ack + 1                            
                            break
                except socket.timeout:
                    sock.settimeout(timeout_time * 2)                    
                    checksum = binascii.crc32(chunk)
                    checksum = struct.pack('L', checksum)
                    sock.send(chunk + checksum)
                    next_ack = next_ack + 1                                    

def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.
    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
    Return:
        The number of bytes written to the destination.
    """
    
    logger = homework5.logging.get_logger("reliable-receiver")
    # Naive solution, where we continually read data off the socket
    # until we don't receive any more data, and then return.
    
    reply = packet_listening(sock)
    acknowledgement = 1
    num_bytes = 0
    reply1 = []
    reply1 = list(reply)
    total = 0
    for x in range(1):
        reply1[0] = random.randint(1,5)
    reply1[1] = reply1[1] + 1
    reply1[2] = reply1[2] + 1 
    second_packet = make_packet(reply1[0], reply1[1], reply1[2], reply1[3])
    sock.send(second_packet)
    a = 2
    while(a == 2):
               
        for x in range(1):
            reply1[0] = random.randint(1,5)
        reply1[1] = reply1[1] + 1
        reply1[2] = reply1[2] + 1        
        second_packet = make_packet(reply1[0], reply1[1], reply1[2], reply1[3])
        data1 = sock.recv(5000)
        dlen = len(data1) - 8
        data = data1[:dlen]
        checksum = struct.unpack("L", data1[dlen:])
        checkchecksum = binascii.crc32(data)
        if data and checkchecksum in checksum:
            sock.send(second_packet)     
        else:
            sock.close()
            break
        logger.info("Received %d bytes", len(data))
        dest.write(data)
        num_bytes += len(data)
        dest.flush()
    return num_bytes


def packet_listening(sock: socket.socket):
    first_received = False
    while not first_received:
        received_data = sock.recv(homework5.MAX_PACKET)
        received_packet = struct.unpack("iiii", received_data)
        if received_packet:
            break
    return received_packet
 

def make_packet(seqnum, acknum, ack, final):
    packet = struct.pack("iiii", seqnum, acknum, ack, final)
    return packet

