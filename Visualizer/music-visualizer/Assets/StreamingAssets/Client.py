import socket

host, port = "127.0.0.1", 25001

# SOCK_STREAM means TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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