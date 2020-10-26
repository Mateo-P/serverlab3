#!/usr/bin/env python
from socket import *
import sys
import struct

def main():
  MCAST_GRP = '224.1.1.1'
  MCAST_PORT = 5007
  buf =1024
  file_name=sys.argv[1]
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
  sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
  sock.sendto(file_name, (MCAST_GRP, MCAST_PORT))
  f=open(file_name,"rb")
  data = f.read(buf)
  while (data):
    if(sock.sendto(data,(MCAST_GRP, MCAST_PORT))):
        print ("sending ...")
        data = f.read(buf)
  sock.close()
  f.close()

if __name__ == '__main__':
  main()


