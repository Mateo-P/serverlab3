import hashlib
import struct
import socket
import time
import threading
from os import path, listdir
from logger import create_logger, write_log, close_log
import atexit

PORT = 40001
HOST = "0.0.0.0"
ADDRESS_TUPLE = (HOST, PORT)


def run_server():
    connection_socket.listen(25)

    print(f"LISTENING ON HOST: {HOST}")

    while True:
        connection, addr = connection_socket.accept()
        connection_socket.setblocking(1)
        connection_thread = threading.Thread(target=connect, args=(connection, addr))

        threads = [connection_thread]
        connection_thread.start()

        print('CONNECTION READY', addr)
        if len(threads) == client_quantity:
            can_send = False
            while not can_send:
                ready = True
                for t in threads:
                    ready = getattr(t, 'connected', False) and ready
                can_send = ready
            for t in threads:
                t.send = can_send
            del threads[:]
    mainconn.close()


def connect(connection, addr):

    logger = create_logger(addr)
    start_time = time.time()

    try:

        received_message = connection.recv(255).decode()
        print("RECEIVED: " + received_message + "\n")
        write_log(logger, "RECEIVED: " + received_message + "\n")
        thread = threading.current_thread()

        if received_message == "CONNECTED":
            thread.connected = True
            connection_message = 'CONNECTED SUCCESFULLY TO ADDRESS {} \n'.format(addr)
            print("RECEIVED: " + connection_message + "\n")
            write_log(logger, "RECEIVED: " + connection_message + "\n")

            #while getattr(t, 'send', True):
            #    continue

            print("SEND: " + file_name + " (file name) \n")
            write_log(logger, "SEND: " + file_name + " (file name) \n")

            connection.send(file_name.encode())
            file = open(file_address, 'rb')
            print('FILE OPENED \n')
            write_log(logger, 'FILE OPENED \n')

            file_size_e = struct.pack('i', file_size)
            connection.send(file_size_e)
            print("SEND: file size encoded \n")
            write_log(logger, "SEND: file size encoded \n")

            line = file.read(1024)

            while line:
                connection.send(line)
                line = file.read(1024)

            received_message = connection.recv(255).decode()

            if received_message != "FINISHED":
                print("SERVER CAPACITY REACHED! \n")
            else:
                print('FILE SENT\n')
                write_log(logger, 'FILE SENT \n')

                print("RECEIVED: " + received_message + "\n")
                write_log(logger, "RECEIVED: " + received_message + "\n")

                print('SEND: HMAC VERIFICATION \n')
                write_log(logger, 'SEND: HMAC VERIFICATION \n')

                connection.send(hmac)

                received_message = connection.recv(255).decode()

                #the incoming message might be "INTEGRITY VERIFIED" or "INTEGRITY ERROR"
                #depending on the result of the hash digest

                print("RECEIVED: " + received_message + "\n")
                write_log(logger, "RECEIVED: " + received_message + "\n")

                stop_time = float(struct.unpack('d', connection.recv(8))[0])
                total_time = abs(start_time - stop_time)

                time_message = 'TIME ELAPSED IN SECONDS: ' + str(total_time)

                print(time_message)
                write_log(logger, time_message + " \n")
                close_log(logger)

        else:
            print('FILE NOT SENT')
            write_log(logger, 'FILE NOT SENT \n')
            close_log(logger)
        connection.close()

    except Exception as e:
        print(str(e))
        write_log(logger, 'ERROR' + str(e) + "\n")
        close_log(logger)
        connection.close()


abs_path = path.dirname(path.abspath(__file__))
files_address = path.join(abs_path, 'files')
connection_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection_socket.bind(ADDRESS_TUPLE)


@atexit.register
def at_exit_cleanup():
    print("BYE")
    connection_socket.close()


try:

    client_quantity = int(input('INGRESAR EL NUMERO MAXIMO DE CLIENTES: '))
    files = [f for f in listdir(files_address) if path.isfile(path.join(files_address, f))]

    print("ARCHIVOS DISPONIBLES PARA ENVIAR:")

    for i in range(len(files)):
        print("#" + str(i) + ": " + files[i])

    file_name = files[int(input('INGRESAR EL NUMERO DE ARCHIVO: '))]
    file_address = path.join(files_address, file_name)
    file_size = path.getsize(file_address)

    print("TAMANO DEL ARCHIVO: " + str(file_size))

    # HMAC VERIFICATION
    hash_md5 = hashlib.md5()
    with open(file_address, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)

    file.close()

    hmac = hash_md5.digest()

except Exception as e:
    connection_socket.close()
    print("ERROR AL CARGAR ARCHIVO")

run_server()
connection_socket.close()
