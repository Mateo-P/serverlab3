import socket
import sys
from os import path, system

IP = '127.0.0.1'
PORT = 65432

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((IP, PORT))

if len(sys.argv) != 2:
    print("datos necesarios: ", sys.argv[0], "<ruta del video que se desea subir>")

    sys.exit(1)
abs_path = path.dirname(path.abspath(__file__))
files_address = path.join(abs_path, 'videos')
video_address = path.join(files_address, sys.argv[1])
with open (video_address, 'rb') as a:
    data = a.read()
    soc.sendall(data)
soc.shutdown(socket.SHUT_RDWR)
soc.close()