from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    if countTo < len(string):
        csum = csum + string[len(string) - 1]
        csum = csum & 0xffffffff
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return "Request timed out."
        
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        
        # Fill in start
        ipNetHeader = recPacket[:20]    # the first 20 bytes from packet that is received to get to ICMP header

        # Fetch the ICMP header from the IP packet
        ttlVal = recPacket[8]   # extracting TTL field (offset 8)

        icmpNetHeader = recPacket[20:28]    # this header byte 20-28 has the ICMP header
        icmpUnpacked = struct.unpack("bbHHh", icmpNetHeader) # b: ICMP, b: Code, H: checksum, H: packet ID, h: sequence
        packetNo = icmpUnpacked[3]  # getting packet ID at index 3
        sequence = icmpUnpacked[4]  # and then index 4 for the sequence #

        if packetNo == ID:
            # calculating the data payload data size
            dataSize = len(recPacket) - 28      # total packet - 28 bytes header
            sendTime = struct.unpack("d", recPacket[28:36])[0]
            rttRespTime = (timeReceived - sendTime) * 1000  # calculating round trip in ms

            # Formatting and returning string for reply
            result = f"Packets received from {destAddr}:\nbytes={dataSize} time={rttRespTime:.2f}ms TTL={ttlVal} Sequence={sequence}"
            return result
    
        # Fill in end
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
        
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF # Return the current process ID
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay

def ping(host, timeout=1):
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    while 1:
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1) # one second
    return delay

# To ping the desired host, uncomment one, then run sudo python3 icmp_ping.py to get result
# ping("127.0.0.1")         # To localhost
# ping("google.com")        # Ping from North America
# ping("bbc.co.uk")         # Ping from Europe
# ping("yahoo.co.jp")       # Ping from Asia
# ping("news24.com")        # Ping from Africa