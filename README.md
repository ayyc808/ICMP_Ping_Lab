# ICMP Pinger - Lab 4

## DESCRIPTION
A python ICMP Ping app that sends echo requests, measures rount trip time (RTT), and reports packet loss stats

## REQUIREMENTS
-Python 3
-Admin (root) privileges for raw sockets

## TO RUN IT
**On Windows**
- Right click your VSCode then select Run as Administrator
-Run the icmp_ping.py

**On macOS**
- Run by using sudo python3 icmp_ping.py

## TESTING THE HOST
Uncomment the desired host in the code for pinging:

| Host        | Location      |
|-------------|---------------|
| 127.0.0.1   | Localhost     |
| google.com  | North America |
| bbc.co.uk   | Europe        |
| yahoo.co.jp | Asia          |
| news24.com  | Africa        |