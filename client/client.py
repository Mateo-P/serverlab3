import hashlib
import math
import struct
import socket
import time
from os import path
import atexit

PORT = 40001
SERVER = "127.0.0.1"
ADDRESS_TUPLE = (SERVER, PORT)
BUFFER_SIZE = 1024


def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_socket.connect(ADDRESS_TUPLE)
print("SEND: CONNECTED")
connection_socket.send("CONNECTED".encode())

absolute_path = path.dirname(path.abspath(__file__))
file_name = str(connection_socket.recv(300).decode())
print("RECEIVED: " + file_name + " (file name)")
file_path = path.join(absolute_path, file_name)
print("FILE PATH: " + file_path)

file_received = False

try:
    file = open(file_path, 'wb')
    file_size = int(struct.unpack('i', connection_socket.recv(4))[0])
    print("RECEIVED: " + str(file_size) + " (file size)")
    processed_quantity = 0
    processing_percentage = 0
    last_processing_percentage = 0
    total_packages = 0

    while processed_quantity < file_size:
        data = connection_socket.recv(BUFFER_SIZE)
        processed_quantity += len(data)
        processing_percentage = roundup((processed_quantity / file_size) * 100)

        if processing_percentage != last_processing_percentage:
            print("PROCESSING: " + str(processing_percentage) + "%")

        total_packages += 1
        last_processing_percentage = processing_percentage
        file.write(data)
    file.close()

    print("TOTAL NUMBER OF PACKAGES RECEIVED: " + str(total_packages))

    print("SEND: FINISHED")
    connection_socket.send('FINISHED'.encode())

    file_received = True

except Exception as e:
    print("ERROR WHILE PROCESSING FILE: MAXIMUM SERVER CAPACITY")

if file_received:

    # verify integrity with HMAC digest from server
    integrity = connection_socket.recv(64)
    print("RECEIVED: (integrity)")

    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    file.close()

    integrity_local = hash_md5.digest()

    if integrity == integrity_local:
        print("SEND: INTEGRITY VERIFIED")
        connection_socket.send("INTEGRITY VERIFIED".encode())
    else:
        print("SEND: INTEGRITY ERROR")
        connection_socket.send("INTEGRITY ERROR".encode())

    elapsed_time = time.time()

    connection_socket.send(struct.pack('d', elapsed_time))

connection_socket.close()


@atexit.register
def at_exit_cleanup():
    print("BYE")
    connection_socket.close()
