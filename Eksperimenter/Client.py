import socket

from pycparser.c_ast import Return

host, port = "127.0.0.1", 25001
# data = "0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5"

# SOCK_STREAM means TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# try:
#     # Connect to the server and send the data
#     sock.connect((host, port))
#     sock.sendall(data.encode("utf-8"))
#     response = sock.recv(1024).decode("utf-8")
#     print (response)
#
# finally:
#     sock.close()

def connect():
    try:
        sock.connect((host, port))
    except Exception as e:
        return False
    else:
        return True


def disconnect():
    sock.close()

def send_data(data):
    try:
        sock.sendall(data.encode("utf-8"))
    except Exception as e:
        disconnect()